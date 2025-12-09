"""
Simulation Module - Dreamer-V3 Adapter

This adapter exposes Dreamer-V3 model-based RL capabilities through the standard
L9 module interface (handles/run).
"""

from .dreamer import simulate, latent_rollout


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["simulate", "simulate_rollout", "dream", "latent_rollout"]


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
                "module": "simulation"
            }
        
        # Route to appropriate function
        if command in ["simulate", "dream"]:
            latent_state = task.get("latent_state", {})
            action = task.get("action", {})
            horizon = task.get("horizon", 10)
            return simulate(latent_state, action, horizon)
        
        elif command in ["simulate_rollout", "latent_rollout"]:
            initial_state = task.get("initial_state", {})
            policy = task.get("policy", {})
            num_steps = task.get("num_steps", 20)
            return latent_rollout(initial_state, policy, num_steps)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "simulation"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "simulation"
        }

