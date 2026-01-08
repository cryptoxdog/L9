"""
Integration Tests for Slack Adapter with Memory Substrate.

Tests the flow: Slack Request → Adapter → Memory Substrate
Uses canonical MockSubstrateService from GMP spec.
"""

import json
import time
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from slack_webhook_adapter import SlackWebhookAdapter
from memory.substratemodels import (
    PacketEnvelopeIn,
    PacketWriteResult,
    PacketMetadata,
)


# ============================================================================
# CANONICAL MOCK SUBSTRATE (from GMP spec)
# ============================================================================


class MockSubstrateService:
    """
    Mock substrate for integration testing.
    
    Hand-written fake that behaves like MemorySubstrateService.
    Used ONLY in integration tests where we want "real-ish" behavior
    without touching Postgres/Redis.
    
    Source: GMP-Action-Prompt-Integration-Tests-v1.0.md
    """

    def __init__(self):
        """Initialize in-memory storage."""
        self.packets = []
        self.search_results = []

    async def write_packet(self, packet: PacketEnvelopeIn) -> PacketWriteResult:
        """
        Write packet to storage.
        
        Args:
            packet: PacketEnvelopeIn to store
            
        Returns:
            PacketWriteResult with packet_id
        """
        self.packets.append(packet)
        packet_id = str(uuid4())
        return PacketWriteResult(
            packet_id=packet_id,
            success=True,
            message="Packet stored",
        )

    async def search_packets(
        self, metadata_filter: dict = None, limit: int = 10
    ) -> list:
        """
        Search stored packets.
        
        Args:
            metadata_filter: Metadata to filter on
            limit: Max results
            
        Returns:
            List of matching packets
        """
        # Simple in-memory search
        if metadata_filter is None:
            return self.packets[:limit]

        # Filter by metadata_filter keys
        results = []
        for packet in self.packets:
            matches = True
            for key, value in metadata_filter.items():
                # Check packet metadata
                if hasattr(packet, "metadata") and packet.metadata:
                    if getattr(packet.metadata, key, None) != value:
                        matches = False
                        break
                # Check tags
                if key == "slack_event_id" and hasattr(packet, "tags"):
                    if value not in packet.tags:
                        matches = False
                        break
            if matches:
                results.append(packet)

        return results[:limit]


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_substrate():
    """In-memory MockSubstrateService for integration tests."""
    return MockSubstrateService()


@pytest.fixture
def slack_adapter_with_mock_substrate(mock_substrate):
    """Create adapter with MockSubstrateService."""
    return SlackWebhookAdapter(
        signing_secret="test-secret",
        substrate_service=mock_substrate,
        workspace_id="slack-test",
    )


# ============================================================================
# API INTEGRATION TESTS
# ============================================================================


@pytest.mark.integration
class TestSlackAdapterSubstrateIntegration:
    """Test Slack adapter integration with memory substrate."""

    @pytest.mark.asyncio
    async def test_full_event_flow_writes_to_substrate(
        self, slack_adapter_with_mock_substrate, mock_substrate
    ):
        """Full flow: Event → Adapter → Substrate write."""
        adapter = slack_adapter_with_mock_substrate

        payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev456",
            "event": {
                "type": "message",
                "user": "U789",
                "channel": "C111",
                "text": "Hello L9 from Slack",
                "ts": "1234567890.123456",
                "thread_ts": None,
            },
        }

        # Call adapter
        status, response = await adapter._handle_event_callback(payload)

        # Verify response
        assert status == 200
        assert response["ok"] is True

        # Verify packet was written to substrate
        assert len(mock_substrate.packets) == 1

        packet = mock_substrate.packets[0]
        assert packet.packet_type == "slack.in"
        assert "Hello L9 from Slack" in packet.payload["text"]

    @pytest.mark.asyncio
    async def test_deduplication_via_substrate(
        self, slack_adapter_with_mock_substrate, mock_substrate
    ):
        """Duplicate detection works via substrate search."""
        adapter = slack_adapter_with_mock_substrate

        # First event
        payload1 = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev111",
            "event": {
                "type": "message",
                "user": "U789",
                "channel": "C111",
                "text": "First message",
                "ts": "1234567890.1",
            },
        }

        await adapter._handle_event_callback(payload1)
        assert len(mock_substrate.packets) == 1

        # Second event with SAME event_id (duplicate)
        payload2 = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev111",  # Same event_id
            "event": {
                "type": "message",
                "user": "U789",
                "channel": "C111",
                "text": "Duplicate message",
                "ts": "1234567890.2",
            },
        }

        await adapter._handle_event_callback(payload2)

        # Should NOT write duplicate (still 1 packet)
        assert len(mock_substrate.packets) == 1

    @pytest.mark.asyncio
    async def test_packet_metadata_structure(
        self, slack_adapter_with_mock_substrate, mock_substrate
    ):
        """Verify packet metadata matches repo schema."""
        adapter = slack_adapter_with_mock_substrate

        payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev456",
            "event": {
                "type": "app_mention",
                "user": "U789",
                "channel": "C111",
                "text": "<@UBOT> what is 2+2?",
                "ts": "1234567890.123456",
            },
        }

        await adapter._handle_event_callback(payload)

        packet = mock_substrate.packets[0]

        # Verify required fields
        assert packet.packet_type == "slack.in"
        assert packet.payload is not None
        assert packet.metadata is not None
        assert packet.provenance is not None
        assert packet.thread_id is not None

        # Verify metadata content
        assert packet.metadata.agent == "slack-webhook-adapter"
        assert packet.metadata.domain == "slack"

        # Verify provenance
        assert packet.provenance.source == "slack"

        # Verify payload
        assert "user" in packet.payload
        assert "channel" in packet.payload
        assert "text" in packet.payload
        assert "event_type" in packet.payload

    @pytest.mark.asyncio
    async def test_thread_uuid_determinism(
        self, slack_adapter_with_mock_substrate, mock_substrate
    ):
        """Thread UUID is deterministic across packets."""
        adapter = slack_adapter_with_mock_substrate

        team_id = "T123"
        channel_id = "C111"
        thread_ts = "1234567890.123456"

        # Same thread, different messages
        payload1 = {
            "type": "event_callback",
            "team_id": team_id,
            "event_id": "Ev1",
            "event": {
                "type": "message",
                "user": "U1",
                "channel": channel_id,
                "text": "Message 1",
                "ts": "1234567890.123456",
                "thread_ts": thread_ts,
            },
        }

        payload2 = {
            "type": "event_callback",
            "team_id": team_id,
            "event_id": "Ev2",
            "event": {
                "type": "message",
                "user": "U2",
                "channel": channel_id,
                "text": "Message 2",
                "ts": "1234567891.123456",
                "thread_ts": thread_ts,
            },
        }

        await adapter._handle_event_callback(payload1)
        await adapter._handle_event_callback(payload2)

        packet1 = mock_substrate.packets[0]
        packet2 = mock_substrate.packets[1]

        # Same thread should have same UUID
        assert packet1.thread_id == packet2.thread_id

    @pytest.mark.asyncio
    async def test_multiple_event_types(
        self, slack_adapter_with_mock_substrate, mock_substrate
    ):
        """Adapter handles multiple event types."""
        adapter = slack_adapter_with_mock_substrate

        # Message event
        msg_payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev1",
            "event": {
                "type": "message",
                "user": "U1",
                "channel": "C1",
                "text": "Hello",
                "ts": "1234567890.1",
            },
        }

        # App mention event
        mention_payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev2",
            "event": {
                "type": "app_mention",
                "user": "U2",
                "channel": "C1",
                "text": "<@UBOT> help",
                "ts": "1234567890.2",
            },
        }

        await adapter._handle_event_callback(msg_payload)
        await adapter._handle_event_callback(mention_payload)

        assert len(mock_substrate.packets) == 2
        assert mock_substrate.packets[0].payload["event_type"] == "message"
        assert mock_substrate.packets[1].payload["event_type"] == "app_mention"

    @pytest.mark.asyncio
    async def test_unsupported_event_type_skipped(
        self, slack_adapter_with_mock_substrate, mock_substrate
    ):
        """Unsupported event types are skipped."""
        adapter = slack_adapter_with_mock_substrate

        payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev1",
            "event": {
                "type": "file_shared",  # Unsupported
                "user": "U1",
                "channel": "C1",
            },
        }

        await adapter._handle_event_callback(payload)

        # No packet should be written
        assert len(mock_substrate.packets) == 0

    @pytest.mark.asyncio
    async def test_error_recovery(self, slack_adapter_with_mock_substrate, mock_substrate):
        """Adapter recovers from errors gracefully."""
        adapter = slack_adapter_with_mock_substrate

        # Invalid payload (missing required fields)
        invalid_payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev1",
            "event": None,  # None event
        }

        # Should not raise, should return 200 to Slack
        status, response = await adapter._handle_event_callback(invalid_payload)

        assert status == 200
        assert response["ok"] is True


# ============================================================================
# ACCEPTANCE TESTS
# ============================================================================


@pytest.mark.integration
@pytest.mark.acceptance
class TestSlackAdapterAcceptance:
    """Acceptance tests verifying adapter behavior against spec."""

    @pytest.mark.asyncio
    async def test_accepts_valid_slack_event_callback(
        self, slack_adapter_with_mock_substrate
    ):
        """✓ Adapter accepts valid event_callback from Slack."""
        adapter = slack_adapter_with_mock_substrate

        payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev456",
            "event": {
                "type": "message",
                "user": "U789",
                "channel": "C111",
                "text": "Hello",
                "ts": "1234567890.123456",
            },
        }

        status, _ = await adapter._handle_event_callback(payload)
        assert status == 200

    @pytest.mark.asyncio
    async def test_rejects_unsigned_requests(self):
        """✓ Adapter rejects requests with invalid signatures."""
        import hmac
        from slack_webhook_adapter import SlackSignatureVerifier

        verifier = SlackSignatureVerifier("secret")
        result = verifier.verify(
            str(int(time.time())),
            b'{"type":"event_callback"}',
            "v0=invalid",
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_writes_valid_packets(self, slack_adapter_with_mock_substrate):
        """✓ Adapter writes valid PacketEnvelopeIn to substrate."""
        adapter = slack_adapter_with_mock_substrate
        substrate = adapter.substrate_service

        payload = {
            "type": "event_callback",
            "team_id": "T123",
            "event_id": "Ev456",
            "event": {
                "type": "message",
                "user": "U789",
                "channel": "C111",
                "text": "Hello",
                "ts": "1234567890.123456",
            },
        }

        await adapter._handle_event_callback(payload)

        packets = await substrate.search_packets()
        assert len(packets) == 1

        packet = packets[0]
        assert isinstance(packet, PacketEnvelopeIn)
