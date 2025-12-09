"""
Routing Module Adapter
L9 v3.6 Standard Module
"""
import sys
from pathlib import Path
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

try:
    from core.coordination.coplanner import PlanningAgent, ReasoningAgent
except ImportError:
    logger.warning("Coplanner not available, using stub")
    PlanningAgent = None
    ReasoningAgent = None


def handles(command: str) -> bool:
    """Check if this module handles the given command."""
    routing_commands = [
        "route_plan",
        "route_execute",
        "routing",
        "coplanner"
    ]
    return command in routing_commands


def run(task: dict) -> dict:
    """Execute Routing task."""
    command = task.get("command")
    
    if not PlanningAgent:
        return {
            "success": False,
            "module": "routing",
            "error": "Coplanner not available"
        }
    
    try:
        if command == "route_plan":
            return _route_plan(task)
        elif command == "route_execute":
            return _route_execute(task)
        else:
            return _routing_full_pipeline(task)
            
    except Exception as e:
        logger.exception(f"Routing execution failed: {e}")
        return {
            "success": False,
            "module": "routing",
            "operation": command,
            "error": str(e)
        }


def _route_plan(task: dict) -> dict:
    """Create execution plan."""
    objective = task.get("objective", "")
    context = task.get("context", {})
    
    planner = PlanningAgent()
    plan = planner.create_plan(objective, context)
    
    return {
        "success": True,
        "module": "routing",
        "operation": "plan",
        "output": {
            "plan": plan
        }
    }


def _route_execute(task: dict) -> dict:
    """Execute plan."""
    plan = task.get("plan", {})
    context = task.get("context", {})
    
    executor = ReasoningAgent()
    result = executor.execute(plan, context)
    
    return {
        "success": True,
        "module": "routing",
        "operation": "execute",
        "output": {
            "result": result
        }
    }


def _routing_full_pipeline(task: dict) -> dict:
    """Execute full routing pipeline: plan → execute."""
    objective = task.get("objective", "")
    context = task.get("context", {})
    
    # 1. Plan
    planner = PlanningAgent()
    plan = planner.create_plan(objective, context)
    
    # 2. Execute
    executor = ReasoningAgent()
    result = executor.execute(plan, context)
    
    return {
        "success": True,
        "module": "routing",
        "operation": "full_pipeline",
        "output": {
            "plan": plan,
            "result": result
        }
    }
