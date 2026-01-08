# ══════════════════════════════════════════════════════════════════════════════
# Generated from Module-Spec v2.6
# module_id: email.adapter
# enforced_acceptance: ["valid_email_processed", "idempotent_replay_cached", "email_parsed_correctly", "aios_response_forwarded", "packet_written_on_success", ... (8 total)]
# ══════════════════════════════════════════════════════════════════════════════
# DORA META BLOCK — DO NOT EDIT MANUALLY (CI-owned)
# ══════════════════════════════════════════════════════════════════════════════
# __meta__ = {
#     "template_version": "2.6.0",
#     "spec_hash": "SPEC-62d9295fc71f",
#     "created_at": "2025-12-18T06:24:54.974886+00:00",
#     "created_by": "module_pipeline",
#     "last_updated_at": "2025-12-18T06:24:54.974886+00:00",
#     "last_updated_by": "module_pipeline",
#     "module_id": "email.adapter",
#     "file": "schemas.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Email Adapter Schemas
─────────────────────
Pydantic models for request/response validation.

Auto-generated from Module-Spec v2.6.0
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class EmailAdapterRequest(BaseModel):
    """Inbound request schema for Email Adapter."""

    event_id: Optional[str] = Field(
        None, description="Unique event identifier for idempotency"
    )
    source: Optional[str] = Field(None, description="Event source identifier")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    payload: dict[str, Any] = Field(default_factory=dict, description="Event payload")

    # Attachment support
    attachments: list[dict[str, Any]] = Field(
        default_factory=list, description="File attachments"
    )

    class Config:
        extra = "allow"


class EmailAdapterResponse(BaseModel):
    """Response schema for Email Adapter."""

    ok: bool = Field(..., description="Whether the request succeeded")
    packet_id: Optional[str] = Field(None, description="ID of the emitted packet")
    dedupe: bool = Field(False, description="Whether this was a duplicate request")
    error: Optional[str] = Field(None, description="Error message if ok=False")
    data: Optional[dict[str, Any]] = Field(None, description="Response data")


class EmailAdapterContext(BaseModel):
    """Execution context for Email Adapter."""

    thread_uuid: UUID = Field(..., description="Deterministic thread UUID")
    source: str = Field("email.adapter", description="Source module ID")
    task_id: Optional[str] = Field(None, description="Task identifier")
    tool_id: Optional[str] = Field(None, description="Tool identifier")

    class Config:
        frozen = True


class PacketPayload(BaseModel):
    """Standard packet payload structure."""

    request: Optional[dict[str, Any]] = None
    response: Optional[dict[str, Any]] = None
    error: Optional[dict[str, str]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "API-OPER-015",
    "component_name": "Schemas",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:13Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "api_gateway",
    "type": "schema",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Provides schemas components including EmailAdapterRequest, EmailAdapterResponse, EmailAdapterContext",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
