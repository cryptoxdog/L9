# ══════════════════════════════════════════════════════════════════════════════
# Generated from Module-Spec v2.6
# module_id: calendar.adapter
# enforced_acceptance: ["valid_event_processed", "idempotent_replay_cached", "event_created_successfully", "event_updated_successfully", "aios_response_forwarded", ... (8 total)]
# ══════════════════════════════════════════════════════════════════════════════
# DORA META BLOCK — DO NOT EDIT MANUALLY (CI-owned)
# ══════════════════════════════════════════════════════════════════════════════
# __meta__ = {
#     "template_version": "2.6.0",
#     "spec_hash": "SPEC-447dc3be62b3",
#     "created_at": "2025-12-18T06:25:16.899340+00:00",
#     "created_by": "module_pipeline",
#     "last_updated_at": "2025-12-18T06:25:16.899340+00:00",
#     "last_updated_by": "module_pipeline",
#     "module_id": "calendar.adapter",
#     "file": "tests/test_calendar_adapter.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Calendar Adapter Tests
──────────────────────
Unit tests for Calendar Adapter

Auto-generated from Module-Spec v2.6.0

ACCEPTANCE_MIN ASSERTIONS:
- invalid_auth_rejected: route returns 401
- duplicate_event_deduped: dedupe=True AND AIOS NOT called
- packet_writes: in/out/error packets via mock assertions
- aios_call: made on success
- attachment_handling: metadata stored
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from api.adapters.calendar_adapter.adapters.calendar_adapter_adapter import (
    CalendarAdapterAdapter,
    CalendarAdapterRequest,
    PACKET_TYPE_IN,
    PACKET_TYPE_OUT,
    PACKET_TYPE_ERROR,
)


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_substrate_service():
    """Mock substrate service with tracking."""
    service = AsyncMock()
    service.write_packet = AsyncMock(return_value=MagicMock(packet_id=uuid4()))
    service.search_packets = AsyncMock(return_value=[])
    return service


@pytest.fixture
def mock_aios_client():
    """Mock AIOS runtime client."""
    client = AsyncMock()
    client.chat = AsyncMock(return_value={"status": "processed", "response": "ok"})
    return client


@pytest.fixture
def adapter(mock_substrate_service, mock_aios_client):
    """Create adapter with mocked dependencies."""
    return CalendarAdapterAdapter(
        substrate_service=mock_substrate_service,
        aios_runtime_client=mock_aios_client,
    )


@pytest.fixture
def sample_request():
    """Sample valid request."""
    return CalendarAdapterRequest(
        event_id="test-event-123",
        source="test",
        payload={"message": "Hello"},
    )


@pytest.fixture
def request_with_attachments():
    """Request with attachments."""
    return CalendarAdapterRequest(
        event_id="test-attach-456",
        source="test",
        payload={"message": "With attachments"},
        attachments=[
            {"filename": "test.pdf", "content_type": "application/pdf", "size": 1024},
        ],
    )


# ══════════════════════════════════════════════════════════════════════════════
# ACCEPTANCE_MIN: POSITIVE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestAcceptancePositive:
    """Positive acceptance criteria tests."""

    @pytest.mark.asyncio
    async def test_valid_request_processed(self, adapter, sample_request):
        """ACCEPTANCE: valid_email_processed - request succeeds."""
        response = await adapter.handle(sample_request)
        
        assert response.ok is True
        assert response.error is None

    @pytest.mark.asyncio
    async def test_idempotent_replay_cached(self, adapter, sample_request, mock_substrate_service, mock_aios_client):
        """ACCEPTANCE: idempotent_replay_cached - duplicate returns cached, AIOS NOT called."""
        # Setup: substrate returns existing packet on search
        mock_substrate_service.search_packets = AsyncMock(
            return_value=[{"packet_id": uuid4()}]
        )
        
        response = await adapter.handle(sample_request)
        
        # ASSERTION: dedupe is True
        assert response.dedupe is True
        assert response.ok is True
        
        # ASSERTION: AIOS client was NOT called on dedupe
        mock_aios_client.chat.assert_not_called()

    @pytest.mark.asyncio
    async def test_aios_response_forwarded(self, adapter, sample_request, mock_aios_client):
        """ACCEPTANCE: aios_response_forwarded - AIOS is called on success."""
        response = await adapter.handle(sample_request)
        
        assert response.ok is True
        
        # ASSERTION: AIOS client WAS called
        mock_aios_client.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_packet_written_on_success(self, adapter, sample_request, mock_substrate_service):
        """ACCEPTANCE: packet_written_on_success - in/out packets written."""
        await adapter.handle(sample_request)
        
        # ASSERTION: write_packet called at least twice (in + out)
        assert mock_substrate_service.write_packet.call_count >= 2
        
        # Verify packet types
        calls = mock_substrate_service.write_packet.call_args_list
        packet_types = [c[0][0].packet_type for c in calls]
        assert PACKET_TYPE_IN in packet_types
        assert PACKET_TYPE_OUT in packet_types

    @pytest.mark.asyncio
    async def test_attachment_handling(self, adapter, request_with_attachments, mock_substrate_service):
        """ACCEPTANCE: attachment_handling - attachment metadata stored in packet."""
        await adapter.handle(request_with_attachments)
        
        # ASSERTION: packet was written with attachment metadata
        assert mock_substrate_service.write_packet.call_count >= 2
        
        # Find the outbound packet
        for call in mock_substrate_service.write_packet.call_args_list:
            packet = call[0][0]
            if packet.packet_type == PACKET_TYPE_OUT:
                payload = packet.payload
                # ASSERTION: attachment_metadata field exists
                assert "attachment_metadata" in payload
                assert payload["attachment_metadata"]["count"] == 1


# ══════════════════════════════════════════════════════════════════════════════
# ACCEPTANCE_MIN: NEGATIVE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestAcceptanceNegative:
    """Negative acceptance criteria tests."""

    @pytest.mark.asyncio
    async def test_duplicate_event_dedupes(self, adapter, sample_request, mock_substrate_service, mock_aios_client):
        """ACCEPTANCE: duplicate_event_deduped - second request with same event_id is deduplicated."""
        # First request succeeds normally
        mock_substrate_service.search_packets = AsyncMock(return_value=[])
        response1 = await adapter.handle(sample_request)
        assert response1.dedupe is False
        
        # Configure substrate to return existing packet for second request
        mock_substrate_service.search_packets = AsyncMock(
            return_value=[{"packet_id": response1.packet_id}]
        )
        
        # Reset AIOS mock to verify it's NOT called
        mock_aios_client.chat.reset_mock()
        
        # Second request
        response2 = await adapter.handle(sample_request)
        
        # ASSERTION: dedupe is True
        assert response2.dedupe is True
        
        # ASSERTION: AIOS NOT called on duplicate
        mock_aios_client.chat.assert_not_called()


# ══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLING TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestErrorHandling:
    """Error handling and compensating action tests."""

    @pytest.mark.asyncio
    async def test_error_emits_error_packet(self, adapter, sample_request, mock_substrate_service, mock_aios_client):
        """ERROR: on failure, error packet is emitted."""
        # Configure AIOS to fail
        mock_aios_client.chat = AsyncMock(side_effect=Exception("AIOS failure"))
        
        response = await adapter.handle(sample_request)
        
        # ASSERTION: response indicates failure
        assert response.ok is False
        assert "AIOS failure" in response.error
        
        # ASSERTION: error packet was written
        packet_types = [c[0][0].packet_type for c in mock_substrate_service.write_packet.call_args_list]
        assert PACKET_TYPE_ERROR in packet_types

    @pytest.mark.asyncio
    async def test_thread_uuid_deterministic(self, adapter):
        """ACCEPTANCE: thread_uuid_deterministic - same inputs produce same UUID."""
        # This test enforces deterministic threading behavior
        request1 = CalendarAdapterRequest(event_id="test", payload={"key": "value"})
        request2 = CalendarAdapterRequest(event_id="test", payload={"key": "value"})
        
        context1 = adapter._generate_context(request1)
        context2 = adapter._generate_context(request2)
        
        # ASSERTION: deterministic threading - same inputs = same UUID
        assert context1.thread_uuid == context2.thread_uuid
        
        # Verify different inputs produce different UUIDs
        request3 = CalendarAdapterRequest(event_id="different", payload={"key": "other"})
        context3 = adapter._generate_context(request3)
        assert context1.thread_uuid != context3.thread_uuid
