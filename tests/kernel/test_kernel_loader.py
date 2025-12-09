"""
Kernel Loader Tests
===================

Tests for kernel loading functionality.
"""

import sys
from pathlib import Path

# Add tests directory to path for mock imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tests"))

from mocks.kernel_mocks import load_kernels, KernelState


def test_loader_runs():
    """Test that kernel loader runs and returns valid state."""
    ks = load_kernels()
    assert isinstance(ks, KernelState)
    assert ks.governance
    assert ks.agent
    assert ks.merged


def test_loader_returns_governance_rules():
    """Test that governance rules are present in loaded kernel."""
    ks = load_kernels()
    assert "rules" in ks.governance
    assert "truth" in ks.governance["rules"]


def test_loader_returns_agent_capabilities():
    """Test that agent capabilities are present."""
    ks = load_kernels()
    assert "capabilities" in ks.agent


def test_merged_contains_both():
    """Test that merged kernel contains data from both sources."""
    ks = load_kernels()
    
    # Should have governance rules
    assert "rules" in ks.merged
    
    # Should have agent capabilities
    assert "capabilities" in ks.merged


def test_kernel_state_has_memory_config():
    """Test that kernel has memory configuration."""
    ks = load_kernels()
    assert "memory" in ks.merged
    assert "max_in_state_size_kb" in ks.merged["memory"]


def test_kernel_state_has_rate_limits():
    """Test that kernel has rate limit configuration."""
    ks = load_kernels()
    assert "rate_limits" in ks.merged

