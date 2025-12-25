"""
L9 Core Agents - Agent Instance
===============================

Represents a running agent instance with its configuration and bound tools.

The AgentInstance class manages:
- Agent configuration and state
- Tool bindings (approved by governance)
- Context assembly for AIOS calls
- Conversation history within a task

This class does NOT:
- Execute reasoning (that's AIOS runtime)
- Execute tools (that's tool registry)
- Define agent personalities (that's loaded from registry)

L Memory Usage Rules
====================

For agent L (agent_id="L"), the following memory usage rules apply:

1. governance_meta:
   - Use memory_search(governance_meta, ...) to look up rules, authority, policies
   - Use memory_write(governance_meta, ...) to record new governance rules (rare)
   - Example: "What are the approval requirements for GMP runs?"

2. project_history:
   - Use memory_search(project_history, ...) before executing long plans
   - Use memory_write(project_history, ...) after major decisions or milestones
   - Example: "What architecture decisions were made for the tool system?"

3. tool_audit:
   - Automatically populated by tool call logging (ToolGraph.log_tool_call)
   - Use memory_search(tool_audit, ...) to review past actions
   - Example: "What tools did I call in the last session?"

4. session_context:
   - Use memory_write(session_context, ...) to store current session state
   - Use memory_search(session_context, ...) to retrieve session context
   - Example: "What was I working on in this session?"

Tool Call Logging:
- All tool calls (internal, MCP, Mac Agent, GMP) must call ToolGraph.log_tool_call
- This automatically populates tool_audit segment
- Use tool_call_wrapper() helper to ensure consistent logging

Version: 1.0.0
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from core.agents.schemas import (
    AgentConfig,
    AgentTask,
    ExecutorState,
    ToolBinding,
)

logger = logging.getLogger(__name__)


class AgentInstance:
    """
    Represents a running agent instance.
    
    Manages the agent's configuration, state, and context during task execution.
    This class is instantiated by the AgentExecutorService for each task.
    
    Attributes:
        instance_id: Unique instance identifier
        config: Agent configuration
        task: The task being executed
        state: Current executor state
        iteration: Current iteration in execution loop
        history: Message history for this task
        tool_results: Results from tool calls
        created_at: Instance creation timestamp
    """
    
    def __init__(
        self,
        config: AgentConfig,
        task: AgentTask,
    ):
        """
        Initialize a new agent instance.
        
        Args:
            config: Agent configuration with personality and tools
            task: The task to execute
        """
        self._instance_id = uuid4()
        self._config = config
        self._task = task
        self._state = ExecutorState.INITIALIZING
        self._iteration = 0
        self._history: list[dict[str, Any]] = []
        self._tool_results: list[dict[str, Any]] = []
        self._created_at = datetime.utcnow()
        self._total_tokens = 0
        
        logger.info(
            "AgentInstance created",
            extra={
                "instance_id": str(self._instance_id),
                "agent_id": config.agent_id,
                "task_id": str(task.id),
            }
        )
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def instance_id(self) -> UUID:
        """Get instance ID."""
        return self._instance_id
    
    @property
    def config(self) -> AgentConfig:
        """Get agent configuration."""
        return self._config
    
    @property
    def task(self) -> AgentTask:
        """Get the task being executed."""
        return self._task
    
    @property
    def state(self) -> ExecutorState:
        """Get current executor state."""
        return self._state
    
    @property
    def iteration(self) -> int:
        """Get current iteration number."""
        return self._iteration
    
    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        return self._total_tokens
    
    @property
    def thread_id(self) -> UUID:
        """Get the thread ID for this task."""
        return self._task.get_thread_id()
    
    # =========================================================================
    # State Management
    # =========================================================================
    
    def transition_to(self, new_state: ExecutorState) -> None:
        """
        Transition to a new state.
        
        Args:
            new_state: Target state
        """
        old_state = self._state
        self._state = new_state
        
        logger.debug(
            f"State transition: {old_state.value} -> {new_state.value}",
            extra={
                "instance_id": str(self._instance_id),
                "task_id": str(self._task.id),
            }
        )
    
    def increment_iteration(self) -> int:
        """
        Increment iteration counter.
        
        Returns:
            New iteration number
        """
        self._iteration += 1
        return self._iteration
    
    def add_tokens(self, tokens: int) -> None:
        """Add to total token count."""
        self._total_tokens += tokens
    
    # =========================================================================
    # Tool Management
    # =========================================================================
    
    def get_bound_tools(self) -> list[ToolBinding]:
        """
        Get list of tools bound to this agent.
        
        Returns:
            List of enabled tool bindings
        """
        return [t for t in self._config.tools if t.enabled]
    
    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """
        Get tool definitions in OpenAI function calling format.
        
        function.name == tool_id (canonical identity, must match exactly).
        
        Returns:
            List of tool definitions for AIOS
        """
        definitions = []
        for tool in self.get_bound_tools():
            definitions.append({
                "type": "function",
                "function": {
                    "name": tool.tool_id,  # Canonical identity
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                }
            })
        return definitions
    
    def has_tool(self, tool_id: str) -> bool:
        """Check if a tool is bound to this agent."""
        return any(t.tool_id == tool_id and t.enabled for t in self._config.tools)
    
    # =========================================================================
    # History Management
    # =========================================================================
    
    def add_user_message(self, content: str, metadata: Optional[dict[str, Any]] = None) -> None:
        """
        Add a user message to history.
        
        Args:
            content: Message content
            metadata: Optional metadata
        """
        self._history.append({
            "role": "user",
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def add_assistant_message(self, content: str, metadata: Optional[dict[str, Any]] = None) -> None:
        """
        Add an assistant message to history.
        
        Args:
            content: Message content
            metadata: Optional metadata
        """
        self._history.append({
            "role": "assistant",
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def add_tool_result(
        self,
        tool_id: str,
        call_id: str,
        result: Any,
        success: bool = True,
    ) -> None:
        """
        Add a tool result to history.
        
        Uses tool_id as canonical identity for result tracking.
        
        Args:
            tool_id: Canonical tool identity
            call_id: Call identifier
            result: Tool result
            success: Whether call succeeded
        """
        self._tool_results.append({
            "tool_id": tool_id,
            "call_id": call_id,
            "result": result,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Also add to history for context (tool_id tagged for re-entry)
        self._history.append({
            "role": "tool",
            "tool_call_id": call_id,
            "content": str(result) if success else f"Error: {result}",
            "metadata": {"tool_id": tool_id, "success": success},
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def get_history(self) -> list[dict[str, Any]]:
        """Get message history."""
        return self._history.copy()
    
    def get_messages_for_aios(self) -> list[dict[str, str]]:
        """
        Get messages formatted for AIOS call.
        
        Returns:
            List of message dicts with role and content
        """
        messages = []
        for msg in self._history:
            if msg["role"] == "tool":
                # Format tool results for AIOS
                messages.append({
                    "role": "tool",
                    "tool_call_id": msg.get("tool_call_id", ""),
                    "content": msg["content"],
                })
            else:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })
        return messages
    
    # =========================================================================
    # Context Assembly
    # =========================================================================
    
    def assemble_context(self) -> dict[str, Any]:
        """
        Assemble full context bundle for AIOS call.
        
        Returns:
            Context dict containing:
            - system_prompt: System prompt for the agent
            - messages: Conversation history
            - tools: Available tool definitions
            - task: Current task information
            - metadata: Additional context
        """
        return {
            "system_prompt": self._config.system_prompt,
            "messages": self.get_messages_for_aios(),
            "tools": self.get_tool_definitions(),
            "task": {
                "id": str(self._task.id),
                "kind": self._task.kind.value,
                "payload": self._task.payload,
                "context": self._task.context,
            },
            "metadata": {
                "agent_id": self._config.agent_id,
                "personality_id": self._config.personality_id,
                "model": self._config.model,
                "temperature": self._config.temperature,
                "max_tokens": self._config.max_tokens,
                "iteration": self._iteration,
                "thread_id": str(self.thread_id),
            },
        }
    
    # =========================================================================
    # Serialization
    # =========================================================================
    
    def to_trace_dict(self) -> dict[str, Any]:
        """
        Serialize instance state for trace logging.
        
        Returns:
            Dict suitable for packet storage
        """
        return {
            "instance_id": str(self._instance_id),
            "agent_id": self._config.agent_id,
            "task_id": str(self._task.id),
            "thread_id": str(self.thread_id),
            "state": self._state.value,
            "iteration": self._iteration,
            "total_tokens": self._total_tokens,
            "history_length": len(self._history),
            "tool_calls": len(self._tool_results),
            "created_at": self._created_at.isoformat(),
        }


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "AgentInstance",
]

