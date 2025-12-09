"""
Shared Utilities - Curriculum Learning Adapter

This adapter exposes curriculum learning capabilities through the standard
L9 module interface (handles/run).
"""

from .curriculum import generate_curriculum, estimate_difficulty


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["curriculum", "generate_curriculum", "estimate_difficulty"]


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
                "module": "shared_curriculum"
            }
        
        # Route to appropriate function
        if command == "curriculum" or command == "generate_curriculum":
            tasks = task.get("tasks", [])
            learner_state = task.get("learner_state", {})
            difficulty_metric = task.get("difficulty_metric", "complexity")
            return generate_curriculum(tasks, learner_state, difficulty_metric)
        
        elif command == "estimate_difficulty":
            task_dict = task.get("task", {})
            learner_state = task.get("learner_state", {})
            return estimate_difficulty(task_dict, learner_state)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "shared_curriculum"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "shared_curriculum"
        }

