"""
Health check module for symbolic computation.

Provides HTTP endpoint for health monitoring in production.
"""

import asyncio
from typing import Dict, Any
from symbolic_computation import SymbolicComputation


async def perform_health_check() -> Dict[str, Any]:
    """
    Perform comprehensive health check.

    Returns:
        Health status dictionary
    """
    engine = SymbolicComputation()

    try:
        # Test basic computation
        result = await engine.compute(
            "x + 1",
            {"x": 1.0},
            backend="numpy"
        )

        # Get metrics
        health = await engine.health_check()

        return {
            "status": "healthy" if result.success else "degraded",
            "details": health,
            "timestamp": str(asyncio.get_event_loop().time())
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": str(asyncio.get_event_loop().time())
        }


if __name__ == "__main__":
    result = asyncio.run(perform_health_check())
    print(result)

    # Exit with appropriate code
    exit(0 if result["status"] == "healthy" else 1)
