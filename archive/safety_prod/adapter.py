"""
Safety Module Adapter
L9 v3.6 Standard Module
"""
import sys
from pathlib import Path
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

try:
    from core.governance.meta_oversight import MetaOversight
except ImportError:
    logger.warning("Meta-Oversight not available, using stub")
    MetaOversight = None


def handles(command: str) -> bool:
    """Check if this module handles the given command."""
    safety_commands = [
        "safety_monitor",
        "safety_validate",
        "safety",
        "meta_oversight"
    ]
    return command in safety_commands


def run(task: dict) -> dict:
    """Execute Safety task."""
    command = task.get("command")
    
    if not MetaOversight:
        return {
            "success": False,
            "module": "safety",
            "error": "Meta-Oversight not available"
        }
    
    try:
        if command == "safety_monitor":
            return _safety_monitor(task)
        elif command == "safety_validate":
            return _safety_validate(task)
        else:
            return _safety_full_pipeline(task)
            
    except Exception as e:
        logger.exception(f"Safety execution failed: {e}")
        return {
            "success": False,
            "module": "safety",
            "operation": command,
            "error": str(e)
        }


def _safety_monitor(task: dict) -> dict:
    """Monitor agent behavior."""
    agent_id = task.get("agent_id", "")
    action = task.get("action", {})
    
    oversight = MetaOversight()
    result = oversight.monitor_agent(agent_id, action)
    
    return {
        "success": True,
        "module": "safety",
        "operation": "monitor",
        "output": result
    }


def _safety_validate(task: dict) -> dict:
    """Validate action safety."""
    action = task.get("action", {})
    
    oversight = MetaOversight()
    validation = oversight.validate_action(action)
    
    return {
        "success": True,
        "module": "safety",
        "operation": "validate",
        "output": validation
    }


def _safety_full_pipeline(task: dict) -> dict:
    """Execute full safety pipeline."""
    agent_id = task.get("agent_id", "")
    action = task.get("action", {})
    
    oversight = MetaOversight()
    
    # 1. Monitor
    monitoring = oversight.monitor_agent(agent_id, action)
    
    # 2. Validate
    validation = oversight.validate_action(action)
    
    return {
        "success": True,
        "module": "safety",
        "operation": "full_pipeline",
        "output": {
            "monitoring": monitoring,
            "validation": validation
        }
    }
