from fastapi import APIRouter

from .memory import router as memory_router
from .health import router as health_router

router = APIRouter()
router.include_router(memory_router, prefix="/memory", tags=["memory"])
router.include_router(health_router, prefix="", tags=["health"])

