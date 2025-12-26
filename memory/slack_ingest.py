"""
Slack Event Ingestion: Core handler for Slack messages.

This module implements the orchestration layer:
  1. Dedupe check (prevent double-processing)
  2. Memory context retrieval (fetch thread history + semantic hits)
  3. AIOS /chat call (get AI response)
  4. Slack API response delivery (post message in thread)
  5. Packet persistence (store inbound + outbound in substrate)

Thread model:
  - All Slack messages belong to a thread (identified by deterministic UUID)
  - Thread UUID is generated from team_id:channel_id:thread_ts using UUIDv5
  - Human-readable string stored in metadata for observability
  - Internal operations use UUID for DB consistency

Deduplication:
  - Check event_id in packet metadata before processing
  - If found, return 200 without re-processing
  - Prevents double-replies if Slack retries delivery

Error handling:
  - AIOS call fails: Log error, store error packet, don't crash
  - Slack API call fails: Log error, store error packet, return 200 to Slack
  - Memory persistence fails: Log error, still return 200 to Slack
"""

import json
import httpx
from typing import Any, Dict, Optional
from datetime import datetime
import structlog
from uuid import UUID

from api.slack_adapter import SlackRequestNormalizer
from api.slack_client import SlackAPIClient, SlackClientError
from memory.substrate_models import PacketEnvelopeIn, PacketMetadata, PacketProvenance
from memory.substrate_service import MemorySubstrateService

logger = structlog.get_logger(__name__)


async def handle_slack_events(
    request_body: bytes,
    payload: Dict[str, Any],
    substrate_service: MemorySubstrateService,
    slack_client: SlackAPIClient,
    aios_base_url: str,
) -> Dict[str, Any]:
    """
    Handle Slack event callback.
    
    Args:
        request_body: Raw request body (for audit trail)
        payload: Parsed JSON payload from Slack
        substrate_service: Memory substrate for packet persistence
        slack_client: Slack API client for posting replies
        aios_base_url: Base URL for AIOS service (e.g., http://localhost:8000)
    
    Returns:
        HTTP response dict (always 200 if we make it this far)
    """
    # Parse and normalize event
    normalized = SlackRequestNormalizer.parse_event_callback(payload)
    
    event_id = normalized.get("event_id")
    team_id = normalized.get("team_id")
    channel_id = normalized.get("channel_id")
    thread_ts = normalized.get("thread_ts")
    thread_uuid = normalized.get("thread_uuid")
    thread_string = normalized.get("thread_string")
    user_id = normalized.get("user_id")
    text = normalized.get("text", "")
    event_type = normalized.get("event_type")
    
    logger.info(
        "slack_event_received",
        event_id=event_id,
        event_type=event_type,
        team_id=team_id,
        channel_id=channel_id,
        thread_ts=thread_ts,
        thread_uuid=thread_uuid,
        user_id=user_id,
    )
    
    # Dedupe check: look for event_id in recent packets
    try:
        dedupe_result = await _check_duplicate(
            substrate_service=substrate_service,
            event_id=event_id,
            thread_uuid=thread_uuid,
            team_id=team_id,
            channel_id=channel_id,
            ts=normalized.get("ts"),
            user_id=user_id,
        )
        
        if dedupe_result.get("is_duplicate"):
            logger.info(
                "slack_event_deduplicated",
                event_id=event_id,
                reason=dedupe_result.get("reason"),
            )
            return {"ok": True, "deduplicated": True}
    except Exception as e:
        logger.error("slack_dedupe_check_error", error=str(e), event_id=event_id)
        # Continue processing; dedupe is opportunistic
    
    # Retrieve memory context
    thread_context = {}
    semantic_hits = {}
    
    try:
        thread_context = await _retrieve_thread_context(
            substrate_service=substrate_service,
            thread_uuid=thread_uuid,
            limit=10,
        )
        logger.debug("slack_thread_context_retrieved", context_size=len(thread_context))
    except Exception as e:
        logger.warning("slack_thread_context_retrieval_error", error=str(e), thread_uuid=thread_uuid)
    
    try:
        semantic_hits = await _retrieve_semantic_hits(
            substrate_service=substrate_service,
            query=text,
            team_id=team_id,
            limit=5,
        )
        logger.debug("slack_semantic_hits_retrieved", hit_count=len(semantic_hits))
    except Exception as e:
        logger.warning("slack_semantic_hits_retrieval_error", error=str(e))
    
    # Call AIOS /chat endpoint
    aios_response = None
    aios_error = None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            system_prompt = _build_system_prompt(
                thread_context=thread_context,
                semantic_hits=semantic_hits,
                user_id=user_id,
                channel_id=channel_id,
            )
            
            aios_payload = {
                "message": text,
                "system_prompt": system_prompt,
            }
            
            aios_response_obj = await client.post(
                f"{aios_base_url}/chat",
                json=aios_payload,
            )
            aios_response_obj.raise_for_status()
            aios_response = aios_response_obj.json()
            
            logger.info(
                "aios_chat_success",
                event_id=event_id,
                response_length=len(aios_response.get("reply", "")),
            )
    except httpx.TimeoutException:
        aios_error = "AIOS timeout (10s)"
        logger.error("aios_chat_timeout", event_id=event_id)
    except httpx.HTTPStatusError as e:
        aios_error = f"AIOS HTTP {e.response.status_code}"
        logger.error("aios_chat_http_error", event_id=event_id, status=e.response.status_code)
    except Exception as e:
        aios_error = str(e)
        logger.error("aios_chat_error", event_id=event_id, error=aios_error)
    
    # Store inbound packet
    try:
        inbound_packet_in = PacketEnvelopeIn(
            packet_type="slack.in",
            payload={
                "event_id": event_id,
                "thread_uuid": thread_uuid,
                "thread_string": thread_string,
                "team_id": team_id,
                "channel_id": channel_id,
                "user_id": user_id,
                "text": text,
                "ts": normalized.get("ts"),
                "thread_ts": thread_ts,
            },
            metadata=PacketMetadata(
                schema_version="1.0.1",
                agent="slack_adapter",
            ),
            provenance=PacketProvenance(
                source="slack",
            ),
        )
        
        result = await substrate_service.write_packet(inbound_packet_in)
        logger.debug("slack_inbound_packet_stored", event_id=event_id, packet_id=result.packet_id)
    except Exception as e:
        logger.error("slack_inbound_packet_storage_error", error=str(e), event_id=event_id)
    
    # Prepare outbound response
    reply_text = aios_response.get("reply") if aios_response else None
    
    if not reply_text and aios_error:
        reply_text = "Sorry, I encountered a temporary error. Please try again."
    
    if not reply_text:
        reply_text = "No response generated."
    
    # Post reply to Slack
    slack_ts = None
    slack_error = None
    
    try:
        slack_response = await slack_client.post_message(
            channel=channel_id,
            text=reply_text,
            thread_ts=thread_ts,
            reply_broadcast=False,
        )
        slack_ts = slack_response.get("ts")
        logger.info("slack_reply_posted", event_id=event_id, slack_ts=slack_ts)
    except SlackClientError as e:
        slack_error = str(e)
        logger.error("slack_post_error", event_id=event_id, error=slack_error)
    except Exception as e:
        slack_error = str(e)
        logger.error("slack_post_exception", event_id=event_id, error=slack_error)
    
    # Store outbound packet
    try:
        outbound_packet_in = PacketEnvelopeIn(
            packet_type="slack.out",
            payload={
                "event_id": event_id,
                "thread_uuid": thread_uuid,
                "thread_string": thread_string,
                "team_id": team_id,
                "channel_id": channel_id,
                "user_id": user_id,
                "reply_text": reply_text,
                "slack_ts": slack_ts,
                "aios_error": aios_error,
                "slack_error": slack_error,
            },
            metadata=PacketMetadata(
                schema_version="1.0.1",
                agent="slack_adapter",
            ),
            provenance=PacketProvenance(
                source="aios",
            ),
        )
        
        result = await substrate_service.write_packet(outbound_packet_in)
        logger.debug("slack_outbound_packet_stored", event_id=event_id, packet_id=result.packet_id)
    except Exception as e:
        logger.error("slack_outbound_packet_storage_error", error=str(e), event_id=event_id)
    
    return {"ok": True}


async def handle_slack_commands(
    payload: Dict[str, Any],
    substrate_service: MemorySubstrateService,
    slack_client: SlackAPIClient,
    aios_base_url: str,
) -> Dict[str, Any]:
    """
    Handle Slack slash command (asynchronous follow-up).
    
    Called after returning 200 ACK to Slack.
    
    Args:
        payload: Form-encoded command payload from Slack
        substrate_service: Memory substrate for packet persistence
        slack_client: Slack API client for async reply
        aios_base_url: Base URL for AIOS service
    
    Returns:
        Response (for logging, not sent to Slack)
    """
    normalized = SlackRequestNormalizer.parse_command(payload)
    
    command = normalized.get("command", "")
    text = normalized.get("text", "")
    user_id = normalized.get("user_id", "")
    channel_id = normalized.get("channel_id", "")
    team_id = normalized.get("team_id", "")
    response_url = normalized.get("response_url", "")
    thread_uuid = normalized.get("thread_uuid", "")
    
    logger.info(
        "slack_command_received",
        command=command,
        user_id=user_id,
        channel_id=channel_id,
        text=text[:50],
    )
    
    # Parse command text
    # Format: /l9 do <task> | /l9 email <instruction> | /l9 extract <artifact>
    parts = text.split(None, 1)
    if len(parts) < 2:
        return {
            "response_type": "ephemeral",
            "text": "Usage: /l9 do <task> | /l9 email <instruction> | /l9 extract <artifact>",
        }
    
    subcommand = parts[0].lower()
    full_text = parts[1] if len(parts) > 1 else ""
    
    # Route to AIOS /chat
    aios_response = None
    aios_error = None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            system_prompt = f"User issued command: /{command} {subcommand}"
            aios_payload = {
                "message": full_text,
                "system_prompt": system_prompt,
            }
            
            aios_response_obj = await client.post(
                f"{aios_base_url}/chat",
                json=aios_payload,
            )
            aios_response_obj.raise_for_status()
            aios_response = aios_response_obj.json()
            logger.info("aios_command_success", command=command, subcommand=subcommand)
    except Exception as e:
        aios_error = str(e)
        logger.error("aios_command_error", command=command, error=aios_error)
    
    # Build response
    reply_text = aios_response.get("reply") if aios_response else None
    
    if not reply_text and aios_error:
        reply_text = "Sorry, I encountered an error processing your command."
    
    if not reply_text:
        reply_text = "No response generated."
    
    # Post to response_url or Slack API
    slack_error = None
    
    if response_url:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    response_url,
                    json={
                        "response_type": "in_channel",
                        "text": reply_text,
                    },
                )
            logger.info("slack_command_response_posted_to_url", command=command)
        except Exception as e:
            slack_error = str(e)
            logger.error("slack_command_response_url_error", error=slack_error)
    
    # Store command packet
    try:
        command_packet_in = PacketEnvelopeIn(
            packet_type="slack.command",
            payload={
                "command": command,
                "subcommand": subcommand,
                "full_text": full_text,
                "team_id": team_id,
                "user_id": user_id,
                "channel_id": channel_id,
                "thread_uuid": thread_uuid,
                "aios_error": aios_error,
                "slack_error": slack_error,
            },
            metadata=PacketMetadata(
                schema_version="1.0.1",
                agent="slack_adapter",
            ),
            provenance=PacketProvenance(
                source="slack",
            ),
        )
        
        result = await substrate_service.write_packet(command_packet_in)
        logger.debug("slack_command_packet_stored", packet_id=result.packet_id)
    except Exception as e:
        logger.error("slack_command_packet_storage_error", error=str(e))
    
    return {"ok": True}


# ============================================================================
# Helper Functions
# ============================================================================

async def _check_duplicate(
    substrate_service: MemorySubstrateService,
    event_id: str,
    thread_uuid: str,
    team_id: str,
    channel_id: str,
    ts: str,
    user_id: str,
) -> Dict[str, Any]:
    """
    Check if event already processed.
    
    Returns dedupe result with is_duplicate, reason.
    
    TODO: In production, this would query packet_store with:
          WHERE payload->>'event_id' = ? OR
                (metadata->>'team_id' = ? AND channel_id = ? AND ts = ? AND user_id = ?)
    """
    try:
        # For now, return no duplicate (real implementation deferred to DAG/repo)
        # This is a stub that can be implemented when query methods are available
        return {"is_duplicate": False}
    except Exception as e:
        logger.error("dedupe_check_error", error=str(e))
        return {"is_duplicate": False, "reason": "dedupe_check_failed"}


async def _retrieve_thread_context(
    substrate_service: MemorySubstrateService,
    thread_uuid: str,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Retrieve recent packets in thread (thread context).
    
    Queries packet_store for packets matching the thread_uuid.
    """
    try:
        packets = await substrate_service.search_packets_by_thread(
            thread_id=thread_uuid,
            limit=limit,
        )
        return {"packets": packets}
    except Exception as e:
        logger.error("thread_context_retrieval_error", error=str(e), thread_uuid=thread_uuid)
        # Log to error telemetry (non-blocking)
        try:
            from core.error_tracking import log_error_to_graph
            import asyncio
            asyncio.create_task(log_error_to_graph(
                error=e,
                context={"thread_uuid": thread_uuid, "limit": limit},
                source="memory.slack_ingest.thread_context",
            ))
        except ImportError:
            pass
        return {"packets": [], "error": str(e)}


async def _retrieve_semantic_hits(
    substrate_service: MemorySubstrateService,
    query: str,
    team_id: str,
    limit: int = 5,
) -> Dict[str, Any]:
    """
    Retrieve semantically similar packets.
    
    Calls substrate_service.semantic_search for vector similarity search.
    """
    from memory.substrate_models import SemanticSearchRequest
    
    try:
        request = SemanticSearchRequest(
            query=query,
            top_k=limit,
            agent_id=team_id,
        )
        result = await substrate_service.semantic_search(request)
        return {
            "results": [
                {
                    "embedding_id": str(hit.embedding_id),
                    "score": hit.score,
                    "payload": hit.payload,
                }
                for hit in result.hits
            ]
        }
    except Exception as e:
        logger.error("semantic_search_error", error=str(e), query=query[:100], team_id=team_id)
        # Log to error telemetry (non-blocking)
        try:
            from core.error_tracking import log_error_to_graph
            import asyncio
            asyncio.create_task(log_error_to_graph(
                error=e,
                context={"query": query[:100], "team_id": team_id, "limit": limit},
                source="memory.slack_ingest.semantic_search",
            ))
        except ImportError:
            pass
        return {"results": [], "error": str(e)}


def _build_system_prompt(
    thread_context: Dict[str, Any],
    semantic_hits: Dict[str, Any],
    user_id: str,
    channel_id: str,
) -> str:
    """
    Build system prompt that includes thread context and semantic hits.
    
    This gives the AIOS model context about the conversation thread and
    any related prior knowledge from the memory substrate.
    """
    parts = [
        "You are an AI assistant integrated with Slack. Respond helpfully and concisely.",
        f"User ID: {user_id}",
        f"Channel: {channel_id}",
    ]
    
    if thread_context and thread_context.get("packets"):
        parts.append("\nRecent thread context:")
        for item in thread_context.get("packets", [])[:5]:
            content = item.get("payload", {}).get("text", "")[:200]
            if content:
                parts.append(f"  - {content}")
    
    if semantic_hits and semantic_hits.get("results"):
        parts.append("\nRelated knowledge:")
        for item in semantic_hits.get("results", [])[:3]:
            content = item.get("payload", {}).get("text", "")[:200]
            if content:
                parts.append(f"  - {content}")
    
    return "\n".join(parts)

