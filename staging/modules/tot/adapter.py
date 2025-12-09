"""
ToT (Tree-of-Thoughts) Module Adapter
L9 v3.6 Standard Module
"""
import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

# Import ToT engine from v3.5 (will be refactored)
try:
    from core.reasoning.toth import TreeOfThoughts, Thought
except ImportError:
    logger.warning("ToT engine not available, using stub")
    TreeOfThoughts = None
    Thought = None


def handles(command: str) -> bool:
    """
    Check if this module handles the given command.
    
    Args:
        command: Command name
        
    Returns:
        True if this module handles the command
    """
    tot_commands = [
        "tot_expand",
        "tot_select",
        "tot_merge",
        "tot",
        "tree_of_thoughts"
    ]
    return command in tot_commands


def run(task: dict) -> dict:
    """
    Execute ToT task.
    
    Args:
        task: Task dict with 'command' and parameters
        
    Returns:
        JSON-serializable result dict
    """
    command = task.get("command")
    
    if not TreeOfThoughts:
        return {
            "success": False,
            "module": "tot",
            "error": "ToT engine not available"
        }
    
    try:
        if command == "tot_expand":
            return _tot_expand(task)
        elif command == "tot_select":
            return _tot_select(task)
        elif command == "tot_merge":
            return _tot_merge(task)
        else:
            return _tot_full_pipeline(task)
            
    except Exception as e:
        logger.exception(f"ToT execution failed: {e}")
        return {
            "success": False,
            "module": "tot",
            "operation": command,
            "error": str(e)
        }


def _tot_expand(task: dict) -> dict:
    """Expand proposal into thought branches."""
    proposal = task.get("proposal", {})
    k_branches = task.get("k_branches", 3)
    
    tot = TreeOfThoughts(k_branches=k_branches)
    thoughts = tot.expand(proposal)
    
    return {
        "success": True,
        "module": "tot",
        "operation": "expand",
        "output": {
            "thoughts": [
                {
                    "branch_id": t.branch_id,
                    "score": t.score,
                    "reasoning": t.reasoning,
                    "content": t.content
                }
                for t in thoughts
            ],
            "count": len(thoughts)
        }
    }


def _tot_select(task: dict) -> dict:
    """Select top thoughts from branches."""
    # Simplified selection logic
    thoughts_data = task.get("thoughts", [])
    top_m = task.get("top_m", 2)
    
    # Sort by score
    sorted_thoughts = sorted(thoughts_data, key=lambda t: t.get("score", 0), reverse=True)
    top_thoughts = sorted_thoughts[:top_m]
    
    return {
        "success": True,
        "module": "tot",
        "operation": "select",
        "output": {
            "top_thoughts": top_thoughts,
            "count": len(top_thoughts)
        }
    }


def _tot_merge(task: dict) -> dict:
    """Merge top thoughts into enriched proposal."""
    thoughts = task.get("thoughts", [])
    original_proposal = task.get("proposal", {})
    
    # Simple merge: combine insights from top thoughts
    enriched = original_proposal.copy()
    enriched["tot_insights"] = [t.get("reasoning") for t in thoughts]
    enriched["tot_confidence"] = sum(t.get("score", 0) for t in thoughts) / len(thoughts) if thoughts else 0
    
    return {
        "success": True,
        "module": "tot",
        "operation": "merge",
        "output": {
            "enriched_proposal": enriched
        }
    }


def _tot_full_pipeline(task: dict) -> dict:
    """Execute full ToT pipeline: expand → select → merge."""
    proposal = task.get("proposal", {})
    k_branches = task.get("k_branches", 3)
    top_m = task.get("top_m", 2)
    
    tot = TreeOfThoughts(k_branches=k_branches, top_m=top_m)
    
    # 1. Expand
    thoughts = tot.expand(proposal)
    
    # 2. Select
    top_thoughts = tot.select_top(thoughts)
    
    # 3. Merge
    enriched = tot.merge(top_thoughts)
    
    return {
        "success": True,
        "module": "tot",
        "operation": "full_pipeline",
        "output": {
            "thoughts_generated": len(thoughts),
            "top_thoughts": [
                {
                    "branch_id": t.branch_id,
                    "score": t.score,
                    "reasoning": t.reasoning
                }
                for t in top_thoughts
            ],
            "enriched_proposal": enriched
        }
    }
