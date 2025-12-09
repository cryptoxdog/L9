"""
PSR Module Adapter - Predictive State Representation v2 Interface

This adapter exposes predictive state inference capabilities through the standard
L9 module interface (handles/run).
"""

from .psr_v2 import psr_update, belief_update, predict_horizon, compute_likelihood


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["psr", "psr_update", "psr_predict", "psr_likelihood", "psr_belief"]


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
                "module": "psr"
            }
        
        # Route to appropriate function
        if command in ["psr", "psr_update"]:
            current_state = task.get("current_state", {})
            observation = task.get("observation", {})
            action = task.get("action", {})
            return psr_update(current_state, observation, action)
        
        elif command == "psr_predict":
            current_state = task.get("current_state", {})
            horizon = task.get("horizon", 5)
            action_sequence = task.get("action_sequence", [])
            return predict_horizon(current_state, horizon, action_sequence)
        
        elif command == "psr_likelihood":
            state = task.get("state", {})
            observation = task.get("observation", {})
            action = task.get("action", {})
            return compute_likelihood(state, observation, action)
        
        elif command == "psr_belief":
            belief = task.get("belief", {})
            observation = task.get("observation", {})
            transition_model = task.get("transition_model", {})
            return belief_update(belief, observation, transition_model)
        
        # Also handle belief_update if "belief" key present
        if "belief" in task:
            belief = task.get("belief", {})
            observation = task.get("observation", {})
            transition_model = task.get("transition_model", {})
            return belief_update(belief, observation, transition_model)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "psr"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "psr"
        }

