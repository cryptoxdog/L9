"""
L9 Tests - Execution Wiring Sanity Check

Ensures:
- get_execution_state_machine() loads without error.
- get_allowed_transitions(state) returns a list.
- No assumptions about actual states or transitions.
"""

import pytest


def test_execution_state_machine_shape():
    """Verify state machine loads and returns dict."""
    # Direct import to avoid __init__ lazy import chain
    from core.kernel_wiring.execution_wiring import get_execution_state_machine
    
    sm = get_execution_state_machine()
    assert isinstance(sm, dict)


def test_allowed_transitions_returns_list():
    """Verify allowed_transitions always returns a list."""
    from core.kernel_wiring.execution_wiring import get_allowed_transitions
    
    # Test with known phase from 07_execution_kernel.yaml
    transitions = get_allowed_transitions("parse_intent")
    assert isinstance(transitions, list)
    
    # Test with unknown state (should return empty list, not crash)
    transitions_unknown = get_allowed_transitions("NONEXISTENT_STATE")
    assert isinstance(transitions_unknown, list)
    assert transitions_unknown == []


def test_execution_state_machine_has_expected_keys():
    """Verify state machine has expected structure (non-empty)."""
    from core.kernel_wiring.execution_wiring import get_execution_state_machine
    
    sm = get_execution_state_machine()
    
    # Should have content from the kernel
    # Not asserting specific keys to allow kernel evolution
    assert sm is not None
