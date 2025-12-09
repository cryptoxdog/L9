"""
Memory Ingestion Tests
======================

Tests for memory packet ingestion and retrieval.
"""

import pytest


@pytest.mark.asyncio
async def test_ingestion_roundtrip(memory_adapter):
    """Test that ingested packets can be retrieved."""
    packet = await memory_adapter.ingest({"content": "hello"})
    out = await memory_adapter.retrieve(packet["packet_id"])
    assert out["content"] == "hello"


@pytest.mark.asyncio
async def test_ingestion_assigns_packet_id(memory_adapter):
    """Test that ingestion assigns a unique packet ID."""
    packet = await memory_adapter.ingest({"content": "test"})
    
    assert "packet_id" in packet
    assert packet["packet_id"] is not None


@pytest.mark.asyncio
async def test_ingestion_assigns_timestamp(memory_adapter):
    """Test that ingestion assigns a timestamp."""
    packet = await memory_adapter.ingest({"content": "test"})
    
    assert "timestamp" in packet


@pytest.mark.asyncio
async def test_ingest_multiple_packets(memory_adapter):
    """Test ingesting multiple packets."""
    packets = []
    
    for i in range(10):
        packet = await memory_adapter.ingest({"content": f"message {i}"})
        packets.append(packet)
    
    # All should have unique IDs
    ids = [p["packet_id"] for p in packets]
    assert len(set(ids)) == 10


@pytest.mark.asyncio
async def test_retrieve_nonexistent(memory_adapter):
    """Test retrieving non-existent packet returns None."""
    result = await memory_adapter.retrieve("nonexistent-id")
    assert result is None


@pytest.mark.asyncio
async def test_ingest_with_metadata(memory_adapter):
    """Test ingesting packet with metadata."""
    packet = await memory_adapter.ingest({
        "content": "test",
        "metadata": {"source": "test", "priority": "high"},
    })
    
    retrieved = await memory_adapter.retrieve(packet["packet_id"])
    assert retrieved["metadata"]["source"] == "test"


@pytest.mark.asyncio
async def test_ingest_preserves_data(memory_adapter):
    """Test that all ingested data is preserved."""
    original = {
        "content": "test content",
        "tags": ["tag1", "tag2"],
        "nested": {"key": "value"},
    }
    
    packet = await memory_adapter.ingest(original)
    retrieved = await memory_adapter.retrieve(packet["packet_id"])
    
    assert retrieved["content"] == original["content"]
    assert retrieved["tags"] == original["tags"]
    assert retrieved["nested"] == original["nested"]

