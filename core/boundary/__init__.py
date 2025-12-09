"""
L9 Core Boundary Module
=======================

PRIVATE_BOUNDARY enforcement at the orchestrator edge.

Provides:
- Boundary specification loading and parsing
- Prompt/response enforcement (redaction)
- Payload field protection

Version: 1.0.0
"""

from core.boundary.enforcer import (
    # Functions
    load_boundary_spec,
    parse_boundary_spec,
    enforce_boundary,
    enforce_response_boundary,
    enforce_payload_boundary,
    get_default_enforcer,
    # Classes
    BoundarySpec,
    BoundaryEnforcer,
    # Constants
    BOUNDARY_FILE,
)

__all__ = [
    # Functions
    "load_boundary_spec",
    "parse_boundary_spec",
    "enforce_boundary",
    "enforce_response_boundary",
    "enforce_payload_boundary",
    "get_default_enforcer",
    # Classes
    "BoundarySpec",
    "BoundaryEnforcer",
    # Constants
    "BOUNDARY_FILE",
]

