# ══════════════════════════════════════════════════════════════════════════════
# Generated from Module-Spec v2.6
# module_id: calendar.adapter
# enforced_acceptance: ["valid_event_processed", "idempotent_replay_cached", "event_created_successfully", "event_updated_successfully", "aios_response_forwarded", ... (8 total)]
# ══════════════════════════════════════════════════════════════════════════════
# DORA META BLOCK — DO NOT EDIT MANUALLY (CI-owned)
# ══════════════════════════════════════════════════════════════════════════════
# __meta__ = {
#     "template_version": "2.6.0",
#     "spec_hash": "SPEC-447dc3be62b3",
#     "created_at": "2025-12-18T06:25:16.899340+00:00",
#     "created_by": "module_pipeline",
#     "last_updated_at": "2025-12-18T06:25:16.899340+00:00",
#     "last_updated_by": "module_pipeline",
#     "module_id": "calendar.adapter",
#     "file": "schemas.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Calendar Adapter Schemas
────────────────────────
Pydantic models for request/response validation.

Auto-generated from Module-Spec v2.6.0
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class CalendarAdapterRequest(BaseModel):
    """Inbound request schema for Calendar Adapter."""
    
    event_id: Optional[str] = Field(None, description="Unique event identifier for idempotency")
    source: Optional[str] = Field(None, description="Event source identifier")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    payload: dict[str, Any] = Field(default_factory=dict, description="Event payload")
    
    # Attachment support
    attachments: list[dict[str, Any]] = Field(default_factory=list, description="File attachments")
    
    class Config:
        extra = "allow"


class CalendarAdapterResponse(BaseModel):
    """Response schema for Calendar Adapter."""
    
    ok: bool = Field(..., description="Whether the request succeeded")
    packet_id: Optional[str] = Field(None, description="ID of the emitted packet")
    dedupe: bool = Field(False, description="Whether this was a duplicate request")
    error: Optional[str] = Field(None, description="Error message if ok=False")
    data: Optional[dict[str, Any]] = Field(None, description="Response data")


class CalendarAdapterContext(BaseModel):
    """Execution context for Calendar Adapter."""
    
    thread_uuid: UUID = Field(..., description="Deterministic thread UUID")
    source: str = Field("calendar.adapter", description="Source module ID")
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
