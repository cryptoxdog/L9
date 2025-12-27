from fastapi import APIRouter

from ..config import settings
from ..db import _pool

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict:
    db_ok = _pool is not None
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "mcp_version": "2025-03-26",
        "embed_model": settings.OPENAI_EMBED_MODEL,
    }

