"""
Coordination Module - GNN Planning Adapter

This adapter exposes GNN-based cooperative planning capabilities through the standard
L9 module interface (handles/run).
"""

from .gnn_plan import gnn_plan, coordinate_agents


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["coordinate_gnn", "coordinate_plan", "gnn_coordinate"]


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
                "module": "coordination"
            }
        
        # Route to appropriate function
        if command in ["coordinate_gnn", "coordinate_plan"]:
            agents = task.get("agents", [])
            goals = task.get("goals", [])
            constraints = task.get("constraints", {})
            return gnn_plan(agents, goals, constraints)
        
        elif command == "gnn_coordinate":
            agent_graph = task.get("agent_graph", {})
            communication_edges = task.get("communication_edges", [])
            num_iterations = task.get("num_iterations", 5)
            return coordinate_agents(agent_graph, communication_edges, num_iterations)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "coordination"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "coordination"
        }

