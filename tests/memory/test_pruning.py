"""
Memory Pruning Tests
====================

Tests for vector index pruning functionality.
"""

import pytest


@pytest.mark.asyncio
async def test_pruning(memory_adapter):
    """Test pruning removes excess vectors."""
    # Add > max_vectors
    for i in range(30000):
        await memory_adapter.ingest({"content": f"text {i}"})

    pruned = await memory_adapter.run_pruning()
    # Should prune down to max_vectors (25000) or below
    assert pruned["active_vectors"] <= 25000
    # Should have pruned some vectors
    assert pruned["pruned"] > 0


@pytest.mark.asyncio
async def test_pruning_no_op_under_limit(memory_adapter):
    """Test pruning does nothing when under limit."""
    # Add just a few packets
    for i in range(10):
        await memory_adapter.ingest({"content": f"text {i}"})

    stats_before = memory_adapter.get_stats()
    pruned = await memory_adapter.run_pruning()
    stats_after = memory_adapter.get_stats()

    # Should not have pruned anything
    assert pruned["pruned"] == 0
    assert stats_before["vector_count"] == stats_after["vector_count"]


@pytest.mark.asyncio
async def test_pruning_returns_stats(memory_adapter):
    """Test pruning returns statistics."""
    for i in range(100):
        await memory_adapter.ingest({"content": f"text {i}"})

    result = await memory_adapter.run_pruning()

    assert "original_vectors" in result
    assert "active_vectors" in result
    assert "pruned" in result


@pytest.mark.asyncio
async def test_pruning_keeps_recent(memory_adapter):
    """Test that pruning keeps most recent vectors."""
    # Set a lower limit for testing
    memory_adapter.max_vectors = 10

    # Add 20 items
    for i in range(20):
        await memory_adapter.ingest({"content": f"text {i}"})

    # Prune
    await memory_adapter.run_pruning()

    # Should only have 10 vectors
    stats = memory_adapter.get_stats()
    assert stats["vector_count"] == 10


@pytest.mark.asyncio
async def test_multiple_prune_cycles(memory_adapter):
    """Test multiple prune cycles work correctly."""
    memory_adapter.max_vectors = 100

    # First batch
    for i in range(150):
        await memory_adapter.ingest({"content": f"batch1-{i}"})

    result1 = await memory_adapter.run_pruning()
    assert result1["active_vectors"] == 100

    # Second batch
    for i in range(150):
        await memory_adapter.ingest({"content": f"batch2-{i}"})

    result2 = await memory_adapter.run_pruning()
    assert result2["active_vectors"] == 100
