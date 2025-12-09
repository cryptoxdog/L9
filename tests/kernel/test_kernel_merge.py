"""
Kernel Merge Tests
==================

Tests for kernel merging functionality.
"""

import sys
from pathlib import Path

# Add tests directory to path for mock imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tests"))

from mocks.kernel_mocks import merge_dicts


def test_governance_overrides_agent():
    """Test that governance values override agent values."""
    g = {"rules": {"truth": "strict"}}
    a = {"rules": {"truth": "loose"}}

    merged = merge_dicts(g, a)
    assert merged["rules"]["truth"] == "strict"


def test_merge_preserves_unique_keys():
    """Test that unique keys from both dicts are preserved."""
    g = {"governance_only": True}
    a = {"agent_only": True}
    
    merged = merge_dicts(g, a)
    assert merged["governance_only"] is True
    assert merged["agent_only"] is True


def test_merge_handles_nested_dicts():
    """Test that nested dictionaries are merged recursively."""
    g = {
        "level1": {
            "level2": {
                "gov_key": "gov_value",
            }
        }
    }
    a = {
        "level1": {
            "level2": {
                "agent_key": "agent_value",
            }
        }
    }
    
    merged = merge_dicts(g, a)
    assert merged["level1"]["level2"]["gov_key"] == "gov_value"
    assert merged["level1"]["level2"]["agent_key"] == "agent_value"


def test_merge_empty_governance():
    """Test merging with empty governance."""
    g = {}
    a = {"key": "value"}
    
    merged = merge_dicts(g, a)
    assert merged["key"] == "value"


def test_merge_empty_agent():
    """Test merging with empty agent."""
    g = {"key": "value"}
    a = {}
    
    merged = merge_dicts(g, a)
    assert merged["key"] == "value"


def test_merge_both_empty():
    """Test merging two empty dicts."""
    merged = merge_dicts({}, {})
    assert merged == {}


def test_merge_complex_structure():
    """Test merging complex nested structures."""
    g = {
        "memory": {
            "max_size": 1024,
            "policy": "strict",
        },
        "rules": {
            "safety": True,
        },
    }
    a = {
        "memory": {
            "max_size": 2048,  # Should be overridden
            "cache": True,
        },
        "tools": {
            "enabled": True,
        },
    }
    
    merged = merge_dicts(g, a)
    
    # Governance wins on conflicts
    assert merged["memory"]["max_size"] == 1024
    
    # Agent values preserved when no conflict
    assert merged["memory"]["cache"] is True
    assert merged["tools"]["enabled"] is True
    
    # Governance values preserved
    assert merged["memory"]["policy"] == "strict"
    assert merged["rules"]["safety"] is True

