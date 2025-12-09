"""
L9 Orchestration - WebSocket Task Router
=========================================

Routes inbound WebSocket EventMessages into actionable tasks.

Phase 2:
- Handle TASK_RESULT events → TaskEnvelope
- Handle ERROR events → TaskEnvelope
- Provide routing hooks for task_queue integration

Phase 3 (stub):
- LangGraph-based routing with state machine
- CONTROL and LOG event handling
- Custom event type registration

Version: 1.0.0
"""

from __future__ import annotations

import logging
from typing import Callable, Dict, Optional

from core.schemas.ws_event_stream import EventMessage, EventType
from core.schemas.tasks import AgentTask, TaskEnvelope, TaskKind

logger = logging.getLogger(__name__)


# =============================================================================
# Router Configuration
# =============================================================================

class RouterConfig:
    """Configuration for the WebSocket task router."""
    
    def __init__(
        self,
        emit_packets: bool = True,
        trace_events: bool = False,
        default_priority: int = 5,
    ):
        self.emit_packets = emit_packets
        self.trace_events = trace_events
        self.default_priority = default_priority


# =============================================================================
# Core Routing Function
# =============================================================================

def route_event_to_task(
    event: EventMessage,
    config: Optional[RouterConfig] = None,
) -> Optional[TaskEnvelope]:
    """
    Convert inbound WebSocket EventMessages into actionable tasks.
    
    This is the primary routing function that bridges WebSocket events
    to the task queue system.
    
    Phase 2:
      - Handle TASK_RESULT → route to completion handler
      - Handle ERROR → route to error handler
      - Future: CONTROL, LOG, custom events
    
    Args:
        event: Inbound WebSocket EventMessage
        config: Router configuration (optional)
        
    Returns:
        TaskEnvelope if event generates a task, None otherwise
        
    Usage:
        event = EventMessage(type=EventType.TASK_RESULT, ...)
        envelope = route_event_to_task(event)
        if envelope:
            task_queue.enqueue(envelope)
    """
    config = config or RouterConfig()
    
    if config.trace_events:
        logger.debug(f"Routing event: type={event.type}, agent={event.agent_id}")
    
    # Route based on event type
    if event.type == EventType.TASK_RESULT:
        return _route_task_result(event, config)
    
    elif event.type == EventType.ERROR:
        return _route_error_event(event, config)
    
    elif event.type == EventType.HEARTBEAT:
        # Heartbeats don't generate tasks
        return None
    
    elif event.type == EventType.HANDSHAKE:
        # Handshakes are handled separately by security layer
        return None
    
    elif event.type == EventType.CONTROL:
        # Phase 3: Route to control handler
        return _route_control_event(event, config)
    
    elif event.type == EventType.LOG:
        # Phase 3: Route to logging pipeline
        return None
    
    else:
        logger.warning(f"Unknown event type: {event.type}")
        return None


# =============================================================================
# Event-Specific Routing
# =============================================================================

def _route_task_result(
    event: EventMessage,
    config: RouterConfig,
) -> TaskEnvelope:
    """Route TASK_RESULT events to completion handler."""
    task = AgentTask(
        kind=TaskKind.RESULT.value,
        payload={
            "original_task_id": event.payload.get("task_id"),
            "result": event.payload.get("result"),
            "status": event.payload.get("status", "completed"),
            **{k: v for k, v in event.payload.items() if k not in ("task_id", "result", "status")},
        },
        priority=config.default_priority,
        trace_id=event.trace_id,
    )
    
    envelope = TaskEnvelope(
        task=task,
        agent_id=event.agent_id,
        source_event_id=event.id,
    )
    
    logger.info(
        f"Routed TASK_RESULT from {event.agent_id}: "
        f"task_id={event.payload.get('task_id')}"
    )
    
    return envelope


def _route_error_event(
    event: EventMessage,
    config: RouterConfig,
) -> TaskEnvelope:
    """Route ERROR events to error handler."""
    task = AgentTask(
        kind=TaskKind.ERROR.value,
        payload={
            "error_code": event.payload.get("code", "UNKNOWN"),
            "message": event.payload.get("message", "No message provided"),
            "details": event.payload.get("details", {}),
            "recoverable": event.payload.get("recoverable", True),
            **{k: v for k, v in event.payload.items() 
               if k not in ("code", "message", "details", "recoverable")},
        },
        priority=2,  # Errors are high priority
        trace_id=event.trace_id,
    )
    
    envelope = TaskEnvelope(
        task=task,
        agent_id=event.agent_id,
        source_event_id=event.id,
    )
    
    logger.warning(
        f"Routed ERROR from {event.agent_id}: "
        f"code={event.payload.get('code', 'UNKNOWN')}"
    )
    
    return envelope


def _route_control_event(
    event: EventMessage,
    config: RouterConfig,
) -> Optional[TaskEnvelope]:
    """
    Phase 3 Stub: Route CONTROL events.
    
    Control events include:
    - PAUSE/RESUME agent
    - SHUTDOWN requests
    - Configuration updates
    - Priority adjustments
    """
    control_action = event.payload.get("action")
    
    if control_action in ("pause", "resume", "shutdown", "reconfigure"):
        task = AgentTask(
            kind=TaskKind.COMMAND.value,
            payload={
                "control_action": control_action,
                **event.payload,
            },
            priority=1,  # Control messages are highest priority
            trace_id=event.trace_id,
        )
        
        envelope = TaskEnvelope(
            task=task,
            agent_id=event.agent_id,
            source_event_id=event.id,
        )
        
        logger.info(f"Routed CONTROL action={control_action} to {event.agent_id}")
        return envelope
    
    logger.debug(f"Ignoring CONTROL event with unknown action: {control_action}")
    return None


# =============================================================================
# Router Registry (Phase 3 Expansion Point)
# =============================================================================

class WSTaskRouter:
    """
    Extensible WebSocket task router.
    
    Provides registration hooks for custom event handlers.
    Phase 3 will integrate with LangGraph for state-machine routing.
    
    Usage:
        router = WSTaskRouter()
        router.register_handler(EventType.CUSTOM, my_handler)
        envelope = router.route(event)
    """
    
    def __init__(self, config: Optional[RouterConfig] = None):
        """Initialize the router with optional configuration."""
        self._config = config or RouterConfig()
        self._handlers: Dict[EventType, Callable[[EventMessage], Optional[TaskEnvelope]]] = {}
        self._default_handlers_registered = False
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register built-in event handlers."""
        if self._default_handlers_registered:
            return
        
        self._handlers[EventType.TASK_RESULT] = lambda e: _route_task_result(e, self._config)
        self._handlers[EventType.ERROR] = lambda e: _route_error_event(e, self._config)
        self._handlers[EventType.CONTROL] = lambda e: _route_control_event(e, self._config)
        
        self._default_handlers_registered = True
    
    def register_handler(
        self,
        event_type: EventType,
        handler: Callable[[EventMessage], Optional[TaskEnvelope]],
    ) -> None:
        """
        Register a custom event handler.
        
        Args:
            event_type: Event type to handle
            handler: Handler function
        """
        self._handlers[event_type] = handler
        logger.info(f"Registered custom handler for {event_type}")
    
    def unregister_handler(self, event_type: EventType) -> bool:
        """
        Unregister an event handler.
        
        Args:
            event_type: Event type to unregister
            
        Returns:
            True if handler was removed
        """
        if event_type in self._handlers:
            del self._handlers[event_type]
            logger.info(f"Unregistered handler for {event_type}")
            return True
        return False
    
    def route(self, event: EventMessage) -> Optional[TaskEnvelope]:
        """
        Route an event to a task envelope.
        
        Args:
            event: EventMessage to route
            
        Returns:
            TaskEnvelope or None
        """
        if self._config.trace_events:
            logger.debug(f"Routing via registry: type={event.type}")
        
        handler = self._handlers.get(event.type)
        
        if handler:
            return handler(event)
        
        # Fall back to static routing
        return route_event_to_task(event, self._config)
    
    def get_registered_types(self) -> list[EventType]:
        """Get list of registered event types."""
        return list(self._handlers.keys())


# =============================================================================
# Phase 3 Stubs
# =============================================================================

class LangGraphRouter:
    """
    Phase 3 Stub: LangGraph-based state machine router.
    
    Will provide:
    - Stateful routing decisions
    - Graph-based task dependencies
    - Conditional routing based on context
    - Integration with world model
    """
    
    def __init__(self):
        # TODO: Phase 3 - Initialize LangGraph state machine
        pass
    
    async def route(self, event: EventMessage, context: dict) -> Optional[TaskEnvelope]:
        """
        Route event using LangGraph state machine.
        
        Phase 3 implementation will:
        1. Load context from world model
        2. Execute routing graph
        3. Return task envelope with enriched context
        """
        # Fallback to simple routing until Phase 3
        return route_event_to_task(event)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "route_event_to_task",
    "RouterConfig",
    "WSTaskRouter",
    "LangGraphRouter",  # Phase 3 stub
]

