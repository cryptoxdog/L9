"""
Shared Utilities - Structured Long-Term Memory Adapter

This adapter exposes SLTM capabilities through the standard
L9 module interface (handles/run).
"""

from .sltm import store_memory, retrieve_memory, consolidate_memory


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["memory_store", "memory_retrieve", "memory_consolidate"]


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
                "module": "shared_sltm"
            }
        
        # Route to appropriate function
        if command == "memory_store":
            memory = task.get("memory", {})
            memory_type = task.get("memory_type", "episodic")
            index = task.get("index", None)
            return store_memory(memory, memory_type, index)
        
        elif command == "memory_retrieve":
            query = task.get("query", {})
            memory_type = task.get("memory_type", None)
            max_results = task.get("max_results", 10)
            return retrieve_memory(query, memory_type, max_results)
        
        elif command == "memory_consolidate":
            memories = task.get("memories", [])
            consolidation_strategy = task.get("consolidation_strategy", "merge")
            return consolidate_memory(memories, consolidation_strategy)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "shared_sltm"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "shared_sltm"
        }

