"""
World Model Node Tests
======================

Tests for world model node operations.
"""

import pytest


@pytest.mark.asyncio
async def test_node_creation(world_model):
    """Test node can be created."""
    nid = await world_model.create_node("fact", {"text": "test"})
    node = await world_model.get_node(nid)
    assert node["type"] == "fact"


@pytest.mark.asyncio
async def test_node_has_id(world_model):
    """Test created node has an ID."""
    nid = await world_model.create_node("fact", {"text": "test"})

    assert nid is not None
    assert len(nid) > 0


@pytest.mark.asyncio
async def test_node_data_preserved(world_model):
    """Test node data is preserved."""
    data = {"text": "hello", "source": "test", "confidence": 0.9}
    nid = await world_model.create_node("fact", data)

    node = await world_model.get_node(nid)

    assert node["data"]["text"] == "hello"
    assert node["data"]["source"] == "test"
    assert node["data"]["confidence"] == 0.9


@pytest.mark.asyncio
async def test_node_type_preserved(world_model):
    """Test node type is preserved."""
    types = ["fact", "entity", "relation", "inference"]

    for node_type in types:
        nid = await world_model.create_node(node_type, {"text": "test"})
        node = await world_model.get_node(nid)

        assert node["type"] == node_type


@pytest.mark.asyncio
async def test_get_nonexistent_node(world_model):
    """Test getting non-existent node returns None."""
    node = await world_model.get_node("nonexistent-id")
    assert node is None


@pytest.mark.asyncio
async def test_node_update(world_model):
    """Test node can be updated."""
    nid = await world_model.create_node("fact", {"text": "original"})

    await world_model.update_node(nid, {"text": "updated"})

    node = await world_model.get_node(nid)
    assert node["data"]["text"] == "updated"


@pytest.mark.asyncio
async def test_node_deletion(world_model):
    """Test node can be deleted."""
    nid = await world_model.create_node("fact", {"text": "delete me"})

    # Should exist
    node = await world_model.get_node(nid)
    assert node is not None

    # Delete
    deleted = await world_model.delete_node(nid)
    assert deleted is True

    # Should not exist
    node = await world_model.get_node(nid)
    assert node is None


@pytest.mark.asyncio
async def test_multiple_nodes(world_model):
    """Test creating multiple nodes."""
    ids = []

    for i in range(10):
        nid = await world_model.create_node("fact", {"text": f"node {i}"})
        ids.append(nid)

    # All should be unique
    assert len(set(ids)) == 10

    # All should be retrievable
    for nid in ids:
        node = await world_model.get_node(nid)
        assert node is not None


@pytest.mark.asyncio
async def test_node_has_timestamps(world_model):
    """Test node has creation timestamp."""
    nid = await world_model.create_node("fact", {"text": "test"})
    node = await world_model.get_node(nid)

    assert "created_at" in node
