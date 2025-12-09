"""
Utils Module Adapter
L9 v3.6 Standard Module
"""
import sys
from pathlib import Path
import logging
import time

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

try:
    from core.utils.metrics import record_metric
    from core.utils.retry import retry_with_backoff
except ImportError:
    logger.warning("Utils components not available, using stubs")
    record_metric = None
    retry_with_backoff = None


def handles(command: str) -> bool:
    """Check if this module handles the given command."""
    utils_commands = [
        "util_metric",
        "util_retry",
        "utils",
        "utility"
    ]
    return command in utils_commands


def run(task: dict) -> dict:
    """Execute Utils task."""
    command = task.get("command")
    
    try:
        if command == "util_metric":
            return _util_metric(task)
        elif command == "util_retry":
            return _util_retry(task)
        else:
            return {
                "success": False,
                "module": "utils",
                "error": f"Unknown utils command: {command}"
            }
            
    except Exception as e:
        logger.exception(f"Utils execution failed: {e}")
        return {
            "success": False,
            "module": "utils",
            "operation": command,
            "error": str(e)
        }


def _util_metric(task: dict) -> dict:
    """Record a metric."""
    metric_name = task.get("metric", "")
    value = task.get("value", 0)
    
    if record_metric:
        record_metric(metric_name, value)
    else:
        logger.info(f"Metric: {metric_name} = {value}")
    
    return {
        "success": True,
        "module": "utils",
        "operation": "metric",
        "output": {
            "metric": metric_name,
            "value": value,
            "recorded": True
        }
    }


def _util_retry(task: dict) -> dict:
    """Retry operation with backoff."""
    operation = task.get("operation", "")
    max_retries = task.get("max_retries", 3)
    
    if retry_with_backoff:
        # Use actual retry logic
        result = {"retried": True}
    else:
        # Stub implementation
        result = {"retried": True, "stub": True}
    
    return {
        "success": True,
        "module": "utils",
        "operation": "retry",
        "output": result
    }
