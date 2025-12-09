"""
PSI (Prerequisite Sequence Intelligence) Module Adapter
L9 v3.6 Standard Module
"""
import sys
from pathlib import Path
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

try:
    from core.learning.psi_kt import PSIKTTracer
except ImportError:
    logger.warning("PSI-KT engine not available, using stub")
    PSIKTTracer = None


def handles(command: str) -> bool:
    """Check if this module handles the given command."""
    psi_commands = [
        "psi_trace",
        "psi_infer",
        "psi",
        "prerequisite_sequence"
    ]
    return command in psi_commands


def run(task: dict) -> dict:
    """Execute PSI task."""
    command = task.get("command")
    
    if not PSIKTTracer:
        return {
            "success": False,
            "module": "psi",
            "error": "PSI-KT engine not available"
        }
    
    try:
        if command == "psi_trace":
            return _psi_trace(task)
        elif command == "psi_infer":
            return _psi_infer(task)
        else:
            return _psi_full_pipeline(task)
            
    except Exception as e:
        logger.exception(f"PSI execution failed: {e}")
        return {
            "success": False,
            "module": "psi",
            "operation": command,
            "error": str(e)
        }


def _psi_trace(task: dict) -> dict:
    """Trace prerequisite sequences."""
    concept = task.get("concept", "")
    context = task.get("context", {})
    
    tracer = PSIKTTracer()
    trace_result = tracer.trace(concept, context)
    
    return {
        "success": True,
        "module": "psi",
        "operation": "trace",
        "output": trace_result
    }


def _psi_infer(task: dict) -> dict:
    """Infer knowledge transfer paths."""
    source = task.get("source", "")
    target = task.get("target", "")
    
    tracer = PSIKTTracer()
    inference = tracer.infer_transfer(source, target)
    
    return {
        "success": True,
        "module": "psi",
        "operation": "infer",
        "output": inference
    }


def _psi_full_pipeline(task: dict) -> dict:
    """Execute full PSI pipeline."""
    concept = task.get("concept", "")
    
    tracer = PSIKTTracer()
    trace = tracer.trace(concept, {})
    
    return {
        "success": True,
        "module": "psi",
        "operation": "full_pipeline",
        "output": {
            "trace": trace
        }
    }
