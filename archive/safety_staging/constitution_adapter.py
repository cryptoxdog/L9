"""
Safety Module - Constitutional AI Adapter

This adapter exposes Constitutional AI rule enforcement capabilities through the standard
L9 module interface (handles/run).
"""

from .constitution import apply_rules, validate_constraints


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["safety_rules", "validate_constraints"]


def run(task: dict) -> dict:
    """
    Execute the task using this adapter.
    
    Args:
        task: Task dictionary with 'command' and other parameters
        
    Returns:
        dict: JSON-serializable result
    """
    try:
        command = task.get("command", "").lower().strip()
        
        if not handles(command):
            return {
                "success": False,
                "error": f"Command '{command}' not supported",
                "module": "safety_constitution"
            }
        
        # Route to appropriate function
        if command == "safety_rules":
            output = task.get("output", {})
            constitution = task.get("constitution", {})
            return apply_rules(output, constitution)
        
        elif command == "validate_constraints":
            output = task.get("output", {})
            constraints = task.get("constraints", {})
            constraint_type = task.get("constraint_type", "soft")
            return validate_constraints(output, constraints, constraint_type)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "safety_constitution"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "safety_constitution"
        }

