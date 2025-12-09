"""
Module Integrity Check - Validate module interface compliance
"""
import logging

logger = logging.getLogger(__name__)


def check_module_integrity(module, module_name: str = "unknown") -> dict:
    """
    Check module integrity and interface compliance.
    
    Validates:
    - has handles() method
    - has run() method
    - both are callable
    - both have correct signatures
    
    Args:
        module: Module to check
        module_name: Module name for logging
        
    Returns:
        Integrity check result
    """
    checks = {
        "has_handles": hasattr(module, "handles"),
        "has_run": hasattr(module, "run"),
        "handles_callable": callable(getattr(module, "handles", None)),
        "run_callable": callable(getattr(module, "run", None))
    }
    
    # Test handles() signature
    if checks["handles_callable"]:
        try:
            # Test with dummy command
            result = module.handles("test_command")
            checks["handles_returns_bool"] = isinstance(result, bool)
        except Exception as e:
            checks["handles_returns_bool"] = False
            checks["handles_error"] = str(e)
    else:
        checks["handles_returns_bool"] = False
    
    # Test run() signature
    if checks["run_callable"]:
        try:
            # Test with dummy task
            result = module.run({"command": "test"})
            checks["run_returns_dict"] = isinstance(result, dict)
            checks["run_has_success"] = "success" in result if isinstance(result, dict) else False
        except Exception as e:
            checks["run_returns_dict"] = False
            checks["run_error"] = str(e)
    else:
        checks["run_returns_dict"] = False
    
    # Overall validity
    valid = all([
        checks["has_handles"],
        checks["has_run"],
        checks["handles_callable"],
        checks["run_callable"],
        checks.get("handles_returns_bool", False),
        checks.get("run_returns_dict", False)
    ])
    
    result = {
        "valid": valid,
        "module": module_name,
        "checks": checks
    }
    
    if valid:
        logger.info(f"✅ Module {module_name} passed integrity check")
    else:
        logger.warning(f"❌ Module {module_name} failed integrity check")
    
    return result


if __name__ == "__main__":
    # Standalone execution - check all modules
    from l9_runtime.module_loader import ModuleLoader
    
    loader = ModuleLoader()
    modules = loader.discover_modules()
    
    print(f"=== Module Integrity Check ===")
    print(f"Checking {len(modules)} modules...")
    print()
    
    for name, module in modules.items():
        result = check_module_integrity(module, name)
        status = "✅" if result["valid"] else "❌"
        print(f"{status} {name}: {'PASS' if result['valid'] else 'FAIL'}")
    
    print()
    print(f"Total: {len(modules)} modules")

