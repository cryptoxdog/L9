"""
L9 OS Bootstrap
Loads settings, initializes controller, router, cursor client, and local API.
No dynamic module discovery - everything explicitly imported.
"""

import yaml
import structlog
from pathlib import Path
from typing import Dict, Any

from .controller import Controller
from .router import Router
from .local_api import LocalAPI
from ..tools.cursor_client import CursorClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = structlog.get_logger(__name__)


class Bootstrap:
    """Bootstrap manager for L9 OS kernel."""

    def __init__(self, config_path: str = "/opt/l9/config/settings.yaml"):
        self.config_path = Path(config_path)
        self.settings: Dict[str, Any] = {}
        self.controller: Controller = None
        self.router: Router = None
        self.cursor_client: CursorClient = None
        self.local_api: LocalAPI = None

    def load_settings(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            self.settings = yaml.safe_load(f) or {}

        logger.info(f"Loaded settings from {self.config_path}")
        return self.settings

    def init_controller(self) -> Controller:
        """Initialize the controller."""
        if not self.settings:
            raise RuntimeError("Settings must be loaded before initializing controller")

        self.controller = Controller(
            settings=self.settings,
            local_api=self.local_api,
            cursor_client=self.cursor_client,
        )
        logger.info("Controller initialized")
        return self.controller

    def init_router(self) -> Router:
        """Initialize the router."""
        if not self.controller:
            raise RuntimeError("Controller must be initialized before router")

        self.router = Router(controller=self.controller)
        logger.info("Router initialized")
        return self.router

    def init_cursor_client(self) -> CursorClient:
        """Initialize Cursor client."""
        if not self.settings:
            raise RuntimeError(
                "Settings must be loaded before initializing cursor client"
            )

        host = self.settings.get("cursor_host", "127.0.0.1")
        port = self.settings.get("cursor_port", 3000)
        timeout = self.settings.get("request_timeout", 30)

        self.cursor_client = CursorClient(host=host, port=port, timeout=timeout)
        logger.info(f"Cursor client initialized: {host}:{port}")
        return self.cursor_client

    def init_local_api(self) -> LocalAPI:
        """Initialize local API for safe shell/file operations."""
        if not self.settings:
            raise RuntimeError("Settings must be loaded before initializing local API")

        self.local_api = LocalAPI(settings=self.settings)
        logger.info("Local API initialized")
        return self.local_api

    def bootstrap(self) -> tuple[Router, Controller]:
        """
        Complete bootstrap sequence.
        Returns: (router, controller) tuple
        """
        logger.info("Starting L9 OS bootstrap...")

        # Load settings first
        self.load_settings()

        # Initialize components in dependency order
        self.init_local_api()
        self.init_cursor_client()
        self.init_controller()
        self.init_router()

        logger.info("Bootstrap complete")
        return self.router, self.controller
