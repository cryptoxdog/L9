"""
RIL (Relational Intelligence Layer) Module Adapter
L9 v3.6 Standard Module
"""
import sys
from pathlib import Path
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

try:
    from core.agents.relational_intelligence import RelationalIntelligence
except ImportError:
    logger.warning("RIL engine not available, using stub")
    RelationalIntelligence = None


def handles(command: str) -> bool:
    """Check if this module handles the given command."""
    ril_commands = [
        "ril_analyze",
        "ril_adjust",
        "ril",
        "relational_intelligence"
    ]
    return command in ril_commands


def run(task: dict) -> dict:
    """Execute RIL task."""
    command = task.get("command")
    
    if not RelationalIntelligence:
        return {
            "success": False,
            "module": "ril",
            "error": "RIL engine not available"
        }
    
    try:
        if command == "ril_analyze":
            return _ril_analyze(task)
        elif command == "ril_adjust":
            return _ril_adjust(task)
        else:
            return _ril_full_pipeline(task)
            
    except Exception as e:
        logger.exception(f"RIL execution failed: {e}")
        return {
            "success": False,
            "module": "ril",
            "operation": command,
            "error": str(e)
        }


def _ril_analyze(task: dict) -> dict:
    """Analyze text for sentiment and tone."""
    text = task.get("text", "")
    
    ril = RelationalIntelligence()
    analysis = ril.analyze(text)
    
    return {
        "success": True,
        "module": "ril",
        "operation": "analyze",
        "output": analysis
    }


def _ril_adjust(task: dict) -> dict:
    """Adjust output based on RIL parameters."""
    text = task.get("text", "")
    empathy = task.get("empathy", 0.5)
    charisma = task.get("charisma", 0.5)
    professionalism = task.get("professionalism", 0.7)
    
    ril = RelationalIntelligence(empathy=empathy, charisma=charisma, professionalism=professionalism)
    adjusted = ril.adjust_output(text)
    
    return {
        "success": True,
        "module": "ril",
        "operation": "adjust",
        "output": {
            "adjusted_text": adjusted
        }
    }


def _ril_full_pipeline(task: dict) -> dict:
    """Execute full RIL pipeline: analyze → adjust."""
    text = task.get("text", "")
    
    ril = RelationalIntelligence()
    
    # 1. Analyze
    analysis = ril.analyze(text)
    
    # 2. Adjust
    adjusted = ril.adjust_output(text)
    
    return {
        "success": True,
        "module": "ril",
        "operation": "full_pipeline",
        "output": {
            "analysis": analysis,
            "adjusted_text": adjusted
        }
    }
