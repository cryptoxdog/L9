"""
Pytest configuration and shared fixtures for Slack adapter tests.
Aligned with L9 testing patterns.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from memory.substratemodels import PacketWriteResult, PacketEnvelopeIn


@pytest.fixture
def event_loop():
    """Provide event loop for async tests."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def mock_write_result():
    """Create a mock PacketWriteResult."""
    return PacketWriteResult(
        packet_id=str(uuid4()),
        success=True,
        message="Packet stored successfully",
    )


@pytest.fixture
def mock_substrate_service(mock_write_result):
    """
    Canonical mock of MemorySubstrateService for tests.
    
    Matches repo patterns from GMP Integration Test specs.
    Uses AsyncMock for async methods.
    """
    service = AsyncMock()
    
    # These are the actual async methods in repo
    service.write_packet = AsyncMock(return_value=mock_write_result)
    service.search_packets = AsyncMock(return_value=[])
    
    return service


@pytest.fixture
def slack_signing_secret():
    """Slack app signing secret for tests."""
    return "test-signing-secret"


@pytest.fixture
def slack_workspace_id():
    """Slack workspace identifier."""
    return "slack-test"


# Markers for test categories
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", 
        "integration: mark test as integration test (requires multiple components)"
    )
    config.addinivalue_line(
        "markers",
        "unit: mark test as unit test (single component isolation)"
    )
    config.addinivalue_line(
        "markers",
        "acceptance: mark test as acceptance test (verifies contract)"
    )
