"""
L9 Memory Client Tests
======================

Tests for memory client with mocked HTTP.
No external services required - uses mocks.

Version: 1.0.0
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from clients.memory_client import MemoryClient, PacketEnvelopeIn
except ImportError as e:
    pytest.skip(f"Could not import clients.memory_client: {e}", allow_module_level=True)


# =============================================================================
# Test: Client initialization
# =============================================================================

def test_client_initialization():
    """
    Contract: MemoryClient can be instantiated.
    """
    client = MemoryClient(base_url="http://test:8080")
    assert client is not None
    assert client.base_url == "http://test:8080"


# =============================================================================
# Test: Write packet mock
# =============================================================================

@pytest.mark.asyncio
async def test_write_packet_mock():
    """
    Contract: MemoryClient can write packets (mocked HTTP).
    """
    client = MemoryClient(base_url="http://test:8080")
    
    packet = PacketEnvelopeIn(
        packet_type="test.event",
        payload={"message": "test"},
    )
    
    # Mock httpx.AsyncClient
    with patch('clients.memory_client.httpx.AsyncClient') as mock_client_class:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"packet_id": "test-123", "status": "ok"}
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await client.write_packet(packet)
        
        assert result is not None
        # Verify HTTP call was made
        mock_client.post.assert_called_once()


# =============================================================================
# Test: Search packets mock
# =============================================================================

@pytest.mark.asyncio
async def test_search_packets_mock():
    """
    Contract: MemoryClient can search packets (mocked HTTP).
    """
    client = MemoryClient(base_url="http://test:8080")
    
    # Mock httpx.AsyncClient
    with patch('clients.memory_client.httpx.AsyncClient') as mock_client_class:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "packets": [{"packet_id": "p1", "packet_type": "test.event"}],
            "total": 1,
        }
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await client.semantic_search(query="test", limit=10)
        
        assert result is not None
        # Verify HTTP call was made
        mock_client.post.assert_called_once()
