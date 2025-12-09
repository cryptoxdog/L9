"""
Deliberate Reasoning Adapter - Tree-of-Thoughts Interface

This adapter exposes deliberate reasoning capabilities through the standard
L9 module interface (handles/run).
"""

from .deliberate import deliberate_sample, expand_branches, prune_tree, reflexive_rerank


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["tot_deliberate", "tot_expand", "tot_prune", "tot_rerank"]


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
                "module": "tot_deliberate"
            }
        
        # Route to appropriate function
        if command == "tot_deliberate":
            proposal = task.get("proposal", {})
            context = task.get("context", {})
            max_steps = task.get("max_steps", 5)
            temperature = task.get("temperature", 0.7)
            return deliberate_sample(proposal, context, max_steps, temperature)
        
        elif command == "tot_expand":
            current_state = task.get("current_state", {})
            beam_width = task.get("beam_width", 3)
            scoring_fn = task.get("scoring_fn", None)
            return expand_branches(current_state, beam_width, scoring_fn)
        
        elif command == "tot_prune":
            tree = task.get("tree", {})
            pruning_strategy = task.get("pruning_strategy", "score_threshold")
            threshold = task.get("threshold", 0.5)
            return prune_tree(tree, pruning_strategy, threshold)
        
        elif command == "tot_rerank":
            trajectories = task.get("trajectories", [])
            context = task.get("context", {})
            return reflexive_rerank(trajectories, context)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "tot_deliberate"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "tot_deliberate"
        }

