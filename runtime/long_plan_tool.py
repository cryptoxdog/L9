"""
L9 Runtime - Long Plan Tool Implementation
==========================================

Tool implementations for long_plan.execute and long_plan.simulate.

These tools expose the LangGraph DAG as callable tools for agent L.

Version: 1.0.0
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from orchestration.long_plan_graph import execute_long_plan, simulate_long_plan
from runtime.tool_call_wrapper import tool_call_wrapper

logger = logging.getLogger(__name__)


async def long_plan_execute_tool(
    goal: str,
    constraints: List[str] | None = None,
    target_apps: List[str] | None = None,
    agent_id: str = "L",
    thread_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute a long plan through the LangGraph DAG.
    
    Args:
        goal: Goal description
        constraints: List of constraints
        target_apps: List of target apps (e.g., ["github", "notion", "vercel"])
        agent_id: Agent identifier (default: "L")
        thread_id: Optional thread identifier
        
    Returns:
        Dictionary with:
            - success: bool
            - state: Final DAG state
            - pending_actions: Actions requiring Igor approval
            - review_summary: Summary for review
    """
    if not goal:
        return {
            "success": False,
            "error": "goal is required",
        }
    
    try:
        # Use tool_call_wrapper to ensure logging
        result = await tool_call_wrapper(
            tool_name="long_plan.execute",
            tool_func=execute_long_plan,
            agent_id=agent_id,
            goal=goal,
            constraints=constraints or [],
            target_apps=target_apps or [],
            thread_id=thread_id,
        )
        
        logger.info(f"Long plan executed: goal={goal[:50]}..., success={result.get('success')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Long plan execution failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


async def long_plan_simulate_tool(
    goal: str,
    constraints: List[str] | None = None,
    target_apps: List[str] | None = None,
    agent_id: str = "L",
) -> Dict[str, Any]:
    """
    Simulate a long plan without executing (dry run).
    
    Args:
        goal: Goal description
        constraints: List of constraints
        target_apps: List of target apps
        agent_id: Agent identifier (default: "L")
        
    Returns:
        Dictionary with simulation results
    """
    if not goal:
        return {
            "success": False,
            "error": "goal is required",
        }
    
    try:
        # Use tool_call_wrapper to ensure logging
        result = await tool_call_wrapper(
            tool_name="long_plan.simulate",
            tool_func=simulate_long_plan,
            agent_id=agent_id,
            goal=goal,
            constraints=constraints or [],
            target_apps=target_apps or [],
        )
        
        logger.info(f"Long plan simulated: goal={goal[:50]}...")
        
        return result
        
    except Exception as e:
        logger.error(f"Long plan simulation failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


__all__ = [
    "long_plan_execute_tool",
    "long_plan_simulate_tool",
]

