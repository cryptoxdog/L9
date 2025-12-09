"""
L9 Governance Tests
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from l9_runtime.governance_hooks import GovernanceHooks
from governance.constitutional_engine import ConstitutionalEngine
from governance.hierarchical_authority_validator import HierarchicalAuthorityValidator
from governance.semantic_sanity_checker import SemanticSanityChecker


def test_governance_pre_check():
    """Test governance pre-check."""
    gov = GovernanceHooks()
    gov.initialize()
    
    result = gov.pre_check({"command": "test"})
    assert result["allowed"] == True
    
    print("✅ Governance pre-check test passed")


def test_constitutional_validation():
    """Test constitutional engine validation."""
    engine = ConstitutionalEngine()
    
    # Test valid action
    result1 = engine.validate({"action": "execute_module"})
    assert result1["valid"] == True
    
    # Test forbidden action
    result2 = engine.validate({"action": "privilege_escalation"})
    assert result2["valid"] == False
    assert len(result2["violations"]) > 0
    
    print("✅ Constitutional validation test passed")


def test_authority_validation():
    """Test hierarchical authority validation."""
    validator = HierarchicalAuthorityValidator()
    
    # Test L authority
    assert validator.validate_authority("L", "architect") == True
    assert validator.validate_authority("L", "shutdown") == False
    
    # Test Module authority
    assert validator.validate_authority("Modules", "execute") == True
    assert validator.validate_authority("Modules", "architect") == False
    
    print("✅ Authority validation test passed")


def test_semantic_sanity():
    """Test semantic sanity checker."""
    checker = SemanticSanityChecker()
    
    # Test valid directive
    result1 = checker.check({"command": "test", "param": "value"})
    assert result1["sane"] == True
    
    # Test invalid directive (missing command)
    result2 = checker.check({"param": "value"})
    assert result2["sane"] == False
    
    print("✅ Semantic sanity test passed")


if __name__ == "__main__":
    print("=== L9 Governance Tests ===\n")
    
    test_governance_pre_check()
    test_constitutional_validation()
    test_authority_validation()
    test_semantic_sanity()
    
    print("\n=== ALL GOVERNANCE TESTS PASSED ===")

