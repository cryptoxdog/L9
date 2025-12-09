"""
Governance Enforcer - Validate directives against governance rules
"""
import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from governance.constitutional_engine import ConstitutionalEngine

logger = logging.getLogger(__name__)


def enforce_governance(directive: dict) -> dict:
    """
    Enforce governance rules on directive.
    
    Args:
        directive: Directive to validate
        
    Returns:
        Enforcement result
    """
    logger.info(f"Enforcing governance on: {directive.get('command')}")
    
    try:
        engine = ConstitutionalEngine()
        validation = engine.validate(directive)
        
        if not validation["valid"]:
            logger.warning(f"Governance violations: {validation['violations']}")
            return {
                "allowed": False,
                "violations": validation["violations"]
            }
        
        logger.info("Governance check passed")
        return {
            "allowed": True,
            "violations": []
        }
        
    except Exception as e:
        logger.error(f"Governance enforcement failed: {e}")
        return {
            "allowed": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Standalone execution - test governance
    print("=== Governance Enforcer Test ===")
    
    # Test 1: Valid directive
    result1 = enforce_governance({"command": "test_command"})
    print(f"Test 1 (valid): {'✅ PASS' if result1['allowed'] else '❌ FAIL'}")
    
    # Test 2: Forbidden action
    result2 = enforce_governance({"command": "privilege_escalation"})
    print(f"Test 2 (forbidden): {'✅ PASS' if not result2['allowed'] else '❌ FAIL'}")
    
    # Test 3: CEO override attempt
    result3 = enforce_governance({"command": "override_ceo"})
    print(f"Test 3 (ceo override): {'✅ PASS' if not result3['allowed'] else '❌ FAIL'}")
    
    print("\nGovernance enforcer operational")

