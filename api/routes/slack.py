"""
Slack HTTP Routes: FastAPI endpoints for Slack webhook integration.

Routes:
  POST /slack/events  - Slack Events API webhook
  POST /slack/commands - Slack slash command handler

Both endpoints:
  1. Validate Slack signature (HMAC-SHA256)
  2. Parse request body (JSON or form)
  3. Route to handler (orchestration layer)
  4. Return appropriate response
  5. Log all events for observability

Error handling:
  - Invalid signature: 401 Unauthorized (fail-closed)
  - Invalid JSON/form: 400 Bad Request
  - Internal error: 200 OK with error logged (downstream failures shouldn't break Slack flow)

Note: Dependencies are injected (no env reads at import time).
"""

import json
from typing import Dict, Any
from fastapi import APIRouter, Request, Header, HTTPException, Depends
import structlog
from time import time as current_time

from api.slack_adapter import SlackRequestValidator, SlackRequestNormalizer
from memory.slack_ingest import handle_slack_events, handle_slack_commands

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/slack", tags=["slack"])


# Dependency injection for validator (injected at app startup)
async def get_slack_validator(request: Request) -> SlackRequestValidator:
    """Retrieve validator from app state."""
    validator = request.app.state.slack_validator
    if not validator:
        raise HTTPException(status_code=500, detail="Slack validator not initialized")
    return validator


@router.post("/events")
async def slack_events(
    request: Request,
    validator: SlackRequestValidator = Depends(get_slack_validator),
    x_slack_signature: str = Header(None),
    x_slack_request_timestamp: str = Header(None),
) -> Dict[str, Any]:
    """
    Slack Events API webhook handler.
    
    Handles:
      - url_verification: Echoes challenge (Slack handshake)
      - event_callback: Processes app_mention and message events
    
    Flow:
      1. Validate Slack signature
      2. Check for url_verification (respond with challenge)
      3. Parse event_callback
      4. Normalize provenance and thread context
      5. Dedupe check (prevent double-processing)
      6. Call AIOS /chat endpoint
      7. Post reply back to Slack in thread
      8. Store inbound/outbound packets in memory substrate
    
    Security:
      - Signature verification is mandatory (fail-closed)
      - Invalid signatures return 401, no further processing
      - Timestamp freshness validated (300s tolerance)
    
    Idempotency:
      - Primary key: event_id
      - Fallback: team_id + channel_id + ts + user_id
      - Duplicate events: return 200 ack, no re-processing
    
    Error handling:
      - Invalid signature: 401 Unauthorized
      - Invalid JSON: 400 Bad Request
      - Internal errors: 200 OK (swallow Slack-side to prevent redelivery loop)
    """
    start_time = current_time()
    
    # Get raw request body
    request_body = await request.body()
    
    # Validate Slack signature
    try:
        is_valid, error_reason = validator.verify(
            request_body,
            x_slack_request_timestamp,
            x_slack_signature,
        )
        if not is_valid:
            logger.warning(
                "slack_signature_verification_failed",
                error=error_reason,
                timestamp=x_slack_request_timestamp,
            )
            raise HTTPException(status_code=401, detail="Unauthorized")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("slack_signature_verification_error", error=str(e))
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Parse JSON payload
    try:
        payload = json.loads(request_body)
    except json.JSONDecodeError as e:
        logger.warning("slack_invalid_json", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Handle url_verification (Slack handshake during setup)
    if payload.get("type") == "url_verification":
        challenge = payload.get("challenge", "")
        logger.info("slack_url_verification_challenge", challenge=challenge[:20])
        return {"challenge": challenge}
    
    # Route to handler
    try:
        # Inject dependencies
        substrate_service = request.app.state.substrate_service
        slack_client = request.app.state.slack_client
        aios_base_url = request.app.state.aios_base_url
        
        result = await handle_slack_events(
            request_body=request_body,
            payload=payload,
            substrate_service=substrate_service,
            slack_client=slack_client,
            aios_base_url=aios_base_url,
        )
        
        elapsed_ms = (current_time() - start_time) * 1000
        logger.info(
            "slack_events_processed",
            event_id=payload.get("event_id"),
            event_type=payload.get("event", {}).get("type"),
            elapsed_ms=elapsed_ms,
        )
        return result
    except Exception as e:
        elapsed_ms = (current_time() - start_time) * 1000
        logger.error(
            "slack_events_handler_error",
            error=str(e),
            event_id=payload.get("event_id"),
            elapsed_ms=elapsed_ms,
        )
        # Return 200 to prevent Slack redelivery, but log error for investigation
        return {"ok": True, "error_logged": True}


@router.post("/commands")
async def slack_commands(
    request: Request,
    validator: SlackRequestValidator = Depends(get_slack_validator),
    x_slack_signature: str = Header(None),
    x_slack_request_timestamp: str = Header(None),
) -> Dict[str, Any]:
    """
    Slack slash command handler.
    
    Handles custom /l9 commands:
      - /l9 do <task> - Execute a task
      - /l9 email <instruction> - Email operation
      - /l9 extract <artifact> - Extract data from artifact
    
    Flow:
      1. Validate Slack signature
      2. Parse form-encoded command payload
      3. Return 200 ACK immediately (< 3 second requirement)
      4. Async: Normalize provenance
      5. Async: Call AIOS /chat endpoint
      6. Async: Post reply to response_url or Slack API
      7. Async: Store inbound/outbound packets
    
    Note: Commands have a response_url which is valid for 3 seconds.
          We return immediately with 200 ACK, then async reply.
    
    Error handling:
      - Invalid signature: 401
      - Invalid command: 200 with error message
      - AIOS failure: 200 with temporary failure message
    """
    start_time = current_time()
    
    # Get raw request body
    request_body = await request.body()
    
    # Validate Slack signature
    try:
        is_valid, error_reason = validator.verify(
            request_body,
            x_slack_request_timestamp,
            x_slack_signature,
        )
        if not is_valid:
            logger.warning(
                "slack_signature_verification_failed",
                error=error_reason,
                timestamp=x_slack_request_timestamp,
            )
            raise HTTPException(status_code=401, detail="Unauthorized")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("slack_signature_verification_error", error=str(e))
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Parse form-encoded payload
    try:
        form_data = await request.form()
        payload = {k: v for k, v in form_data.items()}
    except Exception as e:
        logger.warning("slack_invalid_form_data", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid form data")
    
    # Inject dependencies
    substrate_service = request.app.state.substrate_service
    slack_client = request.app.state.slack_client
    aios_base_url = request.app.state.aios_base_url
    
    # Return 200 ACK immediately (Slack requires response < 3 seconds)
    # Then process async in background
    
    async def process_command_async():
        """Process command asynchronously after returning ACK."""
        try:
            result = await handle_slack_commands(
                payload=payload,
                substrate_service=substrate_service,
                slack_client=slack_client,
                aios_base_url=aios_base_url,
            )
            elapsed_ms = (current_time() - start_time) * 1000
            logger.info(
                "slack_commands_processed",
                command=payload.get("command"),
                user_id=payload.get("user_id"),
                elapsed_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = (current_time() - start_time) * 1000
            logger.error(
                "slack_commands_handler_error",
                error=str(e),
                command=payload.get("command"),
                elapsed_ms=elapsed_ms,
            )
    
    # Schedule async task (Fire and forget, but logged)
    import asyncio
    asyncio.create_task(process_command_async())
    
    # Return immediate ACK (200 < 3 seconds)
    return {
        "response_type": "ephemeral",
        "text": "Processing your command...",
    }

