"""
Slack Webhook Adapter Routes
────────────────────
FastAPI routes for Slack Webhook Adapter

Auto-generated from Module-Spec v2.6.0
Generated at: 2025-12-18T00:42:30.246168+00:00

Tier: 2
"""

import hmac
import hashlib
import time
import os
import structlog
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel, Field

from api.adapters.slack_adapter.adapters.slack_webhook_adapter import (
    SlackWebhookAdapter,
    SlackWebhookRequest,
)

# Import settings at module level for better testability
try:
    from config.settings import get_integration_settings
except ImportError:
    # Fallback for test environments where config might not be available
    get_integration_settings = None

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/slack", tags=["Slack Webhook Adapter"])


# ══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ══════════════════════════════════════════════════════════════════════════════


class SlackWebhookRequestModel(BaseModel):
    """Request model for Slack Webhook Adapter endpoint."""

    event_id: Optional[str] = Field(None, description="Event identifier")
    source: Optional[str] = Field(None, description="Event source")
    payload: dict = Field(default_factory=dict, description="Event payload")

    # Slack-specific fields
    type: Optional[str] = Field(None, description="Slack event type")
    challenge: Optional[str] = Field(None, description="URL verification challenge")
    team_id: Optional[str] = Field(None, description="Slack team ID")
    event: Optional[dict] = Field(None, description="Nested event data")

    class Config:
        extra = "allow"


class SlackWebhookResponseModel(BaseModel):
    """Response model for Slack Webhook Adapter endpoint."""

    ok: bool
    packet_id: Optional[str] = None
    dedupe: bool = False
    error: Optional[str] = None
    challenge: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# SIGNATURE VERIFICATION
# ══════════════════════════════════════════════════════════════════════════════


def verify_slack_signature(
    body: bytes,
    timestamp: str,
    signature: str,
    signing_secret: Optional[str] = None,
) -> bool:
    """Verify Slack request signature using HMAC-SHA256."""
    # Get signing secret from env if not provided
    if not signing_secret:
        signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        if not signing_secret:
            logger.error(
                "SLACK_SIGNING_SECRET not configured for signature verification"
            )
            return False

    # Check timestamp freshness (5 minutes tolerance)
    try:
        request_timestamp = int(timestamp)
        current_timestamp = int(time.time())
        if abs(current_timestamp - request_timestamp) > 300:
            return False
    except (ValueError, TypeError):
        return False

    # Compute expected signature
    sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    expected_sig = (
        "v0="
        + hmac.new(
            signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
    )

    return hmac.compare_digest(expected_sig, signature)


# ══════════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ══════════════════════════════════════════════════════════════════════════════


async def get_adapter(request: Request) -> SlackWebhookAdapter:
    """Get adapter instance from app state."""
    substrate_service = getattr(request.app.state, "substrate_service", None)
    aios_runtime = getattr(request.app.state, "aios_runtime", None)
    return SlackWebhookAdapter(
        substrate_service=substrate_service,
        aios_runtime_client=aios_runtime,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════


@router.post("/events")
async def handle_slack_webhook(
    request: Request,
    adapter: SlackWebhookAdapter = Depends(get_adapter),
    x_slack_signature: Optional[str] = Header(None, alias="X-Slack-Signature"),
    x_slack_request_timestamp: Optional[str] = Header(
        None, alias="X-Slack-Request-Timestamp"
    ),
) -> SlackWebhookResponseModel:
    """
    Validates Slack events, normalizes to L9 packets, and routes to AIOS reasoning.

    Accepts: JSON
    Returns: JSON
    """
    # Get raw body for signature verification
    body = await request.body()

    # Signature verification
    if not x_slack_signature or not x_slack_request_timestamp:
        raise HTTPException(status_code=401, detail="Missing Slack signature headers")

    # Get signing secret from config or env
    signing_secret = None
    if get_integration_settings:
        try:
            integration_settings = get_integration_settings()
            signing_secret = integration_settings.slack_signing_secret
        except Exception:
            pass

    if not signing_secret:
        signing_secret = os.getenv("SLACK_SIGNING_SECRET")

    if not signing_secret:
        logger.error("SLACK_SIGNING_SECRET not configured")
        raise HTTPException(
            status_code=500, detail="Slack signing secret not configured"
        )

    if not verify_slack_signature(
        body, x_slack_request_timestamp, x_slack_signature, signing_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid Slack signature")

    # Parse body
    import json

    try:
        body_json = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Handle URL verification challenge
    if body_json.get("type") == "url_verification":
        challenge = body_json.get("challenge")
        return SlackWebhookResponseModel(ok=True, challenge=challenge)

    # Convert to Pydantic model
    request_model = SlackWebhookRequestModel(**body_json)

    # Convert Pydantic model to adapter request
    adapter_request = SlackWebhookRequest(
        event_id=request_model.event_id,
        source=request_model.source,
        payload=request_model.payload or request_model.model_dump(),
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
