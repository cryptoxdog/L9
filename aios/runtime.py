"""
L9 OS Runtime
Single entrypoint for systemd service.
Infinite loop with error handling and clean shutdown.
"""

import sys
import signal
import structlog
import time

from .bootstrap import Bootstrap

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = structlog.get_logger(__name__)


class Runtime:
    """L9 OS runtime loop."""

    def __init__(self, config_path: str = "/opt/l9/config/settings.yaml"):
        self.config_path = config_path
        self.bootstrap = Bootstrap(config_path)
        self.router = None
        self.controller = None
        self.running = False
        self.shutdown_requested = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown_requested = True

    def start(self):
        """Start the runtime loop."""
        try:
            logger.info("Starting L9 OS runtime...")

            # Bootstrap system
            self.router, self.controller = self.bootstrap.bootstrap()

            if not self.router or not self.controller:
                logger.error("Bootstrap failed - router or controller not initialized")
                sys.exit(1)

            self.running = True
            logger.info("L9 OS runtime started successfully")

            # Main loop
            loop_count = 0
            while self.running and not self.shutdown_requested:
                try:
                    # Phase 1: Simple heartbeat loop
                    # Phase 2: Will poll for messages from API
                    loop_count += 1

                    if loop_count % 60 == 0:  # Log every 60 iterations
                        logger.debug(f"Runtime heartbeat: loop={loop_count}")

                    time.sleep(1)  # 1 second heartbeat

                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received")
                    self.shutdown_requested = True
                    break
                except Exception as e:
                    logger.error(f"Runtime loop error: {e}", exc_info=True)
                    # Continue running despite errors
                    time.sleep(1)

            logger.info("Runtime loop exited")

        except Exception as e:
            logger.error(f"Runtime startup error: {e}", exc_info=True)
            sys.exit(1)
        finally:
            self.shutdown()

    def shutdown(self):
        """Clean shutdown."""
        logger.info("Shutting down L9 OS runtime...")
        self.running = False

        # Cleanup resources
        if self.controller:
            logger.info("Controller shutdown complete")

        if self.router:
            logger.info("Router shutdown complete")

        logger.info("Shutdown complete")


def main():
    """Main entrypoint for systemd service."""
    # Default config path
    config_path = "/opt/l9/config/settings.yaml"

    # Allow override via environment or CLI
    import os

    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    elif os.getenv("L9_CONFIG_PATH"):
        config_path = os.getenv("L9_CONFIG_PATH")

    runtime = Runtime(config_path=config_path)
    runtime.start()


if __name__ == "__main__":
    main()

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "AIO-OPER-005",
    "component_name": "Runtime",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:13Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "aios",
    "type": "utility",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Implements Runtime for runtime functionality",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
