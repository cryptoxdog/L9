"""
Error Recovery - Automatic error recovery strategies
"""
import logging
import time

logger = logging.getLogger(__name__)


def recover_from_error(error: Exception, context: dict) -> dict:
    """
    Attempt to recover from error.
    
    Recovery strategies:
    1. Retry with backoff
    2. Fallback to safe mode
    3. Escalate to L (CTO)
    
    Args:
        error: Exception that occurred
        context: Execution context
        
    Returns:
        Recovery result
    """
    logger.error(f"Error recovery triggered: {error}")
    
    error_type = type(error).__name__
    error_msg = str(error)
    
    # Strategy 1: Retry for transient errors
    if _is_transient_error(error):
        logger.info("Attempting retry strategy...")
        return {
            "recovered": False,
            "strategy": "retry",
            "error": error_msg,
            "recommendation": "Retry with exponential backoff"
        }
    
    # Strategy 2: Fallback for known errors
    if _has_fallback(error):
        logger.info("Attempting fallback strategy...")
        return {
            "recovered": False,
            "strategy": "fallback",
            "error": error_msg,
            "recommendation": "Use fallback implementation"
        }
    
    # Strategy 3: Escalate for unknown errors
    logger.info("Escalating to L (CTO)...")
    return {
        "recovered": False,
        "strategy": "escalate",
        "error": error_msg,
        "error_type": error_type,
        "context": context,
        "recommendation": "Manual intervention required"
    }


def _is_transient_error(error: Exception) -> bool:
    """Check if error is transient (network, timeout, etc)."""
    transient_types = [
        "TimeoutError",
        "ConnectionError",
        "ConnectionRefusedError",
        "ConnectionResetError"
    ]
    return type(error).__name__ in transient_types


def _has_fallback(error: Exception) -> bool:
    """Check if error has known fallback."""
    fallback_types = [
        "ImportError",
        "ModuleNotFoundError",
        "AttributeError"
    ]
    return type(error).__name__ in fallback_types


def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0):
    """
    Retry function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum retry attempts
        initial_delay: Initial delay in seconds
        
    Returns:
        Function result or raises last exception
    """
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff


if __name__ == "__main__":
    # Test error recovery
    print("=== Error Recovery Test ===")
    
    test_error = ConnectionError("Connection refused")
    result = recover_from_error(test_error, {"command": "test"})
    
    print(f"Strategy: {result['strategy']}")
    print(f"Recovered: {result['recovered']}")
    print(f"Recommendation: {result['recommendation']}")

