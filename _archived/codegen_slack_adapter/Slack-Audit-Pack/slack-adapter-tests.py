"""
Unit Tests for Slack Webhook Adapter
Production-grade tests with real mocks aligned to L9 repo patterns.
"""

import json
import time
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from slack_webhook_adapter import (
    SlackSignatureVerifier,
    SlackEventNormalizer,
    DuplicateDetector,
    SlackWebhookAdapter,
    SlackWebhookResponse,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def signing_secret() -> str:
    """Slack app signing secret for testing."""
    return "test-signing-secret"


@pytest.fixture
def mock_substrate_service():
    """
    Mock MemorySubstrateService.
    
    Returns PacketWriteResult (real model from repo),
    not string packet_id.
    """
    from memory.substratemodels import PacketWriteResult

    service = AsyncMock()

    # write_packet returns PacketWriteResult
    service.write_packet = AsyncMock(
        return_value=PacketWriteResult(
            packet_id=str(uuid4()),
            success=True,
            message="Packet stored",
        )
    )

    # search_packets returns list (not awaited second time)
    service.search_packets = AsyncMock(return_value=[])

    return service


@pytest.fixture
def slack_adapter(signing_secret, mock_substrate_service):
    """Create adapter instance with mocked substrate."""
    return SlackWebhookAdapter(
        signing_secret=signing_secret,
        substrate_service=mock_substrate_service,
        workspace_id="slack-test",
    )


# ============================================================================
# SIGNATURE VERIFICATION TESTS
# ============================================================================


class TestSlackSignatureVerifier:
    """Test Slack request signature verification."""

    def test_verify_valid_signature(self, signing_secret):
        """Valid signature passes verification."""
        verifier = SlackSignatureVerifier(signing_secret)

        # Create valid signature
        timestamp = str(int(time.time()))
        body = b'{"type":"event_callback"}'
        sig_basestring = f"v0:{timestamp}:{body.decode()}"

        import hashlib
        import hmac

        valid_signature = (
            "v0="
            + hmac.new(
                signing_secret.encode(),
                sig_basestring.encode(),
                hashlib.sha256,
            ).hexdigest()
        )

        # Verify
        assert verifier.verify(timestamp, body, valid_signature) is True

    def test_verify_invalid_signature(self, signing_secret):
        """Invalid signature fails verification."""
        verifier = SlackSignatureVerifier(signing_secret)

        timestamp = str(int(time.time()))
        body = b'{"type":"event_callback"}'
        invalid_signature = "v0=invalid"

        assert verifier.verify(timestamp, body, invalid_signature) is False

    def test_verify_stale_timestamp(self, signing_secret):
        """Stale timestamp (>5 min) fails verification."""
        verifier = SlackSignatureVerifier(signing_secret)

        # Timestamp 10 minutes ago
        timestamp = str(int(time.time()) - 600)
        body = b'{"type":"event_callback"}'
        signature = "v0=anything"

        assert verifier.verify(timestamp, body, signature) is False

    def test_verify_invalid_timestamp_format(self, signing_secret):
        """Invalid timestamp format fails gracefully."""
        verifier = SlackSignatureVerifier(signing_secret)

        timestamp = "not-a-number"
        body = b'{"type":"event_callback"}'
        signature = "v0=anything"

        assert verifier.verify(timestamp, body, signature) is False


# ============================================================================
# EVENT NORMALIZATION TESTS
# ============================================================================


class TestSlackEventNormalizer:
    """Test Slack event normalization."""

    def test_parse_message_event(self):
        """Parse valid message event."""
        normalizer = SlackEventNormalizer()

        payload = {
            "team_id": "T123",
            "event": {
                "type": "message",
                "user": "U456",
                "channel": "C789",
                "text": "Hello L9",
                "ts": "1234567890.123456",
                "thread_ts": None,
            },
        }

        result = normalizer.parse_event_callback(payload)

        assert result is not None
        assert result["type"] == "message"
        assert result["user"] == "U456"
        assert result["text"] == "Hello L9"

    def test_parse_app_mention_event(self):
        """Parse valid app_mention event."""
        normalizer = SlackEventNormalizer()

        payload = {
            "team_id": "T123",
            "event": {
                "type": "app_mention",
                "user": "U456",
                "channel": "C789",
                "text": "<@UBOT> what is 2+2?",
                "ts": "1234567890.123456",
            },
        }

        result = normalizer.parse_event_callback(payload)

        assert result is not None
        assert result["type"] == "app_mention"

    def test_parse_unsupported_event(self):
        """Unsupported event type returns None."""
        normalizer = SlackEventNormalizer()

        payload = {
            "team_id": "T123",
            "event": {
                "type": "file_shared",
                "user": "U456",
                "channel": "C789",
            },
        }

        result = normalizer.parse_event_callback(payload)
        assert result is None

    def test_generate_thread_uuid_deterministic(self):
        """Generated thread UUID is deterministic."""
        normalizer = SlackEventNormalizer()

        team_id = "T123"
        channel_id = "C456"
        thread_ts = "1234567890.123456"

        # Generate same UUID twice
        uuid1 = normalizer.generate_thread_uuid(team_id, channel_id, thread_ts)
        uuid2 = normalizer.generate_thread_uuid(team_id, channel_id, thread_ts)

        # Must be identical (for idempotency)
        assert uuid1 == uuid2

    def test_generate_thread_uuid_different_for_different_inputs(self):
        """Different inputs generate different UUIDs."""
        normalizer = SlackEventNormalizer()

        uuid1 = normalizer.generate_thread_uuid("T123", "C456", "1234567890.123456")
        uuid2 = normalizer.generate_thread_uuid("T999", "C456", "1234567890.123456")

        assert uuid1 != uuid2


# ============================================================================
# DUPLICATE DETECTION TESTS
# ============================================================================


class TestDuplicateDetector:
    """Test duplicate event detection."""

    @pytest.mark.asyncio
    async def test_is_duplicate_returns_true_for_known_event(self, mock_substrate_service):
        """Returns True if event is in substrate."""
        # Mock substrate to return a packet
        from memory.substratemodels import PacketEnvelopeIn

        existing_packet = MagicMock(spec=PacketEnvelopeIn)
        mock_substrate_service.search_packets = AsyncMock(return_value=[existing_packet])

        detector = DuplicateDetector(mock_substrate_service)
        is_dup = await detector.is_duplicate("event_123")

        assert is_dup is True
        mock_substrate_service.search_packets.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_duplicate_returns_false_for_new_event(self, mock_substrate_service):
        """Returns False if event is not in substrate."""
        # Mock substrate to return empty list
        mock_substrate_service.search_packets = AsyncMock(return_value=[])

        detector = DuplicateDetector(mock_substrate_service)
        is_dup = await detector.is_duplicate("event_new")

        assert is_dup is False

    @pytest.mark.asyncio
    async def test_is_duplicate_handles_substrate_error(self, mock_substrate_service):
        """Handles substrate errors gracefully (fail-open)."""
        # Mock substrate to raise error
        mock_substrate_service.search_packets = AsyncMock(
            side_effect=Exception("Database error")
        )

        detector = DuplicateDetector(mock_substrate_service)
        is_dup = await detector.is_duplicate("event_123")

        # Should return False on error (fail-open)
        assert is_dup is False


# ============================================================================
# ADAPTER TESTS
# ============================================================================


class TestSlackWebhookAdapter:
    """Test main adapter functionality."""

    @pytest.mark.asyncio
    async def test_handle_webhook_url_verification(self, slack_adapter, signing_secret):
        """Handles URL verification challenge."""
        # Create valid challenge request
        timestamp = str(int(time.time()))
        challenge_token = "abc123def456"
        payload = {"type": "url_verification", "challenge": challenge_token}
        body = json.dumps(payload).encode()

        # Create valid signature
        import hashlib
        import hmac

        sig_basestring = f"v0:{timestamp}:{body.decode()}"
        signature = (
            "v0="
            + hmac.new(
                signing_secret.encode(),
                sig_basestring.encode(),
                hashlib.sha256,
            ).hexdigest()
        )

        # Create mock request
        request = MagicMock()
        request.body = AsyncMock(return_value=body)
        request.headers = {
            "x-slack-signature": signature,
            "x-slack-request-timestamp": timestamp,
        }

        status, response = await slack_adapter.handle_webhook(request)

        assert status == 200
        assert response["challenge"] == challenge_token

    @pytest.mark.asyncio
    async def test_handle_webhook_invalid_signature(self, slack_adapter):
        """Rejects invalid signatures."""
        request = MagicMock()
        request.body = AsyncMock(return_value=b'{"type":"event_callback"}')
        request.headers = {
            "x-slack-signature": "v0=invalid",
            "x-slack-request-timestamp": str(int(time.time())),
        }

        status, response = await slack_adapter.handle_webhook(request)

        assert status == 401
        assert "error" in response

    @pytest.mark.asyncio
    async def test_handle_webhook_invalid_json(self, slack_adapter, signing_secret):
        """Handles invalid JSON gracefully."""
        timestamp = str(int(time.time()))
        body = b"not-json"

        # Create valid signature for invalid JSON
        import hashlib
        import hmac

        sig_basestring = f"v0:{timestamp}:{body.decode()}"
        signature = (
            "v0="
            + hmac.new(
                signing_secret.encode(),
                sig_basestring.encode(),
                hashlib.sha256,
            ).hexdigest()
        )

        request = MagicMock()
        request.body = AsyncMock(return_value=body)
        request.headers = {
            "x-slack-signature": signature,
            "x-slack-request-timestamp": timestamp,
        }

        status, response = await slack_adapter.handle_webhook(request)

        assert status == 400

    @pytest.mark.asyncio
    async def test_handle_event_callback_stores_packet(self, slack_adapter):
        """Stores valid event callback as packet."""
        from memory.substratemodels import PacketWriteResult

        # Mock substrate to return success
        write_result = PacketWriteResult(
            packet_id="pkt_123",
            success=True,
            message="Stored",
        )
        slack_adapter.substrate_service.write_packet = AsyncMock(return_value=write_result)
        slack_adapter.substrate_service.search_packets = AsyncMock(return_value=[])

        payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev123",
            "event": {
                "type": "message",
                "user": "U456",
                "channel": "C789",
                "text": "Hello",
                "ts": "1234567890.123456",
            },
        }

        status, response = await slack_adapter._handle_event_callback(payload)

        assert status == 200
        assert response["ok"] is True
        slack_adapter.substrate_service.write_packet.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_event_callback_deduplicates(self, slack_adapter):
        """Skips duplicate events."""
        # Mock duplicate detection
        slack_adapter.substrate_service.search_packets = AsyncMock(
            return_value=[MagicMock()]  # Non-empty = duplicate
        )

        payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev123",  # Duplicate
            "event": {
                "type": "message",
                "user": "U456",
                "channel": "C789",
                "text": "Hello",
                "ts": "1234567890.123456",
            },
        }

        status, response = await slack_adapter._handle_event_callback(payload)

        assert status == 200
        # Should NOT call write_packet for duplicate
        slack_adapter.substrate_service.write_packet.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_event_callback_error_handling(self, slack_adapter):
        """Handles substrate errors gracefully."""
        slack_adapter.substrate_service.search_packets = AsyncMock(
            side_effect=Exception("DB error")
        )

        payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev123",
            "event": {
                "type": "message",
                "user": "U456",
                "channel": "C789",
                "text": "Hello",
                "ts": "1234567890.123456",
            },
        }

        status, response = await slack_adapter._handle_event_callback(payload)

        # Always return 200 (Slack expects it)
        assert status == 200


# ============================================================================
# INTEGRATION-STYLE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_full_message_flow(slack_adapter, signing_secret):
    """Full flow: valid signature → parse → store packet."""
    import hashlib
    import hmac

    # 1. Create valid signed request
    timestamp = str(int(time.time()))
    payload = {
        "type": "event_callback",
        "team_id": "T123",
        "event_id": "Ev456",
        "event": {
            "type": "message",
            "user": "U789",
            "channel": "C111",
            "text": "Hello L9",
            "ts": "1234567890.123456",
        },
    }
    body = json.dumps(payload).encode()

    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    signature = (
        "v0="
        + hmac.new(
            signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256,
        ).hexdigest()
    )

    # 2. Create mock request
    request = MagicMock()
    request.body = AsyncMock(return_value=body)
    request.headers = {
        "x-slack-signature": signature,
        "x-slack-request-timestamp": timestamp,
    }

    # 3. Call adapter
    status, response = await slack_adapter.handle_webhook(request)

    # 4. Verify
    assert status == 200
    assert response["ok"] is True

    # 5. Verify substrate was called
    slack_adapter.substrate_service.write_packet.assert_called_once()

    # 6. Verify packet structure
    call_args = slack_adapter.substrate_service.write_packet.call_args
    packet_in = call_args[0][0]

    assert packet_in.packet_type == "slack.in"
    assert "Hello L9" in packet_in.payload["text"]
    assert "slack" in packet_in.tags
