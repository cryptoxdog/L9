# ══════════════════════════════════════════════════════════════════════════════
# Generated from Module-Spec v2.6
# module_id: slack.webhook
# enforced_acceptance: ["valid_request_processed", "idempotent_replay_cached", "stale_timestamp_rejected", "aios_response_forwarded", "packet_written_on_success", ... (6 total)]
# ══════════════════════════════════════════════════════════════════════════════
# DORA META BLOCK — DO NOT EDIT MANUALLY (CI-owned)
# ══════════════════════════════════════════════════════════════════════════════
# __meta__ = {
#     "template_version": "2.6.0",
#     "spec_hash": "SPEC-slack-webhook",
#     "created_at": "2025-12-20T00:00:00.000000+00:00",
#     "created_by": "module_pipeline",
#     "last_updated_at": "2025-12-20T00:00:00.000000+00:00",
#     "last_updated_by": "module_pipeline",
#     "module_id": "slack.webhook",
#     "file": "schemas.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Slack Webhook Adapter Schemas
─────────────────────────────
Pydantic models for request/response validation.

Auto-generated from Module-Spec v2.6.0
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class SlackWebhookRequest(BaseModel):
    """Inbound request schema for Slack Webhook Adapter."""

    event_id: Optional[str] = Field(
        None, description="Unique event identifier for idempotency"
    )
    source: Optional[str] = Field(None, description="Event source identifier")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    payload: dict[str, Any] = Field(default_factory=dict, description="Event payload")

    # Slack-specific fields
    type: Optional[str] = Field(
        None,
        description="Slack event type (e.g., 'event_callback', 'url_verification')",
    )
    challenge: Optional[str] = Field(
        None, description="URL verification challenge from Slack"
    )
    team_id: Optional[str] = Field(None, description="Slack team/workspace ID")
    event: Optional[dict[str, Any]] = Field(
        None, description="Nested event data from Slack"
    )

    class Config:
        extra = "allow"


class SlackWebhookResponse(BaseModel):
    """Response schema for Slack Webhook Adapter."""

    ok: bool = Field(..., description="Whether the request succeeded")
    packet_id: Optional[str] = Field(None, description="ID of the emitted packet")
    dedupe: bool = Field(False, description="Whether this was a duplicate request")
    error: Optional[str] = Field(None, description="Error message if ok=False")
    challenge: Optional[str] = Field(
        None, description="Challenge response for URL verification"
    )
    data: Optional[dict[str, Any]] = Field(None, description="Response data")


class SlackWebhookContext(BaseModel):
    """Execution context for Slack Webhook Adapter."""

    thread_uuid: UUID = Field(..., description="Deterministic thread UUID")
    source: str = Field("slack.webhook", description="Source module ID")
    task_id: Optional[str] = Field(None, description="Task identifier")
    tool_id: Optional[str] = Field(None, description="Tool identifier")
    channel_id: Optional[str] = Field(None, description="Slack channel ID")
    user_id: Optional[str] = Field(None, description="Slack user ID")

    class Config:
        frozen = True


class PacketPayload(BaseModel):
    """Standard packet payload structure."""

    request: Optional[dict[str, Any]] = None
    response: Optional[dict[str, Any]] = None
    error: Optional[dict[str, str]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
