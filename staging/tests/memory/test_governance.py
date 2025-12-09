# tests/memory/test_governance.py

from memory.shared.governance_filter import governance_filter

def test_forbidden_key():
    bad = governance_filter.validate({"password": "abc"})
    assert bad["allowed"] is False

def test_payload_size_limit():
    huge = {"a": "x" * 30000}
    res = governance_filter.validate(huge)
    assert res["allowed"] is False

def test_valid_payload():
    ok = governance_filter.validate({"hello": "world"})
    assert ok["allowed"] is True

