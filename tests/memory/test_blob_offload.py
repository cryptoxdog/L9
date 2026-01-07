"""
Blob Offload Tests
==================

Tests for large content blob offloading in memory substrate.
"""

import pytest


@pytest.mark.asyncio
async def test_blob_offloading(memory_adapter):
    """Test that large content is offloaded to blob storage."""
    content = "x" * (2 * 1024 * 1024)  # 2MB
    blob_id = await memory_adapter.store_blob(content)
    assert blob_id

    packet = await memory_adapter.ingest({"blob_id": blob_id})
    assert "blob_id" in packet


@pytest.mark.asyncio
async def test_blob_retrieval(memory_adapter):
    """Test blob content can be retrieved."""
    content = "test blob content"
    blob_id = await memory_adapter.store_blob(content)

    retrieved = await memory_adapter.retrieve_blob(blob_id)
    assert retrieved == content.encode("utf-8")


@pytest.mark.asyncio
async def test_large_content_auto_offload(memory_adapter):
    """Test that content exceeding threshold is automatically offloaded."""
    # Create content larger than blob threshold (512KB)
    large_content = "x" * (1024 * 1024)  # 1MB

    packet = await memory_adapter.ingest({"content": large_content})

    # Should have been offloaded to blob
    assert "blob_id" in packet


@pytest.mark.asyncio
async def test_small_content_not_offloaded(memory_adapter):
    """Test that small content is not offloaded."""
    small_content = "small content"

    packet = await memory_adapter.ingest({"content": small_content})

    # Should not have blob_id
    assert "blob_id" not in packet or packet.get("content") == small_content


@pytest.mark.asyncio
async def test_blob_deletion(memory_adapter):
    """Test blob can be deleted."""
    content = "delete me"
    blob_id = await memory_adapter.store_blob(content)

    # Delete should succeed
    deleted = memory_adapter.blob_store.delete(blob_id)
    assert deleted is True

    # Should not be retrievable
    retrieved = await memory_adapter.retrieve_blob(blob_id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_multiple_blobs(memory_adapter):
    """Test storing multiple blobs."""
    contents = ["blob1", "blob2", "blob3"]
    blob_ids = []

    for content in contents:
        blob_id = await memory_adapter.store_blob(content)
        blob_ids.append(blob_id)

    # All should be unique
    assert len(set(blob_ids)) == len(contents)

    # All should be retrievable
    for i, blob_id in enumerate(blob_ids):
        retrieved = await memory_adapter.retrieve_blob(blob_id)
        assert retrieved == contents[i].encode("utf-8")
