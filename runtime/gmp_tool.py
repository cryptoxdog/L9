"""
L9 Runtime - GMP Tool Implementation
=====================================

Tool implementation for gmp_run that enqueues pending GMP tasks.

This tool is called by agent L to request GMP execution.
It only creates pending tasks - actual execution requires Igor's approval.

Version: 1.0.0
"""

from __future__ import annotations

import structlog
import time
from typing import Any, Dict

from runtime.gmp_worker import GMP_QUEUE, store_pending_task

logger = structlog.get_logger(__name__)


async def gmp_run_tool(
    gmp_markdown: str,
    repo_root: str,
    caller: str = "L",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    GMP run tool implementation.
    
    Enqueues a pending GMP task that requires Igor's approval before execution.
    
    Args:
        gmp_markdown: GMP markdown content to execute
        repo_root: Repository root path where GMP should run
        caller: Caller identifier (default: "L")
        metadata: Additional metadata dictionary
        
    Returns:
        Dictionary with:
            - task_id: Task identifier
            - status: "pending_igor_approval"
            - message: Human-readable message
            - summary: Summary blob for L to reference
    """
    if not gmp_markdown:
        return {
            "task_id": None,
            "status": "error",
            "message": "gmp_markdown is required",
            "error": "Missing gmp_markdown parameter",
        }
    
    if not repo_root:
        return {
            "task_id": None,
            "status": "error",
            "message": "repo_root is required",
            "error": "Missing repo_root parameter",
        }
    
    # Create task payload
    payload = {
        "type": "gmp_run",
        "gmp_markdown": gmp_markdown,
        "repo_root": repo_root,
        "caller": caller,
        "metadata": metadata or {},
        "approved_by_igor": False,  # Must be False - requires approval
        "status": "pending_igor_approval",
    }
    
    # Create task and store as pending (not in execution queue yet)
    try:
        from runtime.task_queue import QueuedTask
        from uuid import uuid4
        
        task_id = str(uuid4())
        task = QueuedTask(
            task_id=task_id,
            name="GMP Run",
            payload=payload,
            handler="gmp_worker",
            agent_id="L",
            priority=5,  # Default priority
            tags=["gmp", "pending_approval"],
        )
        
        # Store as pending (requires approval before execution)
        await store_pending_task(task)
        
        # Create summary for L
        summary = {
            "task_id": task_id,
            "repo_root": repo_root,
            "caller": caller,
            "gmp_preview": gmp_markdown[:200] + "..." if len(gmp_markdown) > 200 else gmp_markdown,
            "status": "pending_igor_approval",
        }
        
        logger.info(
            f"Created pending GMP task {task_id}: repo={repo_root}, caller={caller}"
        )
        
        # Log tool call via ToolGraph
        try:
            from core.tools.tool_graph import ToolGraph
            
            await ToolGraph.log_tool_call(
                tool_name="gmp_run",
                agent_id=caller,
                success=True,
                duration_ms=0,  # Enqueue is fast
                error=None,
            )
            
            # Also write to tool_audit memory segment
            try:
                from runtime.memory_helpers import memory_write
                
                await memory_write(
                    segment="tool_audit",
                    payload={
                        "tool_name": "gmp_run",
                        "agent_id": caller,
                        "task_id": task_id,
                        "status": "pending_igor_approval",
                        "success": True,
                    },
                    agent_id=caller,
                )
            except Exception as mem_err:
                logger.warning(f"Failed to write GMP tool audit to memory: {mem_err}")
                
        except Exception as log_err:
            logger.warning(f"Failed to log GMP tool call: {log_err}")
        
        return {
            "task_id": task_id,
            "status": "pending_igor_approval",
            "message": f"GMP task {task_id} created and pending Igor's approval",
            "summary": summary,
        }
        
    except Exception as e:
        logger.error(f"Failed to create GMP task: {e}", exc_info=True)
        
        # Log failed tool call
        try:
            from core.tools.tool_graph import ToolGraph
            
            await ToolGraph.log_tool_call(
                tool_name="gmp_run",
                agent_id=caller,
                success=False,
                duration_ms=0,
                error=str(e),
            )
        except Exception:
            pass
        
        return {
            "task_id": None,
            "status": "error",
            "message": f"Failed to create GMP task: {str(e)}",
            "error": str(e),
        }


__all__ = ["gmp_run_tool"]

