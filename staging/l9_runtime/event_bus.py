"""
L9 Event Bus - Event-driven communication
"""
from typing import Dict, List, Callable, Any
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    L9 Runtime Event Bus
    
    Provides pub/sub event system for:
    - Module communication
    - Observability hooks
    - Audit trail generation
    - Real-time monitoring
    """
    
    def __init__(self):
        """Initialize event bus."""
        self.listeners = {}
        self.event_history = []
        self.initialized = False
    
    def initialize(self):
        """Initialize event bus system."""
        logger.info("Event bus initializing...")
        self.initialized = True
        logger.info("Event bus initialized")
    
    def emit(self, event_type: str, data: dict):
        """
        Emit event to all registered listeners.
        
        Args:
            event_type: Type of event (e.g., "directive_completed")
            data: Event data payload
        """
        logger.debug(f"Emitting event: {event_type}")
        
        # Record in history
        self.event_history.append({
            "type": event_type,
            "data": data
        })
        
        # Notify listeners
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                try:
                    listener(data)
                except Exception as e:
                    logger.error(f"Listener error for {event_type}: {e}")
    
    def subscribe(self, event_type: str, listener: Callable):
        """
        Subscribe to event type.
        
        Args:
            event_type: Event type to listen for
            listener: Callback function(data: dict)
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        self.listeners[event_type].append(listener)
        logger.debug(f"Listener subscribed to: {event_type}")
    
    def unsubscribe(self, event_type: str, listener: Callable):
        """
        Unsubscribe from event type.
        
        Args:
            event_type: Event type
            listener: Callback to remove
        """
        if event_type in self.listeners:
            try:
                self.listeners[event_type].remove(listener)
                logger.debug(f"Listener unsubscribed from: {event_type}")
            except ValueError:
                logger.warning(f"Listener not found for: {event_type}")
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[dict]:
        """
        Get event history.
        
        Args:
            event_type: Filter by event type (None = all events)
            limit: Maximum events to return
            
        Returns:
            List of events
        """
        if event_type:
            filtered = [e for e in self.event_history if e["type"] == event_type]
            return filtered[-limit:]
        else:
            return self.event_history[-limit:]
    
    def clear_history(self):
        """Clear event history (for testing/reset)."""
        self.event_history = []
        logger.info("Event history cleared")

