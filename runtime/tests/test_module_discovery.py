"""
L9 Module Discovery Tests
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from l9_runtime.module_loader import ModuleLoader


def test_module_discovery():
    """Test that module loader discovers all 10 standard modules."""
    loader = ModuleLoader()
    modules = loader.discover_modules()
    
    expected_modules = [
        "tot", "ril", "psi", "ace", "safety",
        "shared", "utils", "transforms", "routing", "coordination"
    ]
    
    assert len(modules) == 10, f"Expected 10 modules, got {len(modules)}"
    
    for expected in expected_modules:
        assert expected in modules, f"Module {expected} not found"
    
    print(f"✅ Module discovery test passed: {len(modules)} modules")


def test_module_interfaces():
    """Test that all modules implement required interface."""
    loader = ModuleLoader()
    modules = loader.discover_modules()
    
    for name, module in modules.items():
        assert hasattr(module, "handles"), f"{name} missing handles()"
        assert hasattr(module, "run"), f"{name} missing run()"
        assert callable(module.handles), f"{name}.handles not callable"
        assert callable(module.run), f"{name}.run not callable"
    
    print(f"✅ Module interface test passed: all {len(modules)} modules compliant")


def test_module_handles():
    """Test that modules correctly identify their commands."""
    loader = ModuleLoader()
    modules = loader.discover_modules()
    
    # Test ToT
    if "tot" in modules:
        assert modules["tot"].handles("tot_expand") == True
        assert modules["tot"].handles("unknown_command") == False
    
    # Test Utils
    if "utils" in modules:
        assert modules["utils"].handles("util_metric") == True
        assert modules["utils"].handles("unknown_command") == False
    
    print("✅ Module handles test passed")


if __name__ == "__main__":
    print("=== L9 Module Discovery Tests ===\n")
    
    test_module_discovery()
    test_module_interfaces()
    test_module_handles()
    
    print("\n=== ALL TESTS PASSED ===")

