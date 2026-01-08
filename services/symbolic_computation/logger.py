"""
Structured logging configuration for symbolic computation module.
"""

import logging
import json
from typing import Any, Dict
from pythonjsonlogger import jsonlogger


class StructuredLogger(logging.Logger):
    """Custom logger with structured JSON output."""

    def __init__(self, name: str):
        """Initialize structured logger."""
        super().__init__(name)
        self._configure_handler()

    def _configure_handler(self):
        """Configure JSON log handler."""
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            timestamp=True
        )
        handler.setFormatter(formatter)
        self.addHandler(handler)
        self.setLevel(logging.INFO)

    def log_structured(
        self,
        level: int,
        message: str,
        extra: Dict[str, Any] = None
    ):
        """
        Log structured message.

        Args:
            level: Log level
            message: Log message
            extra: Additional structured data
        """
        self.log(level, message, extra=extra or {})


def get_logger(name: str) -> logging.Logger:
    """
    Get or create logger instance.

    Args:
        name: Logger name

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "SER-OPER-017",
    "component_name": "Logger",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "symbolic_computation",
    "type": "utility",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Implements StructuredLogger for logger functionality",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
