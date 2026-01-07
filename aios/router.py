"""
L9 OS Router
Dispatch table for message routing.
Routes cursor, mac, local, and test message types.
"""

import structlog
from typing import Dict, Any

from .controller import Controller

logger = structlog.get_logger(__name__)


class Router:
    """Message router for L9 OS kernel."""

    def __init__(self, controller: Controller):
        self.controller = controller

        # Dispatch table
        self.handlers = {
            "cursor": self.controller.handle_cursor,
            "mac": self.controller.handle_mac,
            "local": self.controller.handle_local,
            "test": self.controller.handle_test,
        }

    def route(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route message to appropriate handler.
        Message must have 'type' field: "cursor", "mac", "local", or "test"

        Returns: Handler response dict
        """
        try:
            msg_type = message.get("type", "").lower()

            if not msg_type:
                return {
                    "success": False,
                    "error": "Missing message type",
                    "available_types": list(self.handlers.keys()),
                }

            if msg_type not in self.handlers:
                return {
                    "success": False,
                    "error": f"Unknown message type: {msg_type}",
                    "available_types": list(self.handlers.keys()),
                }

            # Dispatch to handler
            handler = self.handlers[msg_type]
            response = handler(message)

            logger.info(
                f"Routed {msg_type} message: success={response.get('success', False)}"
            )
            return response

        except Exception as e:
            logger.error(f"Router error: {e}")
            return {"success": False, "error": f"Router exception: {str(e)}"}

    def get_available_types(self) -> list[str]:
        """Return list of available message types."""
        return list(self.handlers.keys())
