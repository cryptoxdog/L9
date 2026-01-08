"""
L9 Slack Webhook API Tests
==========================

API-level tests for POST /slack/commands and POST /slack/events endpoints.
Uses TestClient with mocked dependencies - no real Slack/Redis/database calls.

Version: 1.0.0

Test Categories:
1. Unit tests for verify_slack_signature (pure function)
2. API tests for POST /slack/commands
3. API tests for POST /slack/events

Mocked Dependencies:
- app.state.agent_executor
- route_slack_message (orchestration.slack_task_router)
- enqueue_task, enqueue_mac_task (services.mac_tasks)
- slack_post (services.slack_client)
- GmailClient (email_agent.gmail_client)
"""

import sys
from pathlib import Path
import types

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Mock api.db BEFORE importing api.server to prevent database connection attempts
if "api.db" not in sys.modules:
    api_db_module = types.ModuleType("api.db")
    api_db_module.init_db = lambda: None  # Mock function
    sys.modules["api.db"] = api_db_module

import pytest
import hmac
import hashlib
import time
import json
from unittest.mock import patch, MagicMock, AsyncMock


# =============================================================================
# Helper Functions
# =============================================================================


def generate_slack_signature(body: str, timestamp: str, secret: str) -> str:
    """Generate valid Slack HMAC-SHA256 signature for testing."""
    sig_basestring = f"v0:{timestamp}:{body}"
    signature = hmac.new(
        secret.encode(), sig_basestring.encode(), hashlib.sha256
    ).hexdigest()
    return f"v0={signature}"


def fresh_timestamp() -> str:
    """Return current Unix timestamp as string."""
    return str(int(time.time()))


def stale_timestamp() -> str:
    """Return timestamp > 300 seconds old (outside tolerance)."""
    return str(int(time.time()) - 400)


# =============================================================================
# Test Constants
# =============================================================================

TEST_SIGNING_SECRET = "test_slack_signing_secret_123"
TEST_CHANNEL_ID = "C12345678"
TEST_USER_ID = "U12345678"
TEST_TEAM_ID = "T12345678"


# =============================================================================
# Unit Tests: verify_slack_signature (Pure Function)
# =============================================================================


class TestVerifySlackSignature:
    """
    Unit tests for the verify_slack_signature function in webhook_slack.py.
    
    This is a pure function that validates Slack HMAC-SHA256 signatures.
    Tests do NOT require FastAPI app or HTTP client.
    """

    def test_verify_signature_valid(self):
        """Valid signature with fresh timestamp returns True."""
        from api.webhook_slack import verify_slack_signature

        body = '{"type":"url_verification","challenge":"test123"}'
        timestamp = fresh_timestamp()
        signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

        result = verify_slack_signature(
            body=body,
            timestamp=timestamp,
            signature=signature,
            signing_secret=TEST_SIGNING_SECRET,
        )

        assert result is True

    def test_verify_signature_invalid_hash(self):
        """Invalid hash returns False."""
        from api.webhook_slack import verify_slack_signature

        body = '{"type":"url_verification"}'
        timestamp = fresh_timestamp()
        signature = "v0=invalid_hash_that_wont_match"

        result = verify_slack_signature(
            body=body,
            timestamp=timestamp,
            signature=signature,
            signing_secret=TEST_SIGNING_SECRET,
        )

        assert result is False

    def test_verify_signature_stale_timestamp(self):
        """Timestamp > 300 seconds old returns False."""
        from api.webhook_slack import verify_slack_signature

        body = '{"type":"url_verification"}'
        timestamp = stale_timestamp()
        # Generate valid signature with stale timestamp
        signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

        result = verify_slack_signature(
            body=body,
            timestamp=timestamp,
            signature=signature,
            signing_secret=TEST_SIGNING_SECRET,
        )

        assert result is False

    def test_verify_signature_missing_timestamp(self):
        """Empty or None timestamp returns False."""
        from api.webhook_slack import verify_slack_signature

        body = '{"type":"url_verification"}'
        signature = "v0=some_hash"

        # Empty string timestamp
        result = verify_slack_signature(
            body=body,
            timestamp="",
            signature=signature,
            signing_secret=TEST_SIGNING_SECRET,
        )
        assert result is False

    def test_verify_signature_missing_signature(self):
        """Empty or None signature returns False."""
        from api.webhook_slack import verify_slack_signature

        body = '{"type":"url_verification"}'
        timestamp = fresh_timestamp()

        # Empty string signature
        result = verify_slack_signature(
            body=body,
            timestamp=timestamp,
            signature="",
            signing_secret=TEST_SIGNING_SECRET,
        )
        assert result is False

    def test_verify_signature_no_secret(self):
        """Missing signing_secret returns False."""
        from api.webhook_slack import verify_slack_signature

        body = '{"type":"url_verification"}'
        timestamp = fresh_timestamp()
        signature = "v0=some_hash"

        # None signing_secret
        result = verify_slack_signature(
            body=body,
            timestamp=timestamp,
            signature=signature,
            signing_secret=None,
        )
        assert result is False

        # Empty string signing_secret
        result = verify_slack_signature(
            body=body,
            timestamp=timestamp,
            signature=signature,
            signing_secret="",
        )
        assert result is False


# =============================================================================
# Test App Factory - Creates isolated test app with webhook_slack router
# =============================================================================


def create_test_app(slack_enabled: bool = True, signing_secret: str = TEST_SIGNING_SECRET):
    """
    Create a minimal FastAPI app with webhook_slack router for testing.
    
    This avoids importing the full api.server which has many dependencies.
    """
    from fastapi import FastAPI
    
    # Set env vars before importing webhook_slack
    import os
    os.environ["SLACK_APP_ENABLED"] = "true" if slack_enabled else "false"
    os.environ["SLACK_SIGNING_SECRET"] = signing_secret
    
    # Force reimport to pick up env var changes
    import importlib
    import api.webhook_slack
    importlib.reload(api.webhook_slack)
    
    app = FastAPI()
    app.include_router(api.webhook_slack.router)
    
    return app


# =============================================================================
# API Tests: POST /slack/commands
# =============================================================================


class TestSlackCommands:
    """
    API tests for POST /slack/commands endpoint.
    
    Uses TestClient with mocked dependencies for route_slack_message,
    enqueue_task, and GmailClient.
    """

    def test_commands_disabled_returns_503(self):
        """When SLACK_APP_ENABLED=false, returns HTTP 503."""
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=False)
        client = TestClient(app, raise_server_exceptions=False)

        form_data = {
            "command": "/l9",
            "text": "do something",
            "user_id": TEST_USER_ID,
            "channel_id": TEST_CHANNEL_ID,
            "response_url": "https://hooks.slack.com/commands/...",
        }

        response = client.post("/slack/commands", data=form_data)

        assert response.status_code == 503
        assert "disabled" in response.json().get("detail", "").lower()

    def test_commands_do_subcommand(self):
        """POST /slack/commands with 'do' subcommand routes to task planner."""
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=True)

        # Mock dependencies - patch where they are imported in the module
        with patch("orchestration.slack_task_router.route_slack_message") as mock_route, \
             patch("services.mac_tasks.enqueue_task") as mock_enqueue:

            mock_route.return_value = {
                "type": "mac_task",
                "steps": [],
                "metadata": {"user": TEST_USER_ID},
            }
            mock_enqueue.return_value = "task-12345"

            client = TestClient(app, raise_server_exceptions=False)

            form_data = {
                "command": "/l9",
                "text": "do make a report",
                "user_id": TEST_USER_ID,
                "channel_id": TEST_CHANNEL_ID,
                "response_url": "https://hooks.slack.com/commands/...",
            }

            response = client.post("/slack/commands", data=form_data)

            assert response.status_code == 200
            data = response.json()
            assert "task-12345" in data.get("text", "")
            assert data.get("response_type") == "ephemeral"

            # Verify mocks called correctly
            mock_route.assert_called_once()
            mock_enqueue.assert_called_once()

    def test_commands_email_search(self):
        """POST /slack/commands with 'email search' invokes GmailClient."""
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=True)

        # Mock GmailClient
        mock_gmail = MagicMock()
        mock_gmail.list_messages.return_value = [
            {"subject": "Test Email 1", "from": "sender@example.com"},
            {"subject": "Test Email 2", "from": "another@example.com"},
        ]

        with patch("email_agent.gmail_client.GmailClient", return_value=mock_gmail):
            client = TestClient(app, raise_server_exceptions=False)

            form_data = {
                "command": "/l9",
                "text": "email search test query",
                "user_id": TEST_USER_ID,
                "channel_id": TEST_CHANNEL_ID,
                "response_url": "https://hooks.slack.com/commands/...",
            }

            response = client.post("/slack/commands", data=form_data)

            assert response.status_code == 200
            data = response.json()
            # Should contain results from mock
            assert "Found 2 messages" in data.get("text", "") or "Test Email" in data.get("text", "")

    def test_commands_unknown_returns_help(self):
        """Unknown subcommand returns help text."""
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=True)
        client = TestClient(app, raise_server_exceptions=False)

        form_data = {
            "command": "/l9",
            "text": "unknowncommand foo bar",
            "user_id": TEST_USER_ID,
            "channel_id": TEST_CHANNEL_ID,
            "response_url": "https://hooks.slack.com/commands/...",
        }

        response = client.post("/slack/commands", data=form_data)

        assert response.status_code == 200
        data = response.json()
        # Should mention available commands
        assert "Unknown command" in data.get("text", "") or "/l9 do" in data.get("text", "")


# =============================================================================
# API Tests: POST /slack/events
# =============================================================================


class TestSlackEvents:
    """
    API tests for POST /slack/events endpoint.
    
    Uses TestClient with mocked dependencies for signature verification,
    handle_slack_with_l_agent, slack_post, and enqueue_mac_task.
    """

    def test_events_disabled_returns_503(self):
        """When SLACK_APP_ENABLED=false, returns HTTP 503."""
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=False)
        client = TestClient(app, raise_server_exceptions=False)

        payload = {"type": "url_verification", "challenge": "test123"}
        body = json.dumps(payload)
        timestamp = fresh_timestamp()
        signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

        response = client.post(
            "/slack/events",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Slack-Signature": signature,
                "X-Slack-Request-Timestamp": timestamp,
            },
        )

        assert response.status_code == 503
        assert "disabled" in response.json().get("detail", "").lower()

    def test_events_bad_signature_returns_403(self):
        """Invalid HMAC signature returns HTTP 403."""
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=True)
        client = TestClient(app, raise_server_exceptions=False)

        payload = {"type": "url_verification", "challenge": "test123"}
        body = json.dumps(payload)
        timestamp = fresh_timestamp()
        # Invalid signature
        signature = "v0=invalid_signature_that_wont_match"

        response = client.post(
            "/slack/events",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Slack-Signature": signature,
                "X-Slack-Request-Timestamp": timestamp,
            },
        )

        assert response.status_code == 403
        assert "signature" in response.json().get("detail", "").lower()

    def test_events_url_verification(self):
        """URL verification challenge is echoed back."""
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=True)
        client = TestClient(app, raise_server_exceptions=False)

        challenge_value = "unique_challenge_abc123"
        payload = {"type": "url_verification", "challenge": challenge_value}
        body = json.dumps(payload)
        timestamp = fresh_timestamp()
        signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

        response = client.post(
            "/slack/events",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Slack-Signature": signature,
                "X-Slack-Request-Timestamp": timestamp,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("challenge") == challenge_value

    def test_events_app_mention_legacy_router(self):
        """App mention with legacy router calls slack_post."""
        import os
        os.environ["L9_ENABLE_LEGACY_SLACK_ROUTER"] = "true"
        
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=True)

        # Mock slack_post to capture calls
        with patch("services.slack_client.slack_post") as mock_slack_post:
            client = TestClient(app, raise_server_exceptions=False)

            payload = {
                "type": "event_callback",
                "team_id": TEST_TEAM_ID,
                "event": {
                    "type": "app_mention",
                    "text": "<@U123> hello L9",
                    "user": TEST_USER_ID,
                    "channel": TEST_CHANNEL_ID,
                    "ts": "1234567890.123456",
                },
                "event_id": "Ev12345678",
            }
            body = json.dumps(payload)
            timestamp = fresh_timestamp()
            signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

            response = client.post(
                "/slack/events",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Slack-Signature": signature,
                    "X-Slack-Request-Timestamp": timestamp,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "ok"

            # Verify slack_post was called (legacy router responds directly)
            mock_slack_post.assert_called()

    def test_events_app_mention_l_agent_router(self):
        """App mention with L-agent router calls handle_slack_with_l_agent."""
        import os
        os.environ["L9_ENABLE_LEGACY_SLACK_ROUTER"] = "false"
        
        from fastapi.testclient import TestClient
        
        # Force reimport to pick up env var changes
        import importlib
        import api.webhook_slack
        importlib.reload(api.webhook_slack)
        
        app = create_test_app(slack_enabled=True)

        # Mock handle_slack_with_l_agent and slack_post
        with patch("api.webhook_slack.handle_slack_with_l_agent") as mock_handler, \
             patch("services.slack_client.slack_post") as mock_slack_post:

            mock_handler.return_value = ("Hello from L-CTO!", "completed")

            client = TestClient(app, raise_server_exceptions=False)

            payload = {
                "type": "event_callback",
                "team_id": TEST_TEAM_ID,
                "event": {
                    "type": "app_mention",
                    "text": "<@U123> hello L9",
                    "user": TEST_USER_ID,
                    "channel": TEST_CHANNEL_ID,
                    "ts": "1234567890.123456",
                },
                "event_id": "Ev12345678",
            }
            body = json.dumps(payload)
            timestamp = fresh_timestamp()
            signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

            response = client.post(
                "/slack/events",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Slack-Signature": signature,
                    "X-Slack-Request-Timestamp": timestamp,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "ok"

            # Verify the L-agent handler was called
            mock_handler.assert_called_once()
            # Verify reply was posted
            mock_slack_post.assert_called()

    def test_events_bot_message_ignored(self):
        """Bot messages (subtype=bot_message) are ignored."""
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=True)
        client = TestClient(app, raise_server_exceptions=False)

        payload = {
            "type": "event_callback",
            "team_id": TEST_TEAM_ID,
            "event": {
                "type": "app_mention",
                "subtype": "bot_message",
                "text": "Bot says hello",
                "channel": TEST_CHANNEL_ID,
                "ts": "1234567890.123456",
            },
            "event_id": "Ev12345678",
        }
        body = json.dumps(payload)
        timestamp = fresh_timestamp()
        signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

        response = client.post(
            "/slack/events",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Slack-Signature": signature,
                "X-Slack-Request-Timestamp": timestamp,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"

    def test_events_mac_command(self):
        """Message starting with !mac enqueues Mac task."""
        import os
        os.environ["L9_ENABLE_LEGACY_SLACK_ROUTER"] = "true"
        
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=True)

        # Mock enqueue_mac_task and slack_post
        # Note: !mac commands are handled in "message" events, not "app_mention"
        with patch("services.mac_tasks.enqueue_mac_task") as mock_enqueue, \
             patch("services.slack_client.slack_post") as mock_slack_post:

            mock_enqueue.return_value = "mac-task-67890"

            client = TestClient(app, raise_server_exceptions=False)

            # Use "message" event type for !mac commands
            payload = {
                "type": "event_callback",
                "team_id": TEST_TEAM_ID,
                "event": {
                    "type": "message",
                    "text": "!mac echo hello world",
                    "user": TEST_USER_ID,
                    "channel": TEST_CHANNEL_ID,
                    "ts": "1234567890.123456",
                },
                "event_id": "Ev12345678",
            }
            body = json.dumps(payload)
            timestamp = fresh_timestamp()
            signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

            response = client.post(
                "/slack/events",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Slack-Signature": signature,
                    "X-Slack-Request-Timestamp": timestamp,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "ok"

            # Verify Mac task was enqueued
            mock_enqueue.assert_called_once()
            # Verify acknowledgment was posted
            mock_slack_post.assert_called()


# =============================================================================
# Bot Message Filtering Tests (Infinite Loop Prevention)
# =============================================================================


class TestBotMessageFiltering:
    """
    Tests for bot message filtering to prevent infinite response loops.
    
    L should ignore:
    1. Messages with subtype=bot_message
    2. Messages with bot_id field
    3. Messages from L's own user ID (L_SLACK_USER_ID or SLACK_BOT_USER_ID)
    """

    def test_ignores_own_user_id(self):
        """Messages from L's own user ID should be ignored."""
        import os
        os.environ["L_SLACK_USER_ID"] = "l-cto"
        
        from fastapi.testclient import TestClient
        
        # Force reimport to pick up env var
        import importlib
        import api.webhook_slack
        importlib.reload(api.webhook_slack)
        
        app = create_test_app(slack_enabled=True)

        # Mock slack_post to verify it's NOT called
        with patch("services.slack_client.slack_post") as mock_slack_post:
            client = TestClient(app, raise_server_exceptions=False)

            # Message FROM L's user ID (should be ignored)
            payload = {
                "type": "event_callback",
                "team_id": TEST_TEAM_ID,
                "event": {
                    "type": "app_mention",
                    "text": "Hello from L",
                    "user": "l-cto",  # L's own user ID
                    "channel": TEST_CHANNEL_ID,
                    "ts": "1234567890.123456",
                },
                "event_id": "Ev_own_user_test",
            }
            body = json.dumps(payload)
            timestamp = fresh_timestamp()
            signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

            response = client.post(
                "/slack/events",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Slack-Signature": signature,
                    "X-Slack-Request-Timestamp": timestamp,
                },
            )

            assert response.status_code == 200
            assert response.json().get("status") == "ok"
            # slack_post should NOT be called for L's own messages
            mock_slack_post.assert_not_called()

    def test_ignores_bot_id_field(self):
        """Messages with bot_id field should be ignored."""
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=True)

        with patch("services.slack_client.slack_post") as mock_slack_post:
            client = TestClient(app, raise_server_exceptions=False)

            payload = {
                "type": "event_callback",
                "team_id": TEST_TEAM_ID,
                "event": {
                    "type": "app_mention",
                    "text": "Bot message",
                    "user": "U_SOME_BOT",
                    "bot_id": "B12345678",  # Has bot_id = is a bot
                    "channel": TEST_CHANNEL_ID,
                    "ts": "1234567890.123456",
                },
                "event_id": "Ev_bot_id_test",
            }
            body = json.dumps(payload)
            timestamp = fresh_timestamp()
            signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

            response = client.post(
                "/slack/events",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Slack-Signature": signature,
                    "X-Slack-Request-Timestamp": timestamp,
                },
            )

            assert response.status_code == 200
            assert response.json().get("status") == "ok"
            mock_slack_post.assert_not_called()

    def test_ignores_bot_message_subtype(self):
        """Messages with subtype=bot_message should be ignored."""
        from fastapi.testclient import TestClient
        
        app = create_test_app(slack_enabled=True)

        with patch("services.slack_client.slack_post") as mock_slack_post:
            client = TestClient(app, raise_server_exceptions=False)

            payload = {
                "type": "event_callback",
                "team_id": TEST_TEAM_ID,
                "event": {
                    "type": "message",
                    "subtype": "bot_message",  # Bot message subtype
                    "text": "Automated message",
                    "channel": TEST_CHANNEL_ID,
                    "ts": "1234567890.123456",
                },
                "event_id": "Ev_subtype_test",
            }
            body = json.dumps(payload)
            timestamp = fresh_timestamp()
            signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

            response = client.post(
                "/slack/events",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Slack-Signature": signature,
                    "X-Slack-Request-Timestamp": timestamp,
                },
            )

            assert response.status_code == 200
            assert response.json().get("status") == "ok"
            mock_slack_post.assert_not_called()


# =============================================================================
# Event Deduplication Tests
# =============================================================================


class TestEventDeduplication:
    """
    Tests for event_id deduplication to prevent duplicate processing.
    
    Slack retries webhooks after 3 seconds if no 200 response.
    Same event_id should only be processed once.
    """

    def test_duplicate_event_ignored(self):
        """Same event_id sent twice should only be processed once."""
        from fastapi.testclient import TestClient
        
        # Clear the dedupe cache before test
        import api.webhook_slack
        api.webhook_slack._event_dedupe_cache.clear()
        
        app = create_test_app(slack_enabled=True)

        with patch("services.slack_client.slack_post") as mock_slack_post:
            client = TestClient(app, raise_server_exceptions=False)

            event_id = "Ev_dedupe_test_12345"
            payload = {
                "type": "event_callback",
                "team_id": TEST_TEAM_ID,
                "event": {
                    "type": "message",
                    "text": "!mac echo test",
                    "user": TEST_USER_ID,
                    "channel": TEST_CHANNEL_ID,
                    "ts": "1234567890.123456",
                },
                "event_id": event_id,
            }
            body = json.dumps(payload)
            timestamp = fresh_timestamp()
            signature = generate_slack_signature(body, timestamp, TEST_SIGNING_SECRET)

            headers = {
                "Content-Type": "application/json",
                "X-Slack-Signature": signature,
                "X-Slack-Request-Timestamp": timestamp,
            }

            # First request - should be processed
            with patch("services.mac_tasks.enqueue_mac_task") as mock_enqueue:
                mock_enqueue.return_value = "task-123"
                response1 = client.post("/slack/events", content=body, headers=headers)
                assert response1.status_code == 200
                first_call_count = mock_enqueue.call_count

            # Second request with SAME event_id - should be deduplicated
            with patch("services.mac_tasks.enqueue_mac_task") as mock_enqueue2:
                mock_enqueue2.return_value = "task-456"
                response2 = client.post("/slack/events", content=body, headers=headers)
                assert response2.status_code == 200
                # Should NOT have been called again
                assert mock_enqueue2.call_count == 0

    def test_different_event_ids_both_processed(self):
        """Different event_ids should both be processed."""
        from fastapi.testclient import TestClient
        
        # Clear the dedupe cache before test
        import api.webhook_slack
        api.webhook_slack._event_dedupe_cache.clear()
        
        app = create_test_app(slack_enabled=True)

        with patch("services.mac_tasks.enqueue_mac_task") as mock_enqueue, \
             patch("services.slack_client.slack_post"):
            mock_enqueue.return_value = "task-123"
            
            client = TestClient(app, raise_server_exceptions=False)

            # First event
            payload1 = {
                "type": "event_callback",
                "team_id": TEST_TEAM_ID,
                "event": {
                    "type": "message",
                    "text": "!mac echo first",
                    "user": TEST_USER_ID,
                    "channel": TEST_CHANNEL_ID,
                    "ts": "1234567890.111111",
                },
                "event_id": "Ev_first_event",
            }
            body1 = json.dumps(payload1)
            timestamp1 = fresh_timestamp()
            sig1 = generate_slack_signature(body1, timestamp1, TEST_SIGNING_SECRET)

            response1 = client.post(
                "/slack/events",
                content=body1,
                headers={
                    "Content-Type": "application/json",
                    "X-Slack-Signature": sig1,
                    "X-Slack-Request-Timestamp": timestamp1,
                },
            )
            assert response1.status_code == 200
            first_call_count = mock_enqueue.call_count

            # Second event (different event_id)
            payload2 = {
                "type": "event_callback",
                "team_id": TEST_TEAM_ID,
                "event": {
                    "type": "message",
                    "text": "!mac echo second",
                    "user": TEST_USER_ID,
                    "channel": TEST_CHANNEL_ID,
                    "ts": "1234567890.222222",
                },
                "event_id": "Ev_second_event",
            }
            body2 = json.dumps(payload2)
            timestamp2 = fresh_timestamp()
            sig2 = generate_slack_signature(body2, timestamp2, TEST_SIGNING_SECRET)

            response2 = client.post(
                "/slack/events",
                content=body2,
                headers={
                    "Content-Type": "application/json",
                    "X-Slack-Signature": sig2,
                    "X-Slack-Request-Timestamp": timestamp2,
                },
            )
            assert response2.status_code == 200
            
            # Both should have been processed
            assert mock_enqueue.call_count == first_call_count + 1


class TestEventDedupeCacheUnit:
    """Unit tests for the EventDedupeCache class."""

    def test_cache_marks_first_occurrence_as_new(self):
        """First occurrence of event_id should return False (not duplicate)."""
        from api.webhook_slack import EventDedupeCache
        
        cache = EventDedupeCache(max_size=100, ttl_seconds=60)
        
        assert cache.is_duplicate("event_1") is False

    def test_cache_marks_second_occurrence_as_duplicate(self):
        """Second occurrence of same event_id should return True (duplicate)."""
        from api.webhook_slack import EventDedupeCache
        
        cache = EventDedupeCache(max_size=100, ttl_seconds=60)
        
        cache.is_duplicate("event_1")  # First call
        assert cache.is_duplicate("event_1") is True  # Second call = duplicate

    def test_cache_respects_max_size(self):
        """Cache should evict oldest entries when max_size exceeded."""
        from api.webhook_slack import EventDedupeCache
        
        cache = EventDedupeCache(max_size=3, ttl_seconds=60)
        
        # Add 4 events (exceeds max_size of 3)
        cache.is_duplicate("event_1")
        cache.is_duplicate("event_2")
        cache.is_duplicate("event_3")
        cache.is_duplicate("event_4")  # Should evict event_1
        
        # event_1 should be evicted, so it's "new" again
        assert cache.is_duplicate("event_1") is False
        # event_4 should still be in cache
        assert cache.is_duplicate("event_4") is True

    def test_cache_handles_empty_event_id(self):
        """Empty event_id should return False (can't dedupe, process it)."""
        from api.webhook_slack import EventDedupeCache
        
        cache = EventDedupeCache(max_size=100, ttl_seconds=60)
        
        assert cache.is_duplicate("") is False
        assert cache.is_duplicate("") is False  # Still False

    def test_cache_clear(self):
        """Cache clear should remove all entries."""
        from api.webhook_slack import EventDedupeCache
        
        cache = EventDedupeCache(max_size=100, ttl_seconds=60)
        
        cache.is_duplicate("event_1")
        cache.is_duplicate("event_2")
        cache.clear()
        
        # After clear, events should be "new" again
        assert cache.is_duplicate("event_1") is False
        assert cache.is_duplicate("event_2") is False


# =============================================================================
# Run Tests
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

