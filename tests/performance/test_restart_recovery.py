"""
Restart Recovery Tests
======================

Tests for checkpoint save/restore functionality.
"""

import pytest


@pytest.mark.asyncio
async def test_restart_recovery(adapter):
    """Test that state can be recovered after restart."""
    step = {"step": 3, "plan": [1, 2, 3]}
    await adapter.save_checkpoint(step)

    new_adapter = adapter.fork()
    recovered = await new_adapter.load_checkpoint("thread-123")

    assert recovered["step"] == 3
    assert recovered["plan"] == [1, 2, 3]


@pytest.mark.asyncio
async def test_checkpoint_save(adapter):
    """Test checkpoint can be saved."""
    data = {"step": 1, "state": "running"}
    checkpoint_id = await adapter.save_checkpoint(data)
    
    assert checkpoint_id is not None


@pytest.mark.asyncio
async def test_checkpoint_contains_data(adapter):
    """Test saved checkpoint contains original data."""
    data = {
        "step": 5,
        "plan": ["a", "b", "c"],
        "evidence": [{"source": "test"}],
    }
    
    await adapter.save_checkpoint(data)
    recovered = await adapter.load_checkpoint("thread")
    
    assert recovered["step"] == 5
    assert recovered["plan"] == ["a", "b", "c"]
    assert recovered["evidence"] == [{"source": "test"}]


@pytest.mark.asyncio
async def test_checkpoint_timestamp(adapter):
    """Test checkpoint has timestamp."""
    await adapter.save_checkpoint({"step": 1})
    recovered = await adapter.load_checkpoint("thread")
    
    assert "timestamp" in recovered


@pytest.mark.asyncio
async def test_multiple_checkpoints(adapter):
    """Test multiple checkpoints can be saved."""
    for i in range(5):
        await adapter.save_checkpoint({"step": i})
    
    # Should have 5 checkpoints
    assert len(adapter.checkpoints) == 5


@pytest.mark.asyncio
async def test_latest_checkpoint_returned(adapter):
    """Test that most recent checkpoint is returned."""
    await adapter.save_checkpoint({"step": 1})
    await adapter.save_checkpoint({"step": 2})
    await adapter.save_checkpoint({"step": 3})
    
    recovered = await adapter.load_checkpoint("thread")
    
    # Should get the latest
    assert recovered["step"] == 3


@pytest.mark.asyncio
async def test_fork_preserves_checkpoints(adapter):
    """Test forked adapter preserves checkpoints."""
    await adapter.save_checkpoint({"step": 1})
    await adapter.save_checkpoint({"step": 2})
    
    forked = adapter.fork()
    
    assert len(forked.checkpoints) == 2


@pytest.mark.asyncio
async def test_recovery_after_fork(adapter):
    """Test recovery works after forking."""
    original_data = {
        "step": 10,
        "plan": ["research", "analyze", "report"],
        "state": {"key": "value"},
    }
    
    await adapter.save_checkpoint(original_data)
    
    # Fork (simulates restart)
    new_instance = adapter.fork()
    
    # Recover
    recovered = await new_instance.load_checkpoint("thread")
    
    assert recovered["step"] == original_data["step"]
    assert recovered["plan"] == original_data["plan"]
    assert recovered["state"] == original_data["state"]


@pytest.mark.asyncio
async def test_empty_checkpoint_load(adapter):
    """Test loading checkpoint when none exist returns None."""
    # No checkpoints saved
    recovered = await adapter.load_checkpoint("thread")
    
    # Should return None
    assert recovered is None


@pytest.mark.asyncio
async def test_complex_state_recovery(adapter):
    """Test recovery of complex nested state."""
    complex_state = {
        "step": 5,
        "plan": [
            {"id": 1, "action": "search", "params": {"query": "test"}},
            {"id": 2, "action": "analyze", "params": {"depth": 3}},
        ],
        "nested": {
            "level1": {
                "level2": {
                    "value": 42,
                }
            }
        },
        "lists": [[1, 2], [3, 4], [5, 6]],
    }
    
    await adapter.save_checkpoint(complex_state)
    
    forked = adapter.fork()
    recovered = await forked.load_checkpoint("thread")
    
    assert recovered["nested"]["level1"]["level2"]["value"] == 42
    assert recovered["lists"] == [[1, 2], [3, 4], [5, 6]]

