# ══════════════════════════════════════════════════════════════════════════════
# Generated from Module-Spec v2.6
# module_id: twilio.adapter
# enforced_acceptance: ["valid_sms_processed", "idempotent_replay_cached", "signature_validated", "aios_response_forwarded", "packet_written_on_success", ... (8 total)]
# ══════════════════════════════════════════════════════════════════════════════
# DORA META BLOCK — DO NOT EDIT MANUALLY (CI-owned)
# ══════════════════════════════════════════════════════════════════════════════
# __meta__ = {
#     "template_version": "2.6.0",
#     "spec_hash": "SPEC-102d1d3dc34c",
#     "created_at": "2025-12-18T06:25:01.645626+00:00",
#     "created_by": "module_pipeline",
#     "last_updated_at": "2025-12-18T06:25:01.645626+00:00",
#     "last_updated_by": "module_pipeline",
#     "module_id": "twilio.adapter",
#     "file": "tests/test_twilio_adapter_integration.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Twilio Adapter Integration Tests
────────────────────────────────
Integration tests for Twilio Adapter routes

Auto-generated from Module-Spec v2.6.0
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from api.adapters.twilio_adapter.routes.twilio_adapter import router


# ══════════════════════════════════════════════════════════════════════════════
# TEST APP SETUP
# ══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()
    app.include_router(router)

    # Mock app state
    app.state.substrate_service = AsyncMock()
    app.state.substrate_service.write_packet = AsyncMock(
        return_value=MagicMock(packet_id=uuid4())
    )
    app.state.substrate_service.search_packets = AsyncMock(return_value=[])

    app.state.aios_runtime_client = AsyncMock()
    app.state.aios_runtime_client.chat = AsyncMock(return_value={"status": "ok"})

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestRoutes:
    """Route-level integration tests."""

    def test_invalid_auth_rejected(self, client):
        """ACCEPTANCE: invalid_auth_rejected - route returns 401 without auth."""
        response = client.post(
            "/twilio/webhook",
            json={"event_id": "test", "payload": {}},
            # No Authorization header
        )

        # ASSERTION: 401 Unauthorized
        assert response.status_code == 401

    def test_invalid_bearer_rejected(self, client):
        """ACCEPTANCE: invalid_auth_rejected - route returns 401 with invalid bearer."""
        response = client.post(
            "/twilio/webhook",
            json={"event_id": "test", "payload": {}},
            headers={"Authorization": "Basic invalid"},
        )

        # ASSERTION: 401 Unauthorized
        assert response.status_code == 401

    def test_valid_auth_accepted(self, client):
        """Route accepts valid bearer token."""
        response = client.post(
            "/twilio/webhook",
            json={"event_id": "test-123", "payload": {"message": "hello"}},
            headers={"Authorization": "Bearer valid_token"},
        )

        # ASSERTION: Request succeeds
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True

    def test_health_endpoint(self, client):
        """Health check endpoint works."""
        response = client.get("/twilio/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["module"] == "twilio.adapter"
