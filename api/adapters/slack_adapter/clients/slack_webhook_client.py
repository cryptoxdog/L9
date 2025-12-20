"""
Slack Webhook Adapter Client
────────────────────
External API client for Slack Webhook Adapter

Auto-generated from Module-Spec v2.6.0
Generated at: 2025-12-18T00:42:30.246168+00:00
"""

import structlog
import httpx
from typing import Optional
from dataclasses import dataclass

logger = structlog.get_logger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRIES = 3


# ══════════════════════════════════════════════════════════════════════════════
# CLIENT CLASS
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class SlackWebhookClientConfig:
    """Client configuration."""
    base_url: str
    api_key: Optional[str] = None
    timeout: float = DEFAULT_TIMEOUT
    retries: int = DEFAULT_RETRIES


class SlackWebhookClient:
    """
    External API client for Slack Webhook Adapter.

    Uses httpx for async HTTP operations.
    """

    def __init__(self, config: SlackWebhookClientConfig):
        """Initialize client with configuration."""
        self.config = config
        self.logger = structlog.get_logger(__name__)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "SlackWebhookClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=self._get_headers(),
        )
        return self

    async def __aexit__(self, *args) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
    ) -> dict:
        """Make HTTP request with retry logic."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        last_error = None
        for attempt in range(self.config.retries):
            try:
                response = await self._client.request(
                    method=method,
                    url=endpoint,
                    json=data,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                last_error = e
                self.logger.warning(
                    "request_failed",
                    attempt=attempt + 1,
                    status=e.response.status_code,
                )
                if e.response.status_code < 500:
                    raise
            except httpx.RequestError as e:
                last_error = e
                self.logger.warning(
                    "request_error",
                    attempt=attempt + 1,
                    error=str(e),
                )

        raise last_error or RuntimeError("Request failed after retries")

    # ──────────────────────────────────────────────────────────────────────────
    # API METHODS
    # ──────────────────────────────────────────────────────────────────────────

    async def aios_runtime_call(self, data: dict) -> dict:
        """Call aios_runtime_call endpoint."""
        return await self._request("POST", "/chat", data)

    async def memory_service_call(self, data: dict) -> dict:
        """Call memory_service_call endpoint."""
        return await self._request("POST", "/memory/ingest", data)

    async def slack_chat_postMessage(self, data: dict) -> dict:
        """Call slack_chat_postMessage endpoint."""
        return await self._request("POST", "https://slack.com/api/chat.postMessage", data)

