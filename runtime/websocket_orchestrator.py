"""
L9 Runtime - WebSocket Orchestrator
====================================

Central broker for WebSocket-connected agents.

Responsibilities:
- Track connected agents (registration/deregistration)
- Receive and validate EventMessage frames
- Dispatch events to agents (unicast and broadcast)
- Provide hooks for task_queue integration

This orchestrator is designed to be instantiated once per FastAPI
application and shared across all WebSocket connections.

Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

from fastapi import WebSocket

from core.schemas.ws_event_stream import EventMessage, EventType

logger = logging.getLogger(__name__)


class WebSocketOrchestrator:
    """
    Central broker for WebSocket-connected agents.
    
    Thread-safe connection management with asyncio locks.
    
    Attributes:
        _connections: Mapping of agent_id -> WebSocket
        _metadata: Per-agent metadata (handshake info, last seen, etc.)
        _lock: Asyncio lock for connection state mutations
        
    Usage:
        orchestrator = WebSocketOrchestrator()
        await orchestrator.register("agent-1", websocket)
        await orchestrator.send_to_agent("agent-1", event)
        await orchestrator.unregister("agent-1")
    """
    
    def __init__(self) -> None:
        """Initialize the orchestrator with empty connection state."""
        self._connections: Dict[str, WebSocket] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._task_queue: Optional[Any] = None  # TaskQueue instance (lazy-loaded)
    
    def set_task_queue(self, task_queue: Any) -> None:
        """
        Set the task queue for event routing.
        
        Phase 2 integration point for runtime.task_queue.
        
        Args:
            task_queue: TaskQueue instance
        """
        self._task_queue = task_queue
        logger.info("Task queue connected to WebSocketOrchestrator")
    
    # =========================================================================
    # Connection Management
    # =========================================================================
    
    async def register(
        self,
        agent_id: str,
        websocket: WebSocket,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a new agent connection.
        
        Args:
            agent_id: Unique identifier for the agent
            websocket: The WebSocket connection object
            metadata: Optional metadata from handshake
        """
        async with self._lock:
            # Close existing connection if agent reconnects
            if agent_id in self._connections:
                logger.warning(
                    "Agent %s reconnecting, closing previous connection",
                    agent_id
                )
                try:
                    await self._connections[agent_id].close(
                        code=1000,
                        reason="Superseded by new connection"
                    )
                except Exception:  # noqa: BLE001
                    pass  # Ignore errors closing stale connection
            
            self._connections[agent_id] = websocket
            self._metadata[agent_id] = metadata or {}
        
        logger.info("Agent connected via WS: %s", agent_id)
    
    async def unregister(self, agent_id: str) -> None:
        """
        Remove an agent from the connection pool.
        
        Args:
            agent_id: Agent to unregister
        """
        async with self._lock:
            self._connections.pop(agent_id, None)
            self._metadata.pop(agent_id, None)
        
        logger.info("Agent disconnected from WS: %s", agent_id)
    
    async def is_connected(self, agent_id: str) -> bool:
        """Check if an agent is currently connected."""
        async with self._lock:
            return agent_id in self._connections
    
    async def get_connected_agents(self) -> list[str]:
        """Return list of currently connected agent IDs."""
        async with self._lock:
            return list(self._connections.keys())
    
    async def get_agent_metadata(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a connected agent."""
        async with self._lock:
            return self._metadata.get(agent_id)
    
    # =========================================================================
    # Message Sending
    # =========================================================================
    
    async def send_to_agent(self, agent_id: str, event: EventMessage) -> None:
        """
        Send an event to a specific agent.
        
        Args:
            agent_id: Target agent identifier
            event: Event to send
            
        Raises:
            RuntimeError: If agent is not connected
        """
        async with self._lock:
            ws = self._connections.get(agent_id)
        
        if ws is None:
            raise RuntimeError(f"Agent {agent_id} is not connected")
        
        await ws.send_json(event.model_dump(mode="json"))
        logger.debug("Sent event %s to agent %s", event.type, agent_id)
    
    async def broadcast(
        self,
        event: EventMessage,
        exclude: Optional[set[str]] = None,
    ) -> int:
        """
        Broadcast an event to all connected agents.
        
        Args:
            event: Event to broadcast
            exclude: Set of agent_ids to exclude from broadcast
            
        Returns:
            Number of agents the message was successfully sent to
        """
        exclude = exclude or set()
        
        async with self._lock:
            targets = [
                (agent_id, ws)
                for agent_id, ws in self._connections.items()
                if agent_id not in exclude
            ]
        
        success_count = 0
        payload = event.model_dump(mode="json")
        
        for agent_id, ws in targets:
            try:
                await ws.send_json(payload)
                success_count += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Failed to broadcast event to %s: %s",
                    agent_id,
                    exc
                )
        
        logger.debug(
            "Broadcast event %s to %d/%d agents",
            event.type,
            success_count,
            len(targets)
        )
        return success_count
    
    # =========================================================================
    # Message Handling
    # =========================================================================
    
    async def handle_incoming(self, agent_id: str, data: dict) -> Optional[EventMessage]:
        """
        Handle inbound JSON payload from an agent.
        
        Phase 1: Validate and log the event.
        Phase 2: Route into task_queue via ws_task_router.
        
        Args:
            agent_id: Agent that sent the message
            data: Raw JSON payload
            
        Returns:
            Validated EventMessage if successful, None if validation failed
        """
        try:
            event = EventMessage.model_validate(data)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Invalid WS event from %s: %s | Data: %s",
                agent_id,
                exc,
                data
            )
            return None
        
        # Log based on event type
        if event.type == EventType.HEARTBEAT:
            logger.debug("Heartbeat from %s", agent_id)
        elif event.type == EventType.TASK_RESULT:
            logger.info(
                "Task result from %s: %s",
                agent_id,
                event.payload.get("task_id", "unknown")
            )
        elif event.type == EventType.ERROR:
            logger.warning(
                "Error event from %s: %s",
                agent_id,
                event.payload.get("message", "no message")
            )
        else:
            logger.debug(
                "Inbound WS event from %s: type=%s",
                agent_id,
                event.type
            )
        
        # Phase 2.5: Route event to task queue
        await self._route_to_task_queue(event, agent_id)
        
        return event
    
    async def _route_to_task_queue(
        self,
        event: EventMessage,
        agent_id: str,
    ) -> None:
        """
        Route inbound events to the task queue.
        
        Phase 2 integration: Converts WebSocket events into queued tasks
        for processing by the unified controller.
        
        Args:
            event: Validated EventMessage
            agent_id: Source agent identifier
        """
        try:
            from orchestration.ws_task_router import route_event_to_task
            
            envelope = route_event_to_task(event)
            
            if envelope is not None:
                # Enqueue the task for processing
                if self._task_queue is not None:
                    await self._task_queue.enqueue(
                        name=f"ws_event_{event.type.value}",
                        payload=envelope.to_dict(),
                        handler="ws_event_handler",
                        agent_id=agent_id,
                        tags=["websocket", event.type.value],
                    )
                    logger.debug(
                        "Enqueued task from WS event: type=%s, agent=%s",
                        event.type,
                        agent_id
                    )
                else:
                    # Queue not connected yet - log for Phase 3 debugging
                    logger.debug(
                        "Task queue not connected, skipping enqueue: type=%s",
                        event.type
                    )
        except ImportError as e:
            logger.warning("Task router not available: %s", e)
        except Exception as e:
            logger.error("Failed to route event to task queue: %s", e)
    
    # =========================================================================
    # Task Dispatch (Phase 2)
    # =========================================================================
    
    async def dispatch_task(
        self,
        agent_id: str,
        task_id: str,
        task_type: str,
        payload: Dict[str, Any],
    ) -> None:
        """
        Dispatch a task to a specific agent.
        
        Args:
            agent_id: Target agent
            task_id: Unique task identifier
            task_type: Type of task to execute
            payload: Task parameters
        """
        event = EventMessage(
            type=EventType.TASK_ASSIGNED,
            channel="task",
            agent_id=agent_id,
            payload={
                "task_id": task_id,
                "task_type": task_type,
                **payload,
            },
        )
        await self.send_to_agent(agent_id, event)
        logger.info("Dispatched task %s to agent %s", task_id, agent_id)
    
    async def dispatch_event(
        self,
        agent_id: str,
        event: "EventMessage",
    ) -> None:
        """
        Dispatch an EventMessage directly to an agent.
        
        Phase 2 integration: Used by unified_controller to send
        pre-constructed EventMessages over WebSocket.
        
        Args:
            agent_id: Target agent identifier
            event: EventMessage to dispatch
        """
        await self.send_to_agent(agent_id, event)
        logger.debug("Dispatched event %s to agent %s", event.type, agent_id)
    
    async def dispatch_task_envelope(
        self,
        envelope: Any,
    ) -> None:
        """
        Dispatch a TaskEnvelope to its assigned agent.
        
        Phase 2 integration: Converts TaskEnvelope to EventMessage
        and sends via WebSocket.
        
        Args:
            envelope: TaskEnvelope with agent_id and task
        """
        from core.schemas.tasks import TaskEnvelope
        
        if not isinstance(envelope, TaskEnvelope):
            raise TypeError("Expected TaskEnvelope")
        
        if not envelope.agent_id:
            raise ValueError("TaskEnvelope must have agent_id for dispatch")
        
        event = EventMessage(
            type=EventType.TASK_ASSIGNED,
            channel="task",
            agent_id=envelope.agent_id,
            payload={
                "task_id": str(envelope.task.id),
                "task_kind": envelope.task.kind,
                "task_payload": envelope.task.payload,
                "priority": envelope.task.priority,
                "trace_id": envelope.task.trace_id,
            },
            trace_id=envelope.task.trace_id,
        )
        
        await self.send_to_agent(envelope.agent_id, event)
        logger.info(
            "Dispatched task envelope %s to agent %s",
            envelope.task.id,
            envelope.agent_id
        )


# =============================================================================
# Module-level singleton
# =============================================================================

# Shared orchestrator instance used across the application.
# Import this from api/server.py, unified_controller, and other modules
# that need to interact with WebSocket-connected agents.
ws_orchestrator = WebSocketOrchestrator()


def get_ws_orchestrator() -> WebSocketOrchestrator:
    """
    Get the shared WebSocket orchestrator instance.
    
    Returns:
        The module-level ws_orchestrator singleton
    """
    return ws_orchestrator


__all__ = [
    "WebSocketOrchestrator",
    "ws_orchestrator",
    "get_ws_orchestrator",
]

