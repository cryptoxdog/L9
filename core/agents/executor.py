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

import json
import os
import structlog
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol
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
from core.governance.approvals import ApprovalManager
from core.tools.tool_graph import ToolGraph
from core.worldmodel.insight_emitter import get_insight_emitter
from runtime.dora import emit_executor_trace

logger = structlog.get_logger(__name__)


# =============================================================================
# Reactive Task Generation
# =============================================================================


async def _generate_tasks_from_query(query: str) -> List[Dict[str, Any]]:
    """
    Parse user requests into task specifications.

    Analyzes query text, extracts intent, and generates task specs.

    Args:
        query: User query text

    Returns:
        List of task spec dicts with: name, payload, handler, priority
    """
    if not query or not query.strip():
        return []

    query_lower = query.lower().strip()
    task_specs = []

    # Simple intent detection (can be enhanced with LLM in future)
    if "gmp" in query_lower or "governance" in query_lower:
        # GMP task
        task_specs.append(
            {
                "name": f"GMP Run: {query[:50]}",
                "payload": {
                    "type": "gmp_run",
                    "query": query,
                    "status": "pending_igor_approval",
                },
                "handler": "gmp_worker",
                "priority": 5,
            }
        )
    elif "git" in query_lower or "commit" in query_lower:
        # Git commit task
        task_specs.append(
            {
                "name": f"Git Commit: {query[:50]}",
                "payload": {
                    "type": "git_commit",
                    "query": query,
                    "status": "pending_igor_approval",
                },
                "handler": "git_worker",
                "priority": 5,
            }
        )
    elif "plan" in query_lower or "long" in query_lower:
        # Long plan task
        task_specs.append(
            {
                "name": f"Long Plan: {query[:50]}",
                "payload": {
                    "type": "long_plan",
                    "goal": query,
                    "status": "pending",
                },
                "handler": "long_plan_worker",
                "priority": 5,
            }
        )
    else:
        # Default: general agent task
        task_specs.append(
            {
                "name": f"Agent Task: {query[:50]}",
                "payload": {
                    "type": "agent_task",
                    "query": query,
                    "status": "pending",
                },
                "handler": "agent_executor",
                "priority": 5,
            }
        )

    logger.info(f"Generated {len(task_specs)} task(s) from query: {query[:100]}")
    return task_specs


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

            # Emit start packet (with agent_id in payload for metadata extraction)
            await self._emit_packet(
                packet_type="agent.executor.trace",
                payload={
                    "event": "start",
                    "task_id": task_id_str,
                    "agent_id": task.agent_id,  # Used to set metadata.agent
                    "iteration": 0,
                },
                thread_id=task.get_thread_id(),
            )

            # Run execution loop
            result = await self._run_execution_loop(instance)

            # Cache result for idempotency
            self._processed_tasks[dedupe_key] = result

            # Emit result packet (with agent_id in payload for metadata extraction)
            await self._emit_packet(
                packet_type="agent.executor.result",
                payload={
                    "task_id": task_id_str,
                    "agent_id": task.agent_id,  # Used to set metadata.agent
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

            # Emit DORA trace block (auto-updates on every execution)
            await emit_executor_trace(
                task_id=task_id_str,
                task_name=getattr(task, "name", None) or f"task_{task.kind.value}",
                agent_id=task.agent_id,
                inputs={"query": task.payload.get("query", "") if task.payload else ""},
                outputs={
                    "status": result.status,
                    "iterations": result.iterations,
                    "result": str(result.result)[:500] if result.result else None,
                },
                duration_ms=result.duration_ms,
                errors=[result.error] if result.error else None,
                patterns=["agent_execution", "reasoning_loop"],
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

    async def _bind_memory_context(self, task_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Load and inject memory state into executor.

        Retrieves task context from memory substrate (Postgres/Redis) and
        returns context dict for use in task execution.

        Args:
            task_id: Task identifier
            agent_id: Agent identifier

        Returns:
            Context dict with memory state (governance rules, project history, etc.)
        """
        context = {}

        try:
            # Try to get task context from Redis cache first
            from runtime.redis_client import get_redis_client

            redis_client = get_redis_client()
            if redis_client and redis_client.is_available():
                cached_context = await redis_client.get_task_context(task_id)
                if cached_context:
                    context.update(cached_context)
                    logger.debug(f"Loaded task context from Redis cache: {task_id}")

            # Load from memory substrate (Postgres)
            if self._substrate_service:
                # Search for task-related packets
                packets = await self._substrate_service.search_packets_by_thread(
                    thread_id=task_id,
                    packet_type="task_execution",
                    limit=10,
                )

                if packets:
                    # Extract context from recent packets
                    for packet in packets[-5:]:  # Last 5 packets
                        payload = packet.get("payload", {})
                        if payload:
                            context.setdefault("history", []).append(payload)

                    logger.debug(
                        f"Loaded {len(packets)} packets for task context: {task_id}"
                    )

            # Load governance rules and project history via memory_helpers
            try:
                from runtime.memory_helpers import (
                    memory_search,
                    MEMORY_SEGMENT_GOVERNANCE_META,
                    MEMORY_SEGMENT_PROJECT_HISTORY,
                )

                governance_rules = await memory_search(
                    segment=MEMORY_SEGMENT_GOVERNANCE_META,
                    query=f"task {task_id}",
                    agent_id=agent_id,
                    top_k=5,
                )
                if governance_rules:
                    context["governance_rules"] = governance_rules

                project_history = await memory_search(
                    segment=MEMORY_SEGMENT_PROJECT_HISTORY,
                    query=f"task {task_id}",
                    agent_id=agent_id,
                    top_k=5,
                )
                if project_history:
                    context["project_history"] = project_history
            except Exception as e:
                logger.warning(
                    f"Failed to load memory segments for task {task_id}: {e}"
                )

        except Exception as e:
            logger.warning(f"Failed to bind memory context for task {task_id}: {e}")

        return context

    async def _persist_task_result(self, task_id: str, result: dict) -> bool:
        """
        Write execution results to Postgres via memory substrate.

        Persists task execution results to memory substrate for later retrieval.

        Args:
            task_id: Task identifier
            result: Execution result dict with status, iterations, duration_ms, error, etc.

        Returns:
            True if persisted successfully, False otherwise
        """
        if not self._substrate_service:
            logger.warning(
                "Memory substrate service not available - cannot persist task result"
            )
            return False

        try:
            from memory.substrate_models import PacketEnvelopeIn

            # Write task result packet
            packet = PacketEnvelopeIn(
                packet_type="task_execution_result",
                agent_id=result.get("agent_id", "L"),
                payload={
                    "task_id": task_id,
                    "status": result.get("status", "unknown"),
                    "iterations": result.get("iterations", 0),
                    "duration_ms": result.get("duration_ms", 0),
                    "error": result.get("error"),
                    "completed_at": result.get("completed_at"),
                },
            )

            write_result = await self._substrate_service.write_packet(packet)

            if write_result.success:
                logger.info(f"Persisted task result to memory substrate: {task_id}")

                # Also cache in Redis for fast retrieval
                try:
                    from runtime.redis_client import get_redis_client

                    redis_client = get_redis_client()
                    if redis_client and redis_client.is_available():
                        await redis_client.set_task_context(
                            task_id, result, ttl=3600
                        )  # 1 hour TTL
                except Exception as e:
                    logger.warning(f"Failed to cache task result in Redis: {e}")

                return True
            else:
                logger.warning(f"Failed to persist task result: {task_id}")
                return False

        except Exception as e:
            logger.error(f"Error persisting task result {task_id}: {e}", exc_info=True)
            return False

    async def _reactive_dispatch_loop(self) -> None:
        """
        Continuously process user messages and execute generated tasks.

        Reactive dispatch loop that polls for user messages, generates tasks,
        and dispatches them immediately with approval gate enforcement.
        """
        import asyncio
        from runtime.task_queue import dispatch_task_immediate, QueuedTask
        from core.governance.approvals import ApprovalManager
        from uuid import uuid4

        logger.info("Reactive dispatch loop started")
        approval_manager = ApprovalManager(self._substrate_service)

        # Message queue (in-memory for now, could be Redis-backed)
        message_queue = []

        while True:
            try:
                # Poll for messages (placeholder - would integrate with actual message source)
                # For now, this is a stub that can be extended
                await asyncio.sleep(1.0)  # Poll interval

                # Process any pending messages
                while message_queue:
                    message = message_queue.pop(0)

                    # Generate tasks from query
                    task_specs = await _generate_tasks_from_query(message)

                    for spec in task_specs:
                        # Check if task requires approval
                        task_type = spec["payload"].get("type", "")
                        if task_type in ["gmp_run", "git_commit"]:
                            # High-risk task - check approval
                            task_id = str(uuid4())
                            is_approved = await approval_manager.is_approved(task_id)

                            if not is_approved:
                                logger.info(
                                    f"Task {task_id} requires approval, skipping immediate dispatch"
                                )
                                continue

                        # Dispatch immediately
                        task = QueuedTask(
                            task_id=str(uuid4()),
                            name=spec["name"],
                            payload=spec["payload"],
                            handler=spec["handler"],
                            agent_id="L",
                            priority=spec.get("priority", 5),
                            tags=["reactive"],
                        )

                        await dispatch_task_immediate(task)
                        logger.info(f"Dispatched reactive task {task.task_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in reactive dispatch loop: {e}", exc_info=True)
                await asyncio.sleep(1.0)

        logger.info("Reactive dispatch loop stopped")

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
            return (
                f"agent_id is required (hint: use default '{self._default_agent_id}')"
            )

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

        # Pre-execution governance validation
        try:
            from core.governance.validation import validate_authority, validate_safety

            # Extract action from task
            action = (
                instance.task.payload.get("message")
                or instance.task.payload.get("query")
                or str(instance.task.payload)
            )

            # Authority check
            authority_check = validate_authority(
                action=action, agent_id=instance.task.agent_id
            )
            if not authority_check["valid"]:
                logger.warning(
                    "agent.executor.governance.blocked: authority violation",
                    extra={
                        "agent_id": instance.task.agent_id,
                        "violation": authority_check.get("violation"),
                        "task_id": str(instance.task.id),
                    },
                )
                return ExecutionResult(
                    task_id=instance.task.id,
                    status="blocked",
                    error=f"Authority violation: {authority_check.get('violation')}",
                    iterations=0,
                    duration_ms=int(
                        (datetime.utcnow() - start_time).total_seconds() * 1000
                    ),
                )

            # Safety check
            safety_check = validate_safety(action=action, payload=instance.task.payload)
            if not safety_check["safe"]:
                logger.warning(
                    "agent.executor.governance.blocked: safety violation",
                    extra={
                        "agent_id": instance.task.agent_id,
                        "violation": safety_check.get("violation"),
                        "pattern": safety_check.get("pattern"),
                        "task_id": str(instance.task.id),
                    },
                )
                return ExecutionResult(
                    task_id=instance.task.id,
                    status="blocked",
                    error=f"Safety violation: {safety_check.get('violation')}",
                    iterations=0,
                    duration_ms=int(
                        (datetime.utcnow() - start_time).total_seconds() * 1000
                    ),
                )
        except ImportError:
            # Governance validation not available - skip (non-fatal)
            logger.debug(
                "agent.executor.governance: validation module not available, skipping"
            )
        except Exception as e:
            # Governance check failed - log but continue (non-fatal)
            logger.warning(
                f"agent.executor.governance: validation error (non-fatal): {e}"
            )

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
                    "agent_id": instance.task.agent_id,  # Used to set metadata.agent
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

                # CRITICAL: Add assistant message with tool_calls BEFORE tool result
                # OpenAI requires: assistant (with tool_calls) → tool (with matching tool_call_id)
                instance.add_assistant_message_with_tool_calls(
                    tool_calls=[
                        {
                            "id": str(tool_call.call_id),
                            "type": "function",
                            "function": {
                                "name": tool_call.tool_id,
                                "arguments": json.dumps(tool_call.arguments),
                            },
                        }
                    ],
                    content=None,  # Tool call messages typically have no content
                )

                # Dispatch tool call using tool_id
                tool_result = await self._dispatch_tool_call(instance, tool_call)

                # Add result to history using tool_id (canonical identity)
                instance.add_tool_result(
                    tool_id=tool_call.tool_id,
                    call_id=str(tool_call.call_id),
                    result=tool_result.result
                    if tool_result.success
                    else tool_result.error,
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
        if (
            instance.iteration >= max_iterations
            and instance.state == ExecutorState.REASONING
        ):
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

        # Post-execution audit logging
        try:
            from core.governance.validation import audit_log

            action = (
                instance.task.payload.get("message")
                or instance.task.payload.get("query")
                or str(instance.task.payload)
            )
            audit_log(
                agent_id=instance.task.agent_id,
                action=action[:200],  # Truncate for audit trail
                success=(status == "completed"),
                metadata={
                    "task_id": str(instance.task.id),
                    "iterations": instance.iteration,
                    "duration_ms": duration_ms,
                    "status": status,
                },
            )
        except ImportError:
            # Audit logging not available - skip (non-fatal)
            pass
        except Exception as e:
            # Audit logging failed - log but don't fail execution
            logger.debug(f"agent.executor.audit: logging failed (non-fatal): {e}")

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
                "agent_id": instance.task.agent_id,  # Used to set metadata.agent
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

        # Bind memory context before execution
        memory_context = await self._bind_memory_context(
            task_id=str(instance.task.id),
            agent_id=instance.config.agent_id,
        )
        if memory_context:
            logger.debug(
                f"Loaded memory context for task {instance.task.id}: {len(memory_context)} keys"
            )

        # Check if tool requires Igor approval
        catalog = await ToolGraph.get_l_tool_catalog()
        tool_def = next((t for t in catalog if t["name"] == tool_call.tool_id), None)

        if tool_def and tool_def.get("requires_igor_approval"):
            approval_manager = ApprovalManager(self._substrate_service)
            is_approved = await approval_manager.is_approved(str(tool_call.call_id))

            if not is_approved:
                # Get adaptive context from past patterns for high-risk tools
                adaptive_context = ""
                try:
                    from core.agents.adaptive_prompting import get_adaptive_context_for_tool

                    adaptive_context = await get_adaptive_context_for_tool(
                        tool_call.tool_id
                    )
                    if adaptive_context:
                        logger.info(
                            f"Loaded adaptive context for {tool_call.tool_id}",
                            context_length=len(adaptive_context),
                        )
                except Exception as e:
                    logger.debug(f"Could not load adaptive context: {e}")

                logger.warning(
                    f"Tool {tool_call.tool_id} requires approval but not approved. task_id=%s, call_id=%s",
                    str(instance.task.id),
                    str(tool_call.call_id),
                )
                return ToolCallResult(
                    call_id=tool_call.call_id,
                    tool_id=tool_call.tool_id,
                    success=False,
                    error="PENDING_IGOR_APPROVAL",
                    result={
                        "status": "pending",
                        "message": "Awaiting Igor approval",
                        "adaptive_context": adaptive_context,
                    },
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
                    "memory_context": memory_context,  # Inject memory context
                },
            )

            # Persist task result after execution
            await self._persist_task_result(
                task_id=str(instance.task.id),
                result={
                    "agent_id": instance.config.agent_id,
                    "tool_id": tool_call.tool_id,
                    "call_id": str(tool_call.call_id),
                    "status": "completed" if result.success else "failed",
                    "error": result.error,
                    "duration_ms": result.duration_ms or 0,
                    "completed_at": datetime.utcnow().isoformat(),
                },
            )

            # Audit: log tool call in ToolGraph (best-effort)
            try:
                await ToolGraph.log_tool_call(
                    tool_name=tool_call.tool_id,
                    agent_id=instance.config.agent_id,
                    success=result.success,
                    duration_ms=result.duration_ms,
                    error=result.error,
                )
            except Exception as log_err:
                logger.warning(
                    "tool_call_audit_failed: task_id=%s, tool_id=%s, error=%s",
                    str(instance.task.id),
                    tool_call.tool_id,
                    str(log_err),
                )

            # Emit world model insight (best-effort)
            try:
                insight_emitter = get_insight_emitter(self._substrate_service)
                await insight_emitter.on_tool_called(
                    tool_name=tool_call.tool_id,
                    agent_id=instance.config.agent_id,
                    success=result.success,
                    duration_ms=result.duration_ms,
                    error=result.error,
                )
            except Exception as insight_err:
                logger.debug(f"Insight emission failed (non-fatal): {insight_err}")

            return result

        except Exception as e:
            logger.exception(
                "tool_dispatch_error: task_id=%s, tool_id=%s, error=%s",
                str(instance.task.id),
                tool_call.tool_id,
                str(e),
            )
            # Audit failure case as well
            try:
                await ToolGraph.log_tool_call(
                    tool_name=tool_call.tool_id,
                    agent_id=instance.config.agent_id,
                    success=False,
                    duration_ms=None,
                    error=str(e),
                )
            except Exception as log_err:
                logger.warning(
                    "tool_call_audit_failed: task_id=%s, tool_id=%s, error=%s",
                    str(instance.task.id),
                    tool_call.tool_id,
                    str(log_err),
                )

            return ToolCallResult(
                call_id=tool_call.call_id,
                tool_id=tool_call.tool_id,
                success=False,
                error=str(e),
            )

    async def _execute_plan_sequence(self, plan_id: str) -> Dict[str, Any]:
        """
        Dequeue and execute tasks from a plan in order, with approval checks.

        Args:
            plan_id: Plan identifier (thread_id)

        Returns:
            Dict with execution summary: completed, failed, pending_approvals
        """
        from runtime.task_queue import TaskQueue
        from core.governance.approvals import ApprovalManager

        task_queue = TaskQueue(queue_name="l9:tasks", use_redis=True)
        approval_manager = ApprovalManager(self._substrate_service)

        completed = []
        failed = []
        pending_approvals = []

        # Dequeue tasks with plan tag
        max_iterations = 100  # Safety limit
        iteration = 0

        while iteration < max_iterations:
            task = await task_queue.dequeue()
            if task is None:
                break

            # Check if task belongs to this plan
            plan_tag = f"plan:{plan_id}"
            if plan_tag not in task.tags:
                # Re-enqueue if not for this plan
                await task_queue.enqueue(
                    name=task.name,
                    payload=task.payload,
                    handler=task.handler,
                    agent_id=task.agent_id,
                    priority=task.priority,
                    tags=task.tags,
                )
                iteration += 1
                continue

            # Check if task requires approval
            task_type = task.payload.get("type", "")
            if task_type in ["gmp_run", "git_commit"]:
                is_approved = await approval_manager.is_approved(task.task_id)
                if not is_approved:
                    pending_approvals.append(
                        {
                            "task_id": task.task_id,
                            "name": task.name,
                            "type": task_type,
                        }
                    )
                    logger.info(f"Task {task.task_id} requires approval, skipping")
                    iteration += 1
                    continue

            # Execute task via handler
            try:
                handler = task_queue._handlers.get(task.handler)
                if handler:
                    result = await handler(task)
                    completed.append(
                        {
                            "task_id": task.task_id,
                            "name": task.name,
                            "result": str(result)[:200] if result else "success",
                        }
                    )
                else:
                    failed.append(
                        {
                            "task_id": task.task_id,
                            "name": task.name,
                            "error": f"No handler for {task.handler}",
                        }
                    )
            except Exception as e:
                failed.append(
                    {
                        "task_id": task.task_id,
                        "name": task.name,
                        "error": str(e),
                    }
                )

            iteration += 1

        return {
            "plan_id": plan_id,
            "completed": completed,
            "failed": failed,
            "pending_approvals": pending_approvals,
            "summary": {
                "total_completed": len(completed),
                "total_failed": len(failed),
                "total_pending": len(pending_approvals),
            },
        }

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
        - payload: Contains task_id and event-specific data (should include agent_id)
        - thread_id: Thread identity for grouping
        - metadata.agent: Agent ID from payload.agent_id or "agent.executor" as fallback
        - metadata.schema_version: "1.0.0"

        NOTE: Per PacketEnvelope.yaml spec, metadata should use agent_id field.
        Current implementation uses metadata.agent (field name discrepancy to be resolved).

        Args:
            packet_type: Type of packet (e.g., "agent.executor.trace")
            payload: Packet payload (must contain task_id)
            thread_id: Thread identifier
        """
        try:
            # Use task.agent_id if available in payload, otherwise "agent.executor"
            agent_id = payload.get("agent_id", "agent.executor")

            packet = PacketEnvelopeIn(
                packet_type=packet_type,
                payload=payload,
                thread_id=thread_id,
                metadata=PacketMetadata(
                    agent=agent_id,
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
                "agent_id": task.agent_id,  # Used to set metadata.agent
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
