"""
Kernel Constraints Tests
========================

Tests for kernel constraint enforcement.
"""

import sys
from pathlib import Path

# Add tests directory to path for mock imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tests"))

import pytest
from mocks.kernel_mocks import KernelViolationError, load_kernels


def test_memory_size_constraint():
    """Test that memory size constraints are enforced."""
    ks = load_kernels()
    max_kb = ks.merged["memory"]["max_in_state_size_kb"]

    big = "x" * (max_kb * 2048)  # 2x allowed size

    with pytest.raises(KernelViolationError):
        ks.enforce_memory_constraints(big)


def test_memory_constraint_within_limit():
    """Test that content within limits passes."""
    ks = load_kernels()
    max_kb = ks.merged["memory"]["max_in_state_size_kb"]
    
    # Half the allowed size
    small = "x" * (max_kb * 512)
    
    # Should not raise
    result = ks.enforce_memory_constraints(small)
    assert result is True


def test_memory_constraint_exact_limit():
    """Test content at exact limit."""
    ks = load_kernels()
    max_kb = ks.merged["memory"]["max_in_state_size_kb"]
    
    # Exactly at limit
    exact = "x" * (max_kb * 1024)
    
    # Should not raise (at limit is OK)
    result = ks.enforce_memory_constraints(exact)
    assert result is True


def test_memory_constraint_bytes():
    """Test memory constraints with bytes input."""
    ks = load_kernels()
    max_kb = ks.merged["memory"]["max_in_state_size_kb"]
    
    big_bytes = b"x" * (max_kb * 2048)
    
    with pytest.raises(KernelViolationError):
        ks.enforce_memory_constraints(big_bytes)


def test_kernel_violation_error_attributes():
    """Test KernelViolationError has expected attributes."""
    error = KernelViolationError(
        "Test error",
        constraint="test_constraint",
        value=100,
    )
    
    assert str(error) == "Test error"
    assert error.constraint == "test_constraint"
    assert error.value == 100


def test_rate_limit_constraint():
    """Test rate limit enforcement."""
    ks = load_kernels()
    
    # Get google rate limit
    google_limit = ks.merged["rate_limits"]["google"]["max_per_hour"]
    
    # Within limit should pass
    assert ks.enforce_rate_limit("google", google_limit - 1) is True
    
    # Over limit should raise
    with pytest.raises(KernelViolationError):
        ks.enforce_rate_limit("google", google_limit + 1)

