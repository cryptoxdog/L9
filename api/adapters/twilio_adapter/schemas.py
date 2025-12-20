# ══════════════════════════════════════════════════════════════════════════════
# Generated from Module-Spec v2.6
# module_id: twilio.adapter
# enforced_acceptance: ["valid_sms_processed", "idempotent_replay_cached", "signature_validated", "aios_response_forwarded", "packet_written_on_success", ... (8 total)]
# ══════════════════════════════════════════════════════════════════════════════
# DORA META BLOCK — DO NOT EDIT MANUALLY (CI-owned)
# ══════════════════════════════════════════════════════════════════════════════
# __meta__ = {
#     "template_version": "2.6.0",
#     "spec_hash": "SPEC-102d1d3dc34c",
#     "created_at": "2025-12-18T06:25:01.645626+00:00",
#     "created_by": "module_pipeline",
#     "last_updated_at": "2025-12-18T06:25:01.645626+00:00",
#     "last_updated_by": "module_pipeline",
#     "module_id": "twilio.adapter",
#     "file": "schemas.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Twilio Adapter Schemas
──────────────────────
Pydantic models for request/response validation.

Auto-generated from Module-Spec v2.6.0
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class TwilioAdapterRequest(BaseModel):
    """Inbound request schema for Twilio Adapter."""
    
    event_id: Optional[str] = Field(None, description="Unique event identifier for idempotency")
    source: Optional[str] = Field(None, description="Event source identifier")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    payload: dict[str, Any] = Field(default_factory=dict, description="Event payload")
    
    # Attachment support
    attachments: list[dict[str, Any]] = Field(default_factory=list, description="File attachments")
    
    class Config:
        extra = "allow"


class TwilioAdapterResponse(BaseModel):
    """Response schema for Twilio Adapter."""
    
    ok: bool = Field(..., description="Whether the request succeeded")
    packet_id: Optional[str] = Field(None, description="ID of the emitted packet")
    dedupe: bool = Field(False, description="Whether this was a duplicate request")
    error: Optional[str] = Field(None, description="Error message if ok=False")
    data: Optional[dict[str, Any]] = Field(None, description="Response data")


class TwilioAdapterContext(BaseModel):
    """Execution context for Twilio Adapter."""
    
    thread_uuid: UUID = Field(..., description="Deterministic thread UUID")
    source: str = Field("twilio.adapter", description="Source module ID")
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
