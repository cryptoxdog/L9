"""
L9 Introspection API - Runtime status and metrics

v3.6.1 Gap Fill Patch:
- Fixed import path to use absolute import
- Added exception safety (introspection never breaks)
- Added module count, governance status, event bus status
- Added telemetry counters
- Added circuit breaker status
"""
from typing import Dict, Any
import logging
import sys
from pathlib import Path

# Add project root to path for absolute import
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


def get_runtime_status() -> dict:
    """
    Get comprehensive runtime status with exception safety.
    
    Returns:
        Runtime status including modules, governance, event bus, and telemetry
    """
    try:
        from l9_runtime.loop import runtime_loop, telemetry_counters
        
        return {
            "status": "online" if runtime_loop.initialized else "offline",
            "modules_loaded": len(runtime_loop.modules),
            "modules": list(runtime_loop.modules.keys()),
            "governance_active": runtime_loop.governance.initialized if hasattr(runtime_loop.governance, 'initialized') else True,
            "event_bus_active": runtime_loop.event_bus.initialized if hasattr(runtime_loop.event_bus, 'initialized') else True,
            "audit_log_size": len(runtime_loop.governance.audit_log) if hasattr(runtime_loop.governance, 'audit_log') else 0,
            "event_history_size": len(runtime_loop.event_bus.event_history) if hasattr(runtime_loop.event_bus, 'event_history') else 0,
            "telemetry": dict(telemetry_counters),
            "circuit_breaker_open": list(runtime_loop.circuit_breaker_open) if hasattr(runtime_loop, 'circuit_breaker_open') else []
        }
    except Exception as e:
        logger.error(f"Introspection failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Introspection API encountered an error but did not crash"
        }


def get_module_list() -> list:
    """
    Get list of loaded modules with exception safety.
    
    Returns:
        List of module names
    """
    try:
        from l9_runtime.loop import runtime_loop
        return list(runtime_loop.modules.keys())
    except Exception as e:
        logger.error(f"get_module_list failed: {e}")
        return []


def get_module_info(module_name: str) -> dict:
    """
    Get detailed info about a specific module with exception safety.
    
    Args:
        module_name: Name of module
        
    Returns:
        Module information
    """
    try:
        from l9_runtime.loop import runtime_loop
        
        module = runtime_loop.modules.get(module_name)
        if not module:
            return {"error": "Module not found"}
        
        return {
            "name": module_name,
            "has_handles": hasattr(module, "handles"),
            "has_run": hasattr(module, "run"),
            "handles_callable": callable(getattr(module, "handles", None)),
            "run_callable": callable(getattr(module, "run", None)),
            "module_type": str(type(module)),
            "health": runtime_loop.get_module_health(module_name) if hasattr(runtime_loop, 'get_module_health') else {}
        }
    except Exception as e:
        logger.error(f"get_module_info failed: {e}")
        return {"error": str(e)}


def get_governance_status() -> dict:
    """
    Get governance system status with exception safety.
    
    Returns:
        Governance status and rules
    """
    try:
        from l9_runtime.loop import runtime_loop
        
        return {
            "initialized": runtime_loop.governance.initialized if hasattr(runtime_loop.governance, 'initialized') else False,
            "rules_loaded": len(runtime_loop.governance.rules) if hasattr(runtime_loop.governance, 'rules') else 0,
            "audit_log_entries": len(runtime_loop.governance.audit_log) if hasattr(runtime_loop.governance, 'audit_log') else 0
        }
    except Exception as e:
        logger.error(f"get_governance_status failed: {e}")
        return {"error": str(e)}


def get_event_bus_status() -> dict:
    """
    Get event bus status with exception safety.
    
    Returns:
        Event bus status and metrics
    """
    try:
        from l9_runtime.loop import runtime_loop
        
        return {
            "initialized": runtime_loop.event_bus.initialized if hasattr(runtime_loop.event_bus, 'initialized') else False,
            "listeners": {event_type: len(listeners) for event_type, listeners in runtime_loop.event_bus.listeners.items()},
            "event_history_size": len(runtime_loop.event_bus.event_history) if hasattr(runtime_loop.event_bus, 'event_history') else 0
        }
    except Exception as e:
        logger.error(f"get_event_bus_status failed: {e}")
        return {"error": str(e)}

