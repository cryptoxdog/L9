"""
Safety Module - Reflexion Adapter

This adapter exposes Reflexion-2 self-critique capabilities through the standard
L9 module interface (handles/run).
"""

from .reflexion import reflect, self_critique, prune_unsafe, detect_hallucination


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["reflect", "safety_critique", "safety_prune", "detect_hallucination"]


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
                "module": "safety_reflexion"
            }
        
        # Route to appropriate function
        if command == "reflect":
            trajectory = task.get("trajectory", {})
            task_dict = task.get("task", {})
            feedback = task.get("feedback", None)
            return reflect(trajectory, task_dict, feedback)
        
        elif command == "safety_critique":
            output = task.get("output", {})
            constraints = task.get("constraints", {})
            return self_critique(output, constraints)
        
        elif command == "safety_prune":
            trajectories = task.get("trajectories", [])
            safety_rules = task.get("safety_rules", {})
            return prune_unsafe(trajectories, safety_rules)
        
        elif command == "detect_hallucination":
            output = task.get("output", {})
            context = task.get("context", {})
            return detect_hallucination(output, context)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "safety_reflexion"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "safety_reflexion"
        }

