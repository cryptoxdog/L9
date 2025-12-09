"""
Relational Intelligence Adapter - Relation Transformer Interface

This adapter exposes relational intelligence capabilities through the standard
L9 module interface (handles/run).
"""

from .relation_transformer import rel_transform, graph_attention, message_pass, edge_prediction


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["ril_rel", "ril_graph_attention", "ril_message_pass", "ril_edge_prediction"]


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
                "module": "ril_rel"
            }
        
        # Route to appropriate function
        if command == "ril_rel":
            nodes = task.get("nodes", [])
            edges = task.get("edges", [])
            relation_types = task.get("relation_types", [])
            return rel_transform(nodes, edges, relation_types)
        
        elif command == "ril_graph_attention":
            nodes = task.get("nodes", [])
            edges = task.get("edges", [])
            num_heads = task.get("num_heads", 8)
            return graph_attention(nodes, edges, num_heads)
        
        elif command == "ril_message_pass":
            nodes = task.get("nodes", [])
            edges = task.get("edges", [])
            num_hops = task.get("num_hops", 2)
            return message_pass(nodes, edges, num_hops)
        
        elif command == "ril_edge_prediction":
            nodes = task.get("nodes", [])
            candidate_pairs = task.get("candidate_pairs", [])
            return edge_prediction(nodes, candidate_pairs)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "ril_rel"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "ril_rel"
        }

