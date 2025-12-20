"""
L9 Core Agents - Agent Executor Service
========================================

The Agent Executor is the heart of the agentic system, orchestrating agent
instantiation, tool binding, and the execution loop.

Key responsibilities:
- Instantiate agents based on registered configurations
- Bind governance-approved tools to agent instances
- Run the execution loop (reasoning <-> tool_use state machine)
- Dispatch tool calls through the tool registry
- Store reasoning traces and results via memory substrate

This module does NOT:
- Define agent personalities or core reasoning (AIOS does that)
- Approve or deny tool usage (Governance Engine does that)
- Create new database tables

Version: 1.0.0
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Callable, Optional, Protocol
from uuid import UUID

from core.agents.schemas import (
    AgentTask,
    AgentConfig,
    AIOSResult,
    AIOSResultType,
    ExecutorState,
    ExecutionResult,
    DuplicateTaskResponse,
    ToolCallRequest,
    ToolCallResult,
    ToolBinding,
)
from core.agents.agent_instance import AgentInstance
from memory.substrate_models import PacketEnvelopeIn, PacketMetadata

logger = logging.getLogger(__name__)


# =============================================================================
# Protocol Definitions (Interfaces)
# =============================================================================

class AIOSRuntime(Protocol):
    """Protocol for AIOS runtime interface."""
    
    async def execute_reasoning(
        self,
        context: dict[str, Any],
    ) -> AIOSResult:
        """
        Execute reasoning with the given context.
        
        Args:
            context: Context bundle from AgentInstance.assemble_context()
            
        Returns:
            AIOSResult with response or tool call
        """
        ...


class ToolRegistryProtocol(Protocol):
    """Protocol for tool registry interface."""
    
    async def dispatch_tool_call(
        self,
        tool_id: str,
        arguments: dict[str, Any],
        context: dict[str, Any],
    ) -> ToolCallResult:
        """
        Dispatch a tool call.
        
        Args:
            tool_id: Canonical tool identity
            arguments: Arguments for tool
            context: Execution context
            
        Returns:
            ToolCallResult with result or error (includes tool_id)
        """
        ...
    
    def get_approved_tools(
        self,
        agent_id: str,
        principal_id: str,
    ) -> list[ToolBinding]:
        """
        Get list of tools approved for an agent.
        
        Args:
            agent_id: Agent identifier
            principal_id: Principal requesting tools
            
        Returns:
            List of approved tool bindings
        """
        ...


class SubstrateServiceProtocol(Protocol):
    """Protocol for memory substrate service interface."""
    
    async def write_packet(
        self,
        packet_in: PacketEnvelopeIn,
    ) -> Any:
        """
        Write a packet to the substrate.
        
        Args:
            packet_in: Packet envelope to write
            
        Returns:
            Write result
        """
        ...
    
    async def search_packets(
        self,
        thread_id: UUID,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Search packets by thread ID.
        
        Args:
            thread_id: Thread identifier
            limit: Max results
            
        Returns:
            List of matching packets
        """
        ...


class AgentRegistryProtocol(Protocol):
    """Protocol for agent registry interface."""
    
    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """
        Get configuration for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            AgentConfig or None if not found
        """
        ...
    
    def agent_exists(self, agent_id: str) -> bool:
        """Check if an agent is registered."""
        ...


# =============================================================================
# Agent Executor Service
# =============================================================================

class AgentExecutorService:
    """
    Service for executing agent tasks.
    
    Orchestrates the agent execution loop:
    1. Validate and instantiate agent
    2. Bind approved tools
    3. Run reasoning loop until completion or max iterations
    4. Store traces and results
    
    All dependencies are injected - no singletons.
    """
    
    def __init__(
        self,
        aios_runtime: AIOSRuntime,
        tool_registry: ToolRegistryProtocol,
        substrate_service: SubstrateServiceProtocol,
        agent_registry: AgentRegistryProtocol,
        default_agent_id: Optional[str] = None,
        max_iterations: Optional[int] = None,
    ):
        """
        Initialize the executor service.
        
        Args:
            aios_runtime: AIOS runtime for reasoning
            tool_registry: Tool registry for dispatching
            substrate_service: Memory substrate for persistence
            agent_registry: Agent registry for configs
            default_agent_id: Default agent ID (from env if not provided)
            max_iterations: Max iterations (from env if not provided)
        """
        self._aios_runtime = aios_runtime
        self._tool_registry = tool_registry
        self._substrate_service = substrate_service
        self._agent_registry = agent_registry
        
        # Configuration from env vars (read at init, not import time)
        self._default_agent_id = default_agent_id or os.getenv(
            "DEFAULT_AGENT_ID", "l9-standard-v1"
        )
        self._max_iterations = max_iterations or int(
            os.getenv("AGENT_MAX_ITERATIONS", "10")
        )
        
        # Idempotency cache
        # LIMITATION: In-memory only - cleared on process restart.
        # NOT durable: If executor restarts, duplicate tasks will re-execute.
        # For substrate-backed idempotency, see roadmap v1.2.
        self._processed_tasks: dict[str, ExecutionResult] = {}
        
        logger.info(
            "agent.executor.init: default_agent_id=%s, max_iterations=%d",
            self._default_agent_id,
            self._max_iterations,
        )
    
    # =========================================================================
    # Public API
    # =========================================================================
    
    async def start_agent_task(
        self,
        task: AgentTask,
    ) -> ExecutionResult | DuplicateTaskResponse:
        """
        Start executing an agent task.
        
        This is the main entry point for task execution.
        
        Args:
            task: The task to execute
            
        Returns:
            ExecutionResult or DuplicateTaskResponse if duplicate
        """
        start_time = datetime.utcnow()
        task_id_str = str(task.id)
        
        # Log start
        logger.info(
            "agent.executor.start: task_id=%s, agent_id=%s, thread_id=%s",
            task_id_str,
            task.agent_id,
            str(task.get_thread_id()),
        )
        
        # Idempotency check
        dedupe_key = task.get_dedupe_key()
        if dedupe_key in self._processed_tasks:
            logger.info("agent.executor.duplicate: task_id=%s", task_id_str)
            return DuplicateTaskResponse(task_id=task.id)
        
        try:
            # Validate task
            validation_error = self._validate_task(task)
            if validation_error:
                return await self._handle_error(
                    task,
                    validation_error,
                    start_time,
                    "validation_failed",
                )
            
            # Instantiate agent
            instance = await self._instantiate_agent(task)
            if instance is None:
                return await self._handle_error(
                    task,
                    f"Agent not found: {task.agent_id}",
                    start_time,
                    "agent_not_found",
                )
            
            # Emit start packet
            await self._emit_packet(
                packet_type="agent.executor.trace",
                payload={
                    "event": "start",
                    "task_id": task_id_str,
                    "agent_id": task.agent_id,
                    "iteration": 0,
                },
                thread_id=task.get_thread_id(),
            )
            
            # Run execution loop
            result = await self._run_execution_loop(instance)
            
            # Cache result for idempotency
            self._processed_tasks[dedupe_key] = result
            
            # Emit result packet
            await self._emit_packet(
                packet_type="agent.executor.result",
                payload={
                    "task_id": task_id_str,
                    "status": result.status,
                    "iterations": result.iterations,
                    "duration_ms": result.duration_ms,
                    "error": result.error,
                },
                thread_id=task.get_thread_id(),
            )
            
            # Log completion
            log_level = "info" if result.status == "completed" else "error"
            event_name = "success" if result.status == "completed" else "error"
            getattr(logger, log_level)(
                "agent.executor.finish.%s: task_id=%s, total_iterations=%d, duration_ms=%d, error=%s",
                event_name,
                task_id_str,
                result.iterations,
                result.duration_ms,
                result.error,
            )
            
            return result
            
        except Exception as e:
            logger.exception(
                "agent.executor.finish.error: task_id=%s, error=%s",
                task_id_str,
                str(e),
            )
            return await self._handle_error(
                task,
                str(e),
                start_time,
                "execution_error",
            )
    
    # =========================================================================
    # Validation
    # =========================================================================
    
    def _validate_task(self, task: AgentTask) -> Optional[str]:
        """
        Validate an incoming task. Does NOT mutate the task object.
        
        Args:
            task: Task to validate (read-only)
            
        Returns:
            Error message or None if valid
        """
        # Check task has valid ID and kind
        if not task.id:
            return "Task ID is required"
        
        if not task.kind:
            return "Task kind is required"
        
        # Check agent ID - reject if missing (no silent patching)
        if not task.agent_id:
            return f"agent_id is required (hint: use default '{self._default_agent_id}')"
        
        # Verify agent exists
        if not self._agent_registry.agent_exists(task.agent_id):
            return f"Agent not registered: {task.agent_id}"
        
        return None
    
    # =========================================================================
    # Agent Instantiation
    # =========================================================================
    
    async def _instantiate_agent(self, task: AgentTask) -> Optional[AgentInstance]:
        """
        Instantiate an agent for the given task.
        
        Args:
            task: Task to execute
            
        Returns:
            AgentInstance or None if agent not found
        """
        # Get agent config from registry
        config = self._agent_registry.get_agent_config(task.agent_id)
        if config is None:
            logger.error("agent_id_not_found: agent_id=%s", task.agent_id)
            return None
        
        # Bind governance-approved tools
        approved_tools = self._tool_registry.get_approved_tools(
            agent_id=task.agent_id,
            principal_id=task.source_id,
        )
        
        # Update config with approved tools
        config.tools = approved_tools
        
        # Create instance
        instance = AgentInstance(config=config, task=task)
        
        # Load context from previous thread if exists
        await self._hydrate_context(instance)
        
        return instance
    
    async def _hydrate_context(self, instance: AgentInstance) -> None:
        """
        Hydrate agent context from thread history.
        
        NOTE: Currently shallow implementation - searches for packets but does not
        reconstruct conversation history. This is intentional for v1.0 to keep
        execution deterministic. Full context hydration deferred to v1.1.
        
        Behavior:
        - Searches substrate for previous thread packets
        - Logs if search fails (does not block execution)
        - Does NOT add messages to instance history (shallow)
        
        Args:
            instance: Agent instance to hydrate
        """
        try:
            # Search for previous packets in this thread (shallow - for observability only)
            history = await self._substrate_service.search_packets(
                thread_id=instance.thread_id,
                limit=50,
            )
            
            # NOTE: Intentionally not adding history to instance.
            # Full context reconstruction deferred to v1.1.
            # This ensures each task execution is deterministic.
            if history:
                logger.debug(
                    "agent.executor.hydrate: thread_id=%s, found_packets=%d (not applied)",
                    str(instance.thread_id),
                    len(history),
                )
                    
        except Exception as e:
            # Hydration failure does not block execution
            logger.warning(
                "agent.executor.hydrate_failed: thread_id=%s, error=%s",
                str(instance.thread_id),
                str(e),
            )
    
    # =========================================================================
    # Execution Loop
    # =========================================================================
    
    async def _run_execution_loop(
        self,
        instance: AgentInstance,
    ) -> ExecutionResult:
        """
        Run the main execution loop.
        
        State machine transitions:
        INITIALIZING -> REASONING -> TOOL_USE -> REASONING -> ... -> COMPLETED
        
        Args:
            instance: Agent instance to run
            
        Returns:
            ExecutionResult
        """
        start_time = datetime.utcnow()
        max_iterations = min(
            instance.task.max_iterations,
            self._max_iterations,
        )
        
        # Initialize with task payload as first message
        if instance.task.payload.get("message"):
            instance.add_user_message(instance.task.payload["message"])
        elif instance.task.payload.get("query"):
            instance.add_user_message(instance.task.payload["query"])
        elif instance.task.payload.get("content"):
            instance.add_user_message(instance.task.payload["content"])
        
        # Transition to reasoning
        instance.transition_to(ExecutorState.REASONING)
        
        final_result: Optional[str] = None
        error: Optional[str] = None
        
        while instance.iteration < max_iterations:
            iteration = instance.increment_iteration()
            
            # Log iteration
            logger.debug(
                "agent.executor.loop.iteration: task_id=%s, iteration=%d, action_type=%s",
                str(instance.task.id),
                iteration,
                instance.state.value,
            )
            
            # Emit trace packet
            await self._emit_packet(
                packet_type="agent.executor.trace",
                payload={
                    "event": "iteration",
                    "task_id": str(instance.task.id),
                    "iteration": iteration,
                    "state": instance.state.value,
                },
                thread_id=instance.thread_id,
            )
            
            # Call AIOS
            context = instance.assemble_context()
            aios_result = await self._aios_runtime.execute_reasoning(context)
            instance.add_tokens(aios_result.tokens_used)
            
            # Handle result based on type
            if aios_result.result_type == AIOSResultType.RESPONSE:
                # Final answer - done!
                final_result = aios_result.content
                instance.add_assistant_message(final_result or "")
                instance.transition_to(ExecutorState.COMPLETED)
                break
                
            elif aios_result.result_type == AIOSResultType.TOOL_CALL:
                # Need to call a tool
                instance.transition_to(ExecutorState.TOOL_USE)
                
                tool_call = aios_result.tool_call
                if tool_call is None:
                    error = "AIOS returned tool_call type but no tool_call data"
                    instance.transition_to(ExecutorState.FAILED)
                    break
                
                # Dispatch tool call using tool_id
                tool_result = await self._dispatch_tool_call(instance, tool_call)
                
                # Add result to history using tool_id (canonical identity)
                instance.add_tool_result(
                    tool_id=tool_call.tool_id,
                    call_id=str(tool_call.call_id),
                    result=tool_result.result if tool_result.success else tool_result.error,
                    success=tool_result.success,
                )
                
                # Continue reasoning
                instance.transition_to(ExecutorState.REASONING)
                
            elif aios_result.result_type == AIOSResultType.ERROR:
                # AIOS error
                error = aios_result.error or "Unknown AIOS error"
                logger.error(
                    "agent_aios_call_failed: task_id=%s, error=%s",
                    str(instance.task.id),
                    error,
                )
                instance.transition_to(ExecutorState.FAILED)
                break
        
        # Check if we exceeded max iterations
        if instance.iteration >= max_iterations and instance.state == ExecutorState.REASONING:
            logger.warning(
                "agent_max_iterations_exceeded: task_id=%s, max_iterations=%d",
                str(instance.task.id),
                max_iterations,
            )
            instance.transition_to(ExecutorState.TERMINATED)
            error = f"Max iterations exceeded ({max_iterations})"
        
        # Calculate duration
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Determine final status
        if instance.state == ExecutorState.COMPLETED:
            status = "completed"
        elif instance.state == ExecutorState.TERMINATED:
            status = "terminated"
        else:
            status = "failed"
        
        return ExecutionResult(
            task_id=instance.task.id,
            status=status,
            result=final_result,
            iterations=instance.iteration,
            duration_ms=duration_ms,
            error=error,
            trace_id=instance.instance_id,
        )
    
    # =========================================================================
    # Tool Dispatch
    # =========================================================================
    
    async def _dispatch_tool_call(
        self,
        instance: AgentInstance,
        tool_call: ToolCallRequest,
    ) -> ToolCallResult:
        """
        Dispatch a tool call through the registry.
        
        Uses tool_id as the sole identity for binding verification and dispatch.
        
        Args:
            instance: Agent instance
            tool_call: Tool call to dispatch (contains tool_id)
            
        Returns:
            ToolCallResult (includes tool_id for context re-entry)
        """
        # Log dispatch with tool_id (canonical identity)
        logger.info(
            "agent.executor.tool_call.dispatch: task_id=%s, tool_id=%s, arguments=%s",
            str(instance.task.id),
            tool_call.tool_id,
            tool_call.arguments,
        )
        
        # Emit packet with tool_id
        await self._emit_packet(
            packet_type="agent.executor.tool_call",
            payload={
                "event": "dispatch",
                "task_id": str(instance.task.id),
                "call_id": str(tool_call.call_id),
                "tool_id": tool_call.tool_id,
                "arguments": tool_call.arguments,
            },
            thread_id=instance.thread_id,
        )
        
        # Verify tool is bound using tool_id
        if not instance.has_tool(tool_call.tool_id):
            logger.error(
                "tool_binding_failed: task_id=%s, tool_id=%s",
                str(instance.task.id),
                tool_call.tool_id,
            )
            return ToolCallResult(
                call_id=tool_call.call_id,
                tool_id=tool_call.tool_id,
                success=False,
                error=f"Tool not bound to agent: {tool_call.tool_id}",
            )
        
        # Dispatch through registry using tool_id
        try:
            result = await self._tool_registry.dispatch_tool_call(
                tool_id=tool_call.tool_id,
                arguments=tool_call.arguments,
                context={
                    "task_id": str(instance.task.id),
                    "agent_id": instance.config.agent_id,
                    "thread_id": str(instance.thread_id),
                    "iteration": instance.iteration,
                },
            )
            return result
            
        except Exception as e:
            logger.exception(
                "tool_dispatch_error: task_id=%s, tool_id=%s, error=%s",
                str(instance.task.id),
                tool_call.tool_id,
                str(e),
            )
            return ToolCallResult(
                call_id=tool_call.call_id,
                tool_id=tool_call.tool_id,
                success=False,
                error=str(e),
            )
    
    # =========================================================================
    # Packet Emission (best-effort, non-blocking)
    # =========================================================================
    
    async def _emit_packet(
        self,
        packet_type: str,
        payload: dict[str, Any],
        thread_id: UUID,
    ) -> None:
        """
        Emit a packet to the memory substrate.
        
        BEHAVIOR: Best-effort, non-blocking.
        - Packet write failures are logged but do NOT stop execution.
        - This is intentional: execution must complete even if observability fails.
        - Critical failures (e.g., substrate down) are logged at WARNING level.
        
        REQUIRED FIELDS (all packets include):
        - packet_type: Discriminator for packet routing
        - payload: Contains task_id and event-specific data
        - thread_id: Thread identity for grouping
        - metadata.agent: "agent.executor"
        - metadata.schema_version: "1.0.0"
        
        Args:
            packet_type: Type of packet (e.g., "agent.executor.trace")
            payload: Packet payload (must contain task_id)
            thread_id: Thread identifier
        """
        try:
            packet = PacketEnvelopeIn(
                packet_type=packet_type,
                payload=payload,
                thread_id=thread_id,
                metadata=PacketMetadata(
                    agent="agent.executor",
                    schema_version="1.0.0",
                ),
            )
            await self._substrate_service.write_packet(packet)
            
        except Exception as e:
            # Best-effort: log but don't fail execution
            logger.warning(
                "agent.executor.packet_write_failed: packet_type=%s, thread_id=%s, error=%s",
                packet_type,
                str(thread_id),
                str(e),
            )
    
    # =========================================================================
    # Error Handling
    # =========================================================================
    
    async def _handle_error(
        self,
        task: AgentTask,
        error: str,
        start_time: datetime,
        error_type: str,
    ) -> ExecutionResult:
        """
        Handle an error during execution.
        
        Args:
            task: Failed task
            error: Error message
            start_time: When execution started
            error_type: Type of error for logging
            
        Returns:
            ExecutionResult with error
        """
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Emit error packet
        await self._emit_packet(
            packet_type="agent.executor.result",
            payload={
                "task_id": str(task.id),
                "status": "failed",
                "error": error,
                "error_type": error_type,
            },
            thread_id=task.get_thread_id(),
        )
        
        return ExecutionResult(
            task_id=task.id,
            status="failed",
            error=error,
            duration_ms=duration_ms,
        )


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "AgentExecutorService",
    "AIOSRuntime",
    "ToolRegistryProtocol",
    "SubstrateServiceProtocol",
    "AgentRegistryProtocol",
]

