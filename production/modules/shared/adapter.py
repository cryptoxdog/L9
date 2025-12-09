"""
Shared Module Adapter
L9 v3.6 Standard Module
"""
import logging

logger = logging.getLogger(__name__)

# Simple in-memory cache
_cache = {}


def handles(command: str) -> bool:
    """Check if this module handles the given command."""
    shared_commands = [
        "shared_cache",
        "shared_retrieve",
        "shared",
        "cache"
    ]
    return command in shared_commands


def run(task: dict) -> dict:
    """Execute Shared task."""
    command = task.get("command")
    
    try:
        if command == "shared_cache":
            return _shared_cache(task)
        elif command == "shared_retrieve":
            return _shared_retrieve(task)
        else:
            return {
                "success": False,
                "module": "shared",
                "error": f"Unknown shared command: {command}"
            }
            
    except Exception as e:
        logger.exception(f"Shared execution failed: {e}")
        return {
            "success": False,
            "module": "shared",
            "operation": command,
            "error": str(e)
        }


def _shared_cache(task: dict) -> dict:
    """Cache data."""
    key = task.get("key", "")
    value = task.get("value")
    
    if not key:
        return {
            "success": False,
            "module": "shared",
            "operation": "cache",
            "error": "Key required"
        }
    
    _cache[key] = value
    
    return {
        "success": True,
        "module": "shared",
        "operation": "cache",
        "output": {
            "key": key,
            "cached": True
        }
    }


def _shared_retrieve(task: dict) -> dict:
    """Retrieve cached data."""
    key = task.get("key", "")
    
    if not key:
        return {
            "success": False,
            "module": "shared",
            "operation": "retrieve",
            "error": "Key required"
        }
    
    value = _cache.get(key)
    
    return {
        "success": True,
        "module": "shared",
        "operation": "retrieve",
        "output": {
            "key": key,
            "value": value,
            "found": value is not None
        }
    }

