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
#     "file": "tests/test_slack_webhook_integration.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Slack Webhook Adapter Integration Tests
────────────────────────────────────────
Integration tests for Slack Webhook Adapter routes

Auto-generated from Module-Spec v2.6.0
"""

import pytest
import hmac
import hashlib
import time
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from api.adapters.slack_adapter.routes.slack_webhook import router


# ══════════════════════════════════════════════════════════════════════════════
# TEST APP SETUP
# ══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def app(monkeypatch):
    """Create test FastAPI app."""
    # Set test secret in environment for signature verification
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "test_secret")

    app = FastAPI()
    app.include_router(router)

    # Mock app state
    app.state.substrate_service = AsyncMock()
    app.state.substrate_service.write_packet = AsyncMock(
        return_value=MagicMock(packet_id=uuid4())
    )
    app.state.substrate_service.search_packets = AsyncMock(return_value=[])

    app.state.aios_runtime = AsyncMock()
    app.state.aios_runtime.execute_reasoning = AsyncMock(return_value={"status": "ok"})

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def generate_slack_signature(
    body: str, timestamp: str, secret: str = "test_secret"
) -> str:
    """Generate valid Slack HMAC-SHA256 signature."""
    sig_basestring = f"v0:{timestamp}:{body}"
    sig = hmac.new(secret.encode(), sig_basestring.encode(), hashlib.sha256).hexdigest()
    return f"v0={sig}"


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestRoutes:
    """Route-level integration tests."""

    def test_missing_signature_rejected(self, client):
        """ACCEPTANCE: invalid_signature_rejected - route returns 401 without signature."""
        response = client.post(
            "/slack/events",
            json={"event_id": "test", "payload": {}},
            # No X-Slack-Signature header
        )

        # ASSERTION: 401 Unauthorized
        assert response.status_code == 401

    def test_invalid_signature_rejected(self, client):
        """ACCEPTANCE: invalid_signature_rejected - route returns 401 with invalid signature."""
        timestamp = str(int(time.time()))
        response = client.post(
            "/slack/events",
            json={"event_id": "test", "payload": {}},
            headers={
                "X-Slack-Signature": "v0=invalid",
                "X-Slack-Request-Timestamp": timestamp,
            },
        )

        # ASSERTION: 401 Unauthorized
        assert response.status_code == 401

    def test_url_verification_challenge(self, client):
        """Slack URL verification challenge response."""
        timestamp = str(int(time.time()))
        body = '{"type": "url_verification", "challenge": "test_challenge_123"}'

        response = client.post(
            "/slack/events",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Slack-Signature": generate_slack_signature(body, timestamp),
                "X-Slack-Request-Timestamp": timestamp,
            },
        )

        # ASSERTION: Should return challenge
        assert response.status_code == 200
        data = response.json()
        assert data.get("challenge") == "test_challenge_123"

    def test_health_endpoint(self, client):
        """Health check endpoint works."""
        response = client.get("/slack/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["module"] == "slack.webhook"
