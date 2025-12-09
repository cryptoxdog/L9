"""
Transforms Module Adapter
L9 v3.6 Standard Module
"""
import json
import yaml
import logging

logger = logging.getLogger(__name__)


def handles(command: str) -> bool:
    """Check if this module handles the given command."""
    transform_commands = [
        "transform_json",
        "transform_yaml",
        "transform",
        "convert"
    ]
    return command in transform_commands


def run(task: dict) -> dict:
    """Execute Transforms task."""
    command = task.get("command")
    
    try:
        if command == "transform_json":
            return _transform_json(task)
        elif command == "transform_yaml":
            return _transform_yaml(task)
        else:
            return {
                "success": False,
                "module": "transforms",
                "error": f"Unknown transform command: {command}"
            }
            
    except Exception as e:
        logger.exception(f"Transform execution failed: {e}")
        return {
            "success": False,
            "module": "transforms",
            "operation": command,
            "error": str(e)
        }


def _transform_json(task: dict) -> dict:
    """Transform data to JSON."""
    data = task.get("data")
    
    try:
        json_str = json.dumps(data, indent=2)
        return {
            "success": True,
            "module": "transforms",
            "operation": "to_json",
            "output": {
                "json": json_str
            }
        }
    except Exception as e:
        return {
            "success": False,
            "module": "transforms",
            "operation": "to_json",
            "error": f"JSON serialization failed: {str(e)}"
        }


def _transform_yaml(task: dict) -> dict:
    """Transform data to YAML."""
    data = task.get("data")
    
    try:
        yaml_str = yaml.dump(data, default_flow_style=False)
        return {
            "success": True,
            "module": "transforms",
            "operation": "to_yaml",
            "output": {
                "yaml": yaml_str
            }
        }
    except Exception as e:
        return {
            "success": False,
            "module": "transforms",
            "operation": "to_yaml",
            "error": f"YAML serialization failed: {str(e)}"
        }
