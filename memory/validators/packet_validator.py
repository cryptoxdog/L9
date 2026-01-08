"""
L9 Memory - Packet Validator
Version: 1.0.0

Centralized validation for PacketEnvelopeIn before it hits the DAG.
This is where we enforce business-level constraints above Pydantic's typing.
"""

from __future__ import annotations

from typing import Iterable

from pydantic import ValidationError

from memory.substrate_models import PacketEnvelopeIn


ALLOWED_PACKET_TYPES: set[str] = {
    "event",
    "memory_write",
    "reasoning_trace",
    "tool_call",
    "tool_result",
    "message",
}


class PacketValidationError(Exception):
    """Raised when a packet fails custom validation."""


class PacketValidator:
    """Static helpers for validating PacketEnvelopeIn instances."""

    @staticmethod
    def validate(packet_in: PacketEnvelopeIn) -> None:
        """
        Perform custom validation:
        - Pydantic structural validation
        - packet_type sanity check
        """
        # This will re-run Pydantic's field-level checks
        try:
            PacketEnvelopeIn.model_validate(packet_in.model_dump())
        except ValidationError as exc:
            raise PacketValidationError(f"Structural validation failed: {exc}") from exc

        if packet_in.packet_type not in ALLOWED_PACKET_TYPES:
            raise PacketValidationError(
                f"packet_type '{packet_in.packet_type}' not in {sorted(ALLOWED_PACKET_TYPES)}"
            )

    @staticmethod
    def allowed_types() -> Iterable[str]:
        return sorted(ALLOWED_PACKET_TYPES)

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "MEM-LEAR-024",
    "component_name": "Packet Validator",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "learning",
    "domain": "memory_substrate",
    "type": "utility",
    "status": "active",
    "governance_level": "critical",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Provides packet validator components including PacketValidationError, PacketValidator",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
