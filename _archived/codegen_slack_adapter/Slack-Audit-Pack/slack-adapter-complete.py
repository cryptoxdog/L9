"""
Slack Webhook Adapter - Production Ready
L9 Memory Substrate Integration
https://github.com/l9-os/slack-adapter

MODELS USED (from repo ground truth):
- PacketEnvelopeIn: memory.substratemodels
- PacketWriteResult: memory.substratemodels
- MemorySubstrateService: memory.substrateservice
- PacketMetadata, PacketProvenance: memory.substratemodels
"""

import hashlib
import hmac
import json
import structlog
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4, uuid5, NAMESPACE_DNS

import httpx
import structlog
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field

from memory.substratemodels import (
    PacketEnvelopeIn,
    PacketMetadata,
    PacketProvenance,
    PacketWriteResult,
)
from memory.substrateservice import MemorySubstrateService

logger = structlog.get_logger(__name__)


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================


class SlackWebhookRequest(BaseModel):
    """Inbound Slack webhook request model."""

    type: str = Field(..., description="Event type: url_verification, event_callback")
    challenge: Optional[str] = Field(None, description="Challenge token for URL verification")
    team_id: Optional[str] = Field(None, description="Slack workspace ID")
    event_id: Optional[str] = Field(None, description="Unique event ID")
    event: Optional[Dict[str, Any]] = Field(None, description="Event payload")
    event_ts: Optional[str] = Field(None, description="Event timestamp")


class SlackWebhookResponse(BaseModel):
    """Response model for Slack webhook endpoint."""

    ok: bool = Field(True, description="Success status")
    challenge: Optional[str] = Field(None, description="Echo back challenge token")
    message: Optional[str] = Field(None, description="Status message")


# ============================================================================
# SIGNATURE VERIFICATION
# ============================================================================


class SlackSignatureVerifier:
    """
    Verifies Slack request signatures per:
    https://api.slack.com/authentication/verifying-requests-from-slack
    """

    def __init__(self, signing_secret: str):
        """Initialize with Slack app signing secret."""
        self.signing_secret = signing_secret

    def verify(self, timestamp: str, body: bytes, signature: str) -> bool:
        """
        Verify request signature.

        Args:
            timestamp: X-Slack-Request-Timestamp header
            body: Raw request body
            signature: X-Slack-Signature header (format: v0=<hash>)

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Check timestamp is recent (within 5 minutes)
            try:
                ts_int = int(timestamp)
            except (ValueError, TypeError):
                logger.warning("invalid_timestamp_format", timestamp=timestamp)
                return False

            if abs(time.time() - ts_int) > 300:
                logger.warning("stale_timestamp", age_seconds=abs(time.time() - ts_int))
                return False

            # Compute expected signature
            sig_basestring = f"v0:{timestamp}:{body.decode()}"
            computed_signature = (
                "v0="
                + hmac.new(
                    self.signing_secret.encode(),
                    sig_basestring.encode(),
                    hashlib.sha256,
                ).hexdigest()
            )

            # Compare signatures (constant-time)
            is_valid = hmac.compare_digest(computed_signature, signature)
            if not is_valid:
                logger.warning("signature_verification_failed")
            return is_valid

        except Exception as e:
            logger.error("signature_verification_error", error=str(e))
            return False


# ============================================================================
# EVENT NORMALIZATION
# ============================================================================


class SlackEventNormalizer:
    """Normalizes Slack events to L9 packet format."""

    def __init__(self, workspace_id: str = "slack"):
        """Initialize normalizer."""
        self.workspace_id = workspace_id

    def generate_thread_uuid(
        self, team_id: str, channel_id: str, thread_ts: str
    ) -> str:
        """
        Generate deterministic UUIDv5 for thread.

        Uses Slack team_id + channel_id + thread_ts to ensure same
        thread always maps to same UUID (required for idempotency).
        """
        namespace_str = f"{self.workspace_id}:{team_id}:{channel_id}"
        return str(uuid5(NAMESPACE_DNS, f"{namespace_str}#{thread_ts}"))

    def parse_event_callback(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Slack event_callback to normalized event.

        Returns:
            Normalized event dict or None if unsupported event type.
        """
        try:
            event = payload.get("event", {})
            event_type = event.get("type", "unknown")

            # Only handle message events for now
            if event_type not in ("message", "app_mention"):
                logger.info("unsupported_event_type", event_type=event_type)
                return None

            return {
                "type": event_type,
                "user": event.get("user", "unknown"),
                "channel": event.get("channel", "unknown"),
                "text": event.get("text", ""),
                "ts": event.get("ts", ""),
                "thread_ts": event.get("thread_ts"),
                "team_id": payload.get("team_id", "unknown"),
            }

        except Exception as e:
            logger.error("parse_event_callback_error", error=str(e))
            return None


# ============================================================================
# DEDUPLICATION
# ============================================================================


class DuplicateDetector:
    """Detects duplicate Slack events using substrate memory."""

    def __init__(self, substrate_service: MemorySubstrateService):
        """Initialize with substrate service."""
        self.substrate = substrate_service

    async def is_duplicate(self, event_id: str) -> bool:
        """
        Check if event_id has been seen before.

        Args:
            event_id: Slack event ID

        Returns:
            True if event is duplicate, False if new
        """
        try:
            # CRITICAL: search_packets is ASYNC and returns list directly
            packets = await self.substrate.search_packets(
                metadata_filter={"slack_event_id": event_id},
                limit=1,
            )
            # packets is already a list, don't await again
            return len(packets) > 0

        except Exception as e:
            logger.error("deduplication_check_error", event_id=event_id, error=str(e))
            # On error, assume not duplicate (fail-open)
            return False


# ============================================================================
# MAIN ADAPTER
# ============================================================================


class SlackWebhookAdapter:
    """
    Slack webhook adapter for L9 memory substrate.

    Receives Slack events, validates signatures, deduplicates,
    and writes to memory substrate as PacketEnvelopeIn.
    """

    def __init__(
        self,
        signing_secret: str,
        substrate_service: MemorySubstrateService,
        workspace_id: str = "slack",
    ):
        """
        Initialize adapter.

        Args:
            signing_secret: Slack app signing secret
            substrate_service: Memory substrate service
            workspace_id: Identifier for this Slack workspace
        """
        self.verifier = SlackSignatureVerifier(signing_secret)
        self.normalizer = SlackEventNormalizer(workspace_id)
        self.substrate_service = substrate_service
        self.duplicate_detector = DuplicateDetector(substrate_service)
        self.workspace_id = workspace_id

    async def handle_webhook(self, request: Request) -> Tuple[int, Dict[str, Any]]:
        """
        Handle incoming Slack webhook.

        Args:
            request: FastAPI Request object

        Returns:
            Tuple of (status_code, response_dict)
        """
        # Read raw body
        raw_body = await request.body()
        signature = request.headers.get("x-slack-signature", "")
        timestamp = request.headers.get("x-slack-request-timestamp", "")

        # Verify signature
        if not self.verifier.verify(timestamp, raw_body, signature):
            logger.warning("signature_verification_failed")
            return 401, {"error": "unauthorized"}

        # Parse JSON
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            logger.warning("invalid_json_payload")
            return 400, {"error": "bad request"}

        # Handle URL verification challenge
        if payload.get("type") == "url_verification":
            return 200, {"challenge": payload.get("challenge", "")}

        # Handle event callback
        if payload.get("type") == "event_callback":
            return await self._handle_event_callback(payload)

        # Unknown type
        logger.info("unknown_payload_type", payload_type=payload.get("type"))
        return 200, {"ok": True}

    async def _handle_event_callback(
        self, callback_data: Dict[str, Any]
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Process event_callback payload.

        Args:
            callback_data: The event_callback payload

        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            event_id = callback_data.get("event_id", "unknown")
            team_id = callback_data.get("team_id", "unknown")

            # Check for duplicate
            is_dup = await self.duplicate_detector.is_duplicate(event_id)
            if is_dup:
                logger.info("duplicate_event_skipped", event_id=event_id)
                return 200, {"ok": True}

            # Parse event
            event = self.normalizer.parse_event_callback(callback_data)
            if event is None:
                return 200, {"ok": True}

            # Generate deterministic thread UUID
            thread_ts = event.get("thread_ts") or event.get("ts")
            thread_uuid = self.normalizer.generate_thread_uuid(
                team_id, event.get("channel"), thread_ts
            )

            # Create packet (CORRECT: using real models)
            packet_in = PacketEnvelopeIn(
                packet_type="slack.in",
                payload={
                    "text": event.get("text", ""),
                    "user": event.get("user", ""),
                    "channel": event.get("channel", ""),
                    "event_type": event.get("type", ""),
                },
                metadata=PacketMetadata(
                    agent="slack-webhook-adapter",
                    domain="slack",
                ),
                provenance=PacketProvenance(
                    source="slack",
                ),
                thread_id=thread_uuid,
                tags=["slack", "inbound", event.get("type", "message")],
            )

            # Write to substrate (CRITICAL: write_packet is async)
            result: PacketWriteResult = await self.substrate_service.write_packet(
                packet_in
            )

            logger.info(
                "packet_stored",
                packet_type="slack.in",
                packet_id=result.packet_id,
                event_id=event_id,
                thread_id=thread_uuid,
            )

            return 200, {"ok": True}

        except Exception as e:
            logger.error("handle_event_callback_error", error=str(e))
            return 200, {"ok": True}  # Always return 200 to Slack


# ============================================================================
# FASTAPI ROUTE
# ============================================================================


def create_slack_router(
    substrate_service: MemorySubstrateService,
    signing_secret: str,
    workspace_id: str = "slack",
) -> APIRouter:
    """
    Create FastAPI router for Slack webhook.

    Args:
        substrate_service: Memory substrate service (from app.state)
        signing_secret: Slack app signing secret (from env)
        workspace_id: Slack workspace identifier

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/webhooks/slack", tags=["slack"])
    adapter = SlackWebhookAdapter(signing_secret, substrate_service, workspace_id)

    @router.post("/events", response_model=SlackWebhookResponse)
    async def handle_slack_webhook(request: Request) -> Dict[str, Any]:
        """
        Slack Events API webhook endpoint.

        POST /webhooks/slack/events

        Returns:
            SlackWebhookResponse with ok=true or challenge token
        """
        status_code, response = await adapter.handle_webhook(request)

        if status_code != 200:
            raise HTTPException(status_code=status_code, detail=response)

        return response

    return router


# ============================================================================
# USAGE IN MAIN APP
# ============================================================================

"""
In your main FastAPI app (api/server.py):

    from slack_webhook_adapter import create_slack_router
    import os

    app = FastAPI()

    # At startup, get the substrate service
    @app.on_event("startup")
    async def startup():
        app.state.substrate_service = ... # initialize from lifespan
        signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        workspace_id = os.getenv("SLACK_WORKSPACE_ID", "slack")

        # Mount Slack router
        slack_router = create_slack_router(
            app.state.substrate_service,
            signing_secret,
            workspace_id
        )
        app.include_router(slack_router)
"""
