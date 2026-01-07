"""
L9 OS Controller
The brain that manages commands and tool routing.
Handles cursor, mac, local, and test message types.
"""

import structlog
import shlex
from typing import Dict, Any, Optional
from datetime import datetime

from .local_api import LocalAPI
from ..tools.cursor_client import CursorClient

logger = structlog.get_logger(__name__)


class Controller:
    """Main controller for L9 OS kernel."""

    def __init__(
        self,
        settings: Dict[str, Any],
        local_api: LocalAPI,
        cursor_client: Optional[CursorClient] = None,
    ):
        self.settings = settings
        self.local_api = local_api
        self.cursor_client = cursor_client
        self.debug = settings.get("debug", False)

    def handle_cursor(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Cursor protocol messages.
        Message format: {type: "cursor", action: str, payload: Dict}
        """
        try:
            action = message.get("action", "")
            payload = message.get("payload", {})

            if not self.cursor_client:
                return {
                    "success": False,
                    "error": "Cursor client not initialized",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Forward to Cursor API
            if action == "send_code":
                code = payload.get("code", "")
                result = self.cursor_client.send_code(code)
                return {
                    "success": result.get("success", False),
                    "response": result.get("response", ""),
                    "timestamp": datetime.utcnow().isoformat(),
                }

            elif action == "send_command":
                command = payload.get("command", "")
                result = self.cursor_client.send_command(command)
                return {
                    "success": result.get("success", False),
                    "response": result.get("response", ""),
                    "timestamp": datetime.utcnow().isoformat(),
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown cursor action: {action}",
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Cursor handler error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def handle_mac(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Mac protocol messages (reverse tunnel).
        Message format: {type: "mac", token: str, cmd: str, args: List}
        """
        try:
            token = message.get("token", "")
            cmd = message.get("cmd", "")
            args = message.get("args", [])

            # Validate token (Phase 1: simple check, Phase 2: proper auth)
            if not token:
                return {
                    "success": False,
                    "error": "Missing token",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Build full command
            if args:
                full_cmd = f"{cmd} {' '.join(shlex.quote(str(a)) for a in args)}"
            else:
                full_cmd = cmd

            # Execute via local API
            result = self.local_api.execute_shell(full_cmd)

            return {
                "success": result.get("success", False),
                "output": result.get("output", ""),
                "error": result.get("error", ""),
                "exit_code": result.get("exit_code", -1),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Mac handler error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def handle_local(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle local API requests.
        Message format: {type: "local", action: str, params: Dict}
        """
        try:
            action = message.get("action", "")
            params = message.get("params", {})

            if action == "execute_shell":
                command = params.get("command", "")
                cwd = params.get("cwd")
                result = self.local_api.execute_shell(command, cwd=cwd)
                return {
                    "success": result.get("success", False),
                    "output": result.get("output", ""),
                    "error": result.get("error", ""),
                    "exit_code": result.get("exit_code", -1),
                    "timestamp": datetime.utcnow().isoformat(),
                }

            elif action == "read_file":
                file_path = params.get("file_path", "")
                limit = params.get("limit")
                result = self.local_api.read_file(file_path, limit=limit)
                return {
                    "success": result.get("success", False),
                    "content": result.get("content", ""),
                    "error": result.get("error", ""),
                    "timestamp": datetime.utcnow().isoformat(),
                }

            elif action == "write_file":
                file_path = params.get("file_path", "")
                content = params.get("content", "")
                result = self.local_api.write_file(file_path, content)
                return {
                    "success": result.get("success", False),
                    "error": result.get("error", ""),
                    "timestamp": datetime.utcnow().isoformat(),
                }

            elif action == "list_directory":
                dir_path = params.get("dir_path", "")
                result = self.local_api.list_directory(dir_path)
                return {
                    "success": result.get("success", False),
                    "files": result.get("files", []),
                    "error": result.get("error", ""),
                    "timestamp": datetime.utcnow().isoformat(),
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown local action: {action}",
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Local handler error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def handle_test(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle test/debug messages.
        Message format: {type: "test", message: str}
        """
        try:
            test_message = message.get("message", "test")

            return {
                "success": True,
                "response": f"Test successful: {test_message}",
                "timestamp": datetime.utcnow().isoformat(),
                "settings_loaded": bool(self.settings),
                "local_api_ready": self.local_api is not None,
                "cursor_client_ready": self.cursor_client is not None,
            }

        except Exception as e:
            logger.error(f"Test handler error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
