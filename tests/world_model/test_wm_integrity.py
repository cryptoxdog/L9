"""
World Model Graph Integrity Tests
=================================

Tests for world model graph relationships and integrity.
"""

import pytest


@pytest.mark.asyncio
async def test_graph_integrity(world_model):
    """Test graph maintains edge integrity."""
    a = await world_model.create_node("fact", {"text": "A"})
    b = await world_model.create_node("fact", {"text": "B"})
    await world_model.link(a, b, "supports")

    edges = await world_model.get_edges(a)
    assert any(e["type"] == "supports" for e in edges)


@pytest.mark.asyncio
async def test_edge_creation(world_model):
    """Test edge can be created between nodes."""
    a = await world_model.create_node("fact", {"text": "A"})
    b = await world_model.create_node("fact", {"text": "B"})

    edge_id = await world_model.link(a, b, "relates_to")

    assert edge_id is not None


@pytest.mark.asyncio
async def test_edge_direction(world_model):
    """Test edge direction is correct."""
    a = await world_model.create_node("fact", {"text": "A"})
    b = await world_model.create_node("fact", {"text": "B"})

    await world_model.link(a, b, "supports")

    # Outgoing from A
    edges_a = await world_model.get_edges(a, direction="outgoing")
    assert len(edges_a) == 1
    assert edges_a[0]["target"] == b

    # Incoming to B
    edges_b = await world_model.get_edges(b, direction="incoming")
    assert len(edges_b) == 1
    assert edges_b[0]["source"] == a


@pytest.mark.asyncio
async def test_multiple_edges(world_model):
    """Test multiple edges between nodes."""
    a = await world_model.create_node("fact", {"text": "A"})
    b = await world_model.create_node("fact", {"text": "B"})
    c = await world_model.create_node("fact", {"text": "C"})

    await world_model.link(a, b, "supports")
    await world_model.link(a, c, "contradicts")

    edges = await world_model.get_edges(a)
    assert len(edges) == 2


@pytest.mark.asyncio
async def test_edge_types(world_model):
    """Test different edge types."""
    a = await world_model.create_node("fact", {"text": "A"})
    b = await world_model.create_node("fact", {"text": "B"})

    edge_types = ["supports", "contradicts", "relates_to", "derived_from"]

    for edge_type in edge_types:
        await world_model.link(a, b, edge_type)

    edges = await world_model.get_edges(a)
    found_types = {e["type"] for e in edges}

    for edge_type in edge_types:
        assert edge_type in found_types


@pytest.mark.asyncio
async def test_edge_deletion(world_model):
    """Test edge can be deleted."""
    a = await world_model.create_node("fact", {"text": "A"})
    b = await world_model.create_node("fact", {"text": "B"})

    await world_model.link(a, b, "supports")

    # Should have edge
    edges = await world_model.get_edges(a)
    assert len(edges) == 1

    # Delete edge
    removed = await world_model.unlink(a, b, "supports")
    assert removed == 1

    # Should not have edge
    edges = await world_model.get_edges(a)
    assert len(edges) == 0


@pytest.mark.asyncio
async def test_cascade_delete(world_model):
    """Test deleting node removes its edges."""
    a = await world_model.create_node("fact", {"text": "A"})
    b = await world_model.create_node("fact", {"text": "B"})
    c = await world_model.create_node("fact", {"text": "C"})

    await world_model.link(a, b, "supports")
    await world_model.link(b, c, "supports")

    # Delete middle node
    await world_model.delete_node(b)

    # Edges should be cleaned up
    stats = world_model.get_stats()
    assert stats["edge_count"] == 0


@pytest.mark.asyncio
async def test_graph_stats(world_model):
    """Test graph statistics are accurate."""
    # Create nodes
    for i in range(5):
        await world_model.create_node("fact", {"text": f"node {i}"})

    stats = world_model.get_stats()

    assert stats["node_count"] == 5
    assert "node_types" in stats
    assert "fact" in stats["node_types"]


@pytest.mark.asyncio
async def test_edge_weight(world_model):
    """Test edge weight is preserved."""
    a = await world_model.create_node("fact", {"text": "A"})
    b = await world_model.create_node("fact", {"text": "B"})

    await world_model.link(a, b, "supports", weight=0.75)

    edges = await world_model.get_edges(a)
    assert edges[0]["weight"] == 0.75


@pytest.mark.asyncio
async def test_bidirectional_edges(world_model):
    """Test getting edges in both directions."""
    a = await world_model.create_node("fact", {"text": "A"})
    b = await world_model.create_node("fact", {"text": "B"})

    await world_model.link(a, b, "relates")
    await world_model.link(b, a, "relates")

    edges_both = await world_model.get_edges(a, direction="both")
    assert len(edges_both) == 2
