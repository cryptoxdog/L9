"""
Shared Utilities - FlashRAG Adapter

This adapter exposes FlashRAG capabilities through the standard
L9 module interface (handles/run).
"""

from .flashrag import flash_retrieve, build_index


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["flashrag", "fast_retrieve", "build_index"]


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
                "module": "shared_flashrag"
            }
        
        # Route to appropriate function
        if command == "flashrag" or command == "fast_retrieve":
            query = task.get("query", {})
            index = task.get("index", {})
            top_k = task.get("top_k", 10)
            return flash_retrieve(query, index, top_k)
        
        elif command == "build_index":
            documents = task.get("documents", [])
            index_type = task.get("index_type", "inverted")
            return build_index(documents, index_type)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "shared_flashrag"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "shared_flashrag"
        }

