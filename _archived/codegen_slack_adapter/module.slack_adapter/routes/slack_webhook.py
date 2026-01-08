"""
Slack Webhook Adapter Routes
────────────────────
FastAPI routes for Slack Webhook Adapter

Auto-generated from Module-Spec v2.6.0
Generated at: 2025-12-18T00:42:30.246168+00:00

Tier: 2
"""

import structlog
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from typing import Optional, Any
from pydantic import BaseModel, Field

from api.adapters.slack_webhook_adapter import (
    SlackWebhookAdapter,
    SlackWebhookRequest,
    SlackWebhookResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/slack/webhook", tags=["Slack Webhook Adapter"])


# ══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ══════════════════════════════════════════════════════════════════════════════


class SlackWebhookRequestModel(BaseModel):
    """Request model for Slack Webhook Adapter endpoint."""
    event_id: Optional[str] = Field(None, description="Event identifier")
    source: Optional[str] = Field(None, description="Event source")
    payload: dict = Field(default_factory=dict, description="Event payload")

    class Config:
        extra = "allow"


class SlackWebhookResponseModel(BaseModel):
    """Response model for Slack Webhook Adapter endpoint."""
    ok: bool
    packet_id: Optional[str] = None
    dedupe: bool = False
    error: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ══════════════════════════════════════════════════════════════════════════════


async def get_adapter(request: Request) -> SlackWebhookAdapter:
    """Get adapter instance from app state."""
    substrate_service = getattr(request.app.state, "substrate_service", None)
    return SlackWebhookAdapter(
        substrate_service=substrate_service,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════


@router.post("/slack/events")
async def handle_slack_webhook(
    request: Request,
    body: SlackWebhookRequestModel,
    adapter: SlackWebhookAdapter = Depends(get_adapter),
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    x_timestamp: Optional[str] = Header(None, alias="X-Timestamp"),
) -> SlackWebhookResponseModel:
    """
    Validates Slack events, normalizes to L9 packets, and routes to AIOS reasoning.

    Accepts: JSON
    Returns: JSON
    """
    # Signature verification
    if not x_signature or not x_timestamp:
        raise HTTPException(status_code=401, detail="Missing signature headers")

    # TODO: Implement HMAC-SHA256 verification
    # from api.auth import verify_signature
    # if not verify_signature(body, x_signature, x_timestamp):
    #     raise HTTPException(status_code=401, detail="Invalid signature")

    # Convert Pydantic model to adapter request
    adapter_request = SlackWebhookRequest(
        **body.model_dump()
    )

    # Execute handler
    response = await adapter.handle(adapter_request)

    return SlackWebhookResponseModel(
        ok=response.ok,
        packet_id=str(response.packet_id) if response.packet_id else None,
        dedupe=response.dedupe,
        error=response.error,
    )


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "module": "slack.webhook"}
