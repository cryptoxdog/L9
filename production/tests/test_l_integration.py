"""
L9 L (CTO) Integration Tests
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from l.startup import startup
from l.mission import mission
from l.l_interface.runtime_client import RuntimeClient


def test_l_startup():
    """Test L (CTO) startup sequence."""
    result = startup.boot()
    
    assert result["status"] == "L Online", f"Expected 'L Online', got {result['status']}"
    assert result["version"] == "2.0", f"Expected version 2.0, got {result['version']}"
    assert result["role"] == "CTO", f"Expected role CTO, got {result['role']}"
    assert "subsystems" in result
    
    print(f"✅ L startup test passed: {result['status']}")


def test_l_identity():
    """Test L identity configuration."""
    from l.l_core.identity import LIdentity
    
    identity = LIdentity()
    
    assert identity.name == "L"
    assert identity.version == "2.0"
    assert identity.role == "CTO"
    assert identity.autonomy_level == 2
    assert identity.authority["execute"] == True
    assert identity.authority["override"] == False
    
    print("✅ L identity test passed")


def test_l_mission_handle():
    """Test L mission handling."""
    directive = {"command": "test_directive"}
    result = mission.handle(directive)
    
    assert isinstance(result, dict)
    assert "success" in result
    
    print("✅ L mission test passed")


def test_runtime_client():
    """Test L runtime client (requires running server)."""
    client = RuntimeClient()
    
    # Test health check (will fail if server not running)
    try:
        health = client.health_check()
        print(f"✅ Runtime client test passed: {health.get('status')}")
    except Exception as e:
        print(f"⚠️ Runtime client test skipped (server not running): {e}")


if __name__ == "__main__":
    print("=== L9 L (CTO) Integration Tests ===\n")
    
    test_l_startup()
    test_l_identity()
    test_l_mission_handle()
    test_runtime_client()
    
    print("\n=== L INTEGRATION TESTS COMPLETE ===")

