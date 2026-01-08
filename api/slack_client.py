"""
Slack API Client: Async wrapper for posting messages back to Slack.

This module provides a thin async wrapper around the Slack Web API
for posting messages (chat.postMessage) with full thread support.

It is NOT a full Slack SDK; it only implements the subset needed for
the L9 Slack adapter:
  - chat.postMessage (reply in thread)
  - Basic error handling
  - No connection pooling (relies on httpx at app level)
"""

import httpx
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)

SLACK_API_BASE = "https://slack.com/api"
SLACK_CHAT_POST_MESSAGE_ENDPOINT = f"{SLACK_API_BASE}/chat.postMessage"


class SlackClientError(Exception):
    """Raised when Slack API call fails."""

    pass


class SlackAPIClient:
    """
    Async Slack API client for posting messages.

    Requires shared httpx client (not owned by this class).

    Usage:
        client = SlackAPIClient(bot_token="xoxb-...", http_client=shared_httpx_client)
        await client.post_message(
            channel="C123",
            text="Hello",
            thread_ts="1234567890.123456"
        )
    """

    def __init__(self, bot_token: str, http_client: httpx.AsyncClient):
        """
        Args:
            bot_token: Slack bot token (from Settings > Install App)
            http_client: Shared httpx.AsyncClient (managed by app lifespan)
        """
        if not bot_token or not bot_token.strip():
            raise ValueError("SLACK_BOT_TOKEN is required and cannot be empty")
        if not http_client:
            raise ValueError("http_client (httpx.AsyncClient) is required")

        self.bot_token = bot_token
        self.http_client = http_client

    async def post_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None,
        blocks: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
        reply_broadcast: bool = False,
    ) -> Dict[str, Any]:
        """
        Post a message to Slack.

        Args:
            channel: Channel ID (C...) or user ID (U...)
            text: Plain text message content
            thread_ts: Optional; if provided, post as reply in thread
            blocks: Optional; rich formatting blocks (Block Kit)
            metadata: Optional; message metadata (for searchability)
            reply_broadcast: If True and thread_ts provided, also post to channel

        Returns:
            Slack API response dict:
              {
                "ok": true,
                "channel": "C...",
                "ts": "1234567890.123456",
                "message": {...}
              }

        Raises:
            SlackClientError: If API call fails

        Note: httpx.AsyncClient.post() returns a Response directly (not an async context manager).
        """
        payload = {
            "channel": channel,
            "text": text,
        }

        if blocks:
            payload["blocks"] = blocks

        if thread_ts:
            payload["thread_ts"] = thread_ts
            payload["reply_broadcast"] = reply_broadcast

        if metadata:
            payload["metadata"] = metadata

        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json",
        }

        try:
            # httpx.AsyncClient.post() returns Response directly (not async context manager)
            resp = await self.http_client.post(
                SLACK_CHAT_POST_MESSAGE_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=10.0,
            )
            resp.raise_for_status()

            response_data = resp.json()

            if not response_data.get("ok"):
                error = response_data.get("error", "unknown error")
                raise SlackClientError(f"Slack API error: {error}")

            logger.info(
                "slack_message_posted",
                channel=channel,
                ts=response_data.get("ts"),
                thread_ts=thread_ts,
            )

            return response_data

        except httpx.TimeoutException:
            raise SlackClientError("Slack API request timed out (10s)")
        except httpx.HTTPStatusError as e:
            raise SlackClientError(
                f"Slack API HTTP error {e.response.status_code}: {e}"
            )
        except Exception as e:
            raise SlackClientError(f"HTTP error posting to Slack: {e}")

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "API-OPER-005",
    "component_name": "Slack Client",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:13Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "api_gateway",
    "type": "service",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Provides slack client components including SlackClientError, SlackAPIClient",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
