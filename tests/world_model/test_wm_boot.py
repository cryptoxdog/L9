"""
World Model Boot Tests
======================

Tests for world model initialization and status.
"""

import sys
from pathlib import Path

# Add tests directory to path for mock imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tests"))

from mocks.world_model_mocks import get_wm_status


def test_wm_boot():
    """Test world model boots successfully."""
    s = get_wm_status()
    assert s["ok"] is True


def test_wm_status_has_version():
    """Test status includes version info."""
    s = get_wm_status()
    assert "version" in s


def test_wm_status_has_counts():
    """Test status includes node and edge counts."""
    s = get_wm_status()
    
    assert "node_count" in s
    assert "edge_count" in s


def test_wm_status_has_health():
    """Test status includes health metrics."""
    s = get_wm_status()
    
    assert "health" in s
    assert "memory_mb" in s["health"]
    assert "latency_ms" in s["health"]


def test_wm_status_timestamp():
    """Test status includes last update timestamp."""
    s = get_wm_status()
    
    assert "last_update" in s


def test_wm_health_values_reasonable():
    """Test health values are in reasonable ranges."""
    s = get_wm_status()
    health = s["health"]
    
    # Memory should be positive
    assert health["memory_mb"] > 0
    
    # Latency should be small
    assert health["latency_ms"] < 1000

