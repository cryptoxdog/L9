"""
L9 OS Routes
Basic health and system status endpoints.
"""

from fastapi import APIRouter

router = APIRouter(tags=["os"])


@router.get("/health")
async def os_health():
    """Health check for OS layer."""
    return {"status": "ok", "service": "os"}


@router.get("/status")
async def os_status():
    """System status endpoint."""
    return {
        "status": "operational",
        "version": "1.1.0",
        "components": {
            "memory_substrate": "active",
            "orchestrators": "ready",
        }
    }

