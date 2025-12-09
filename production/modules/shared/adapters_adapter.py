"""
Shared Utilities - Adapter Management Adapter

This adapter exposes adapter management capabilities through the standard
L9 module interface (handles/run).
"""

from .adapters import load_adapter, fuse_adapters, manage_adapters


def handles(command: str) -> bool:
    """
    Check if this adapter handles the given command.
    
    Args:
        command: Command string to check
        
    Returns:
        bool: True if this adapter handles the command
    """
    return command in ["adapter_load", "adapter_fuse", "adapter_manage"]


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
                "module": "shared_adapters"
            }
        
        # Route to appropriate function
        if command == "adapter_load":
            adapter_path = task.get("adapter_path", "")
            adapter_type = task.get("adapter_type", "lora")
            return load_adapter(adapter_path, adapter_type)
        
        elif command == "adapter_fuse":
            adapters = task.get("adapters", [])
            fusion_strategy = task.get("fusion_strategy", "weighted")
            return fuse_adapters(adapters, fusion_strategy)
        
        elif command == "adapter_manage":
            model = task.get("model", {})
            adapters = task.get("adapters", [])
            operation = task.get("operation", "attach")
            return manage_adapters(model, adapters, operation)
        
        return {
            "success": False,
            "error": "Command routing failed",
            "module": "shared_adapters"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "module": "shared_adapters"
        }

