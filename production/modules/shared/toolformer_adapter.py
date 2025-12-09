"""
Shared Utilities - Toolformer Adapter

This adapter exposes Toolformer-2 capabilities through the standard
L9 module interface (handles/run).
"""

from .toolformer import discover_tools, score_tool, compose_tools


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["tool_discover", "tool_score", "tool_compose"]


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
                "module": "shared_toolformer"
            }
        
        # Route to appropriate function
        if command == "tool_discover":
            context = task.get("context", {})
            tool_registry = task.get("tool_registry", None)
            return discover_tools(context, tool_registry)
        
        elif command == "tool_score":
            tool = task.get("tool", {})
            context = task.get("context", {})
            task_dict = task.get("task", {})
            return score_tool(tool, context, task_dict)
        
        elif command == "tool_compose":
            tools = task.get("tools", [])
            composition_strategy = task.get("composition_strategy", "sequential")
            return compose_tools(tools, composition_strategy)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "shared_toolformer"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "shared_toolformer"
        }

