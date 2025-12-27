"""
L-CTO Tool Executors
====================

Concrete implementations of all tools L can invoke.
Each function is called by AgentExecutorService.dispatch_tool_call().

Version: 1.0.0
"""

from __future__ import annotations

import structlog
from typing import Any, Optional
from datetime import datetime

logger = structlog.get_logger(__name__)


# ============================================================================
# MEMORY SUBSTRATE TOOLS
# ============================================================================

async def memory_search(
    query: str,
    segment: str = "all",
    limit: int = 10,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Search L's memory substrate using semantic search.
    
    Args:
        query: Natural language search query
        segment: Memory segment to search ("all", "governance", "project", "session")
        limit: Maximum results to return (1-100)
        
    Returns:
        Dict with 'hits' list containing search results
    """
    try:
        from clients.memory_client import get_memory_client
        
        client = get_memory_client()
        result = await client.semantic_search(
            query=query,
            top_k=limit,
            agent_id=kwargs.get("agent_id"),
        )
        
        logger.info(f"Memory search: query='{query[:50]}...' segment={segment} hits={len(result.hits)}")
        
        return {
            "query": query,
            "segment": segment,
            "hits": [
                {
                    "embedding_id": str(hit.embedding_id),
                    "score": hit.score,
                    "payload": hit.payload,
                }
                for hit in result.hits
            ],
        }
    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        return {"error": str(e), "hits": []}


async def memory_write(
    packet: dict[str, Any],
    segment: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Write a packet to L's memory substrate.
    
    Args:
        packet: Packet data to write
        segment: Target memory segment
        
    Returns:
        Dict with write result status
    """
    try:
        from clients.memory_client import get_memory_client
        
        client = get_memory_client()
        
        # Build metadata with segment
        metadata = packet.get("metadata", {})
        metadata["segment"] = segment
        
        result = await client.write_packet(
            packet_type=packet.get("packet_type", "agent_memory"),
            payload=packet.get("payload", packet),
            metadata=metadata,
            provenance=packet.get("provenance"),
            confidence=packet.get("confidence"),
        )
        
        logger.info(f"Memory write: segment={segment} packet_id={result.packet_id}")
        
        return {
            "status": result.status,
            "packet_id": str(result.packet_id),
            "segment": segment,
            "written_tables": result.written_tables,
        }
    except Exception as e:
        logger.error(f"Memory write failed: {e}")
        return {"error": str(e), "status": "error"}


# ============================================================================
# GOVERNANCE TOOLS (High-Risk: Requires Igor Approval)
# ============================================================================

async def gmp_run(
    gmp_id: str,
    params: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Execute a GMP (Governance Management Process).
    
    WARNING: This is a high-risk tool that requires Igor approval.
    
    Args:
        gmp_id: GMP identifier (e.g., "GMP-L-CTO-P0-TOOLS")
        params: GMP execution parameters
        
    Returns:
        Dict with queued GMP task info
    """
    if params is None:
        params = {}
    
    try:
        from runtime.task_queue import TaskQueue
        
        task_queue = TaskQueue()
        
        # Enqueue GMP task
        task_id = await task_queue.enqueue({
            "kind": "gmp_run",
            "gmp_id": gmp_id,
            "params": params,
            "agent_id": kwargs.get("agent_id", "L"),
            "queued_at": datetime.utcnow().isoformat(),
        })
        
        logger.info(f"GMP run queued: gmp_id={gmp_id} task_id={task_id}")
        
        return {
            "status": "queued",
            "gmp_id": gmp_id,
            "task_id": task_id,
            "params": params,
            "queued_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"GMP run failed: {e}")
        return {"error": str(e), "status": "error"}


# ============================================================================
# VERSION CONTROL TOOLS (High-Risk: Requires Igor Approval)
# ============================================================================

async def git_commit(
    message: str,
    files: Optional[list[str]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Commit code changes to git repository.
    
    WARNING: This is a high-risk, destructive tool that requires Igor approval.
    
    Args:
        message: Commit message
        files: List of files to commit (empty = all staged)
        
    Returns:
        Dict with queued commit task info
    """
    if files is None:
        files = []
    
    try:
        from runtime.task_queue import TaskQueue
        
        task_queue = TaskQueue()
        
        # Enqueue git commit task
        task_id = await task_queue.enqueue({
            "kind": "git_commit",
            "message": message,
            "files": files,
            "agent_id": kwargs.get("agent_id", "L"),
            "queued_at": datetime.utcnow().isoformat(),
        })
        
        logger.info(f"Git commit queued: files={len(files)} msg='{message[:50]}...'")
        
        return {
            "status": "queued",
            "task_id": task_id,
            "message": message,
            "files": files,
            "queued_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Git commit failed: {e}")
        return {"error": str(e), "status": "error"}


# ============================================================================
# EXECUTION TOOLS (High-Risk: Requires Igor Approval)
# ============================================================================

async def mac_agent_exec_task(
    command: str,
    timeout: int = 30,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Execute command via Mac agent.
    
    WARNING: This is a high-risk, destructive tool that requires Igor approval.
    
    Args:
        command: Shell command to execute
        timeout: Timeout in seconds (5-300)
        
    Returns:
        Dict with execution result
    """
    try:
        from api.vps_executor import send_mac_task
        
        logger.info(f"Mac exec: command='{command[:50]}...' timeout={timeout}s")
        
        result = await send_mac_task(command, timeout)
        
        return {
            "status": "completed" if result.get("success") else "failed",
            "command": command,
            "output": result.get("output", ""),
            "exit_code": result.get("exit_code"),
            "error": result.get("error"),
        }
    except Exception as e:
        logger.error(f"Mac exec failed: {e}")
        return {"error": str(e), "status": "error"}


# ============================================================================
# EXTERNAL PROTOCOL TOOLS
# ============================================================================

async def mcp_call_tool(
    tool_name: str,
    params: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Call a tool via MCP (Model Context Protocol).
    
    Args:
        tool_name: Tool name in MCP catalog
        params: Tool parameters
        
    Returns:
        Dict with tool call result
    """
    if params is None:
        params = {}
    
    try:
        from runtime.mcp_tool import MCPToolClient
        
        client = MCPToolClient()
        result = await client.call_tool(tool_name, params)
        
        logger.info(f"MCP call: tool={tool_name} params_count={len(params)}")
        
        return {
            "status": "success",
            "tool_name": tool_name,
            "result": result,
        }
    except Exception as e:
        logger.error(f"MCP call failed: {e}")
        return {"error": str(e), "status": "error"}


# ============================================================================
# WORLD MODEL TOOLS
# ============================================================================

async def world_model_query(
    query_type: str,
    params: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Query the world model.
    
    Args:
        query_type: Query type (e.g., "entity_search", "get_entity", "list_entities")
        params: Query parameters
        
    Returns:
        Dict with query result
    """
    if params is None:
        params = {}
    
    try:
        from clients.world_model_client import get_world_model_client
        
        client = get_world_model_client()
        
        # Route to appropriate method based on query_type
        if query_type == "get_entity":
            entity = await client.get_entity(params.get("entity_id", ""))
            result = entity.model_dump() if entity else None
        elif query_type == "list_entities":
            entities = await client.list_entities(
                entity_type=params.get("entity_type"),
                min_confidence=params.get("min_confidence"),
                limit=params.get("limit", 100),
            )
            result = [e.model_dump() for e in entities]
        elif query_type == "state_version":
            state = await client.get_state_version()
            result = state.model_dump()
        else:
            # Default: health check
            result = await client.health_check()
        
        logger.info(f"World model query: type={query_type}")
        
        return {
            "status": "success",
            "query_type": query_type,
            "result": result,
        }
    except Exception as e:
        logger.error(f"World model query failed: {e}")
        return {"error": str(e), "status": "error"}


# ============================================================================
# KERNEL TOOLS
# ============================================================================

async def kernel_read(
    kernel_name: str,
    property: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Read a property from a kernel.
    
    Args:
        kernel_name: Kernel identifier (e.g., "identity", "safety", "execution")
        property: Property to read
        
    Returns:
        Dict with kernel property value
    """
    try:
        from runtime.kernel_loader import get_kernel_by_name
        
        kernel = get_kernel_by_name(kernel_name)
        
        if kernel is None:
            return {
                "error": f"Kernel '{kernel_name}' not found",
                "status": "error",
            }
        
        # Get property from kernel dict
        value = kernel.get(property)
        
        logger.info(f"Kernel read: kernel={kernel_name} property={property}")
        
        return {
            "kernel": kernel_name,
            "property": property,
            "value": value,
            "status": "success",
        }
    except Exception as e:
        logger.error(f"Kernel read failed: {e}")
        return {"error": str(e), "status": "error"}


# ============================================================================
# TOOL REGISTRY
# ============================================================================

# Map tool names to executor functions
TOOL_EXECUTORS: dict[str, Any] = {
    "memory_search": memory_search,
    "memory_write": memory_write,
    "gmp_run": gmp_run,
    "git_commit": git_commit,
    "mac_agent_exec_task": mac_agent_exec_task,
    "mcp_call_tool": mcp_call_tool,
    "world_model_query": world_model_query,
    "kernel_read": kernel_read,
}


def get_tool_executor(tool_name: str) -> Optional[Any]:
    """
    Get executor function for a tool by name.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Executor function or None if not found
    """
    return TOOL_EXECUTORS.get(tool_name)


def list_available_tools() -> list[str]:
    """
    List all available tool names.
    
    Returns:
        List of tool names
    """
    return list(TOOL_EXECUTORS.keys())

