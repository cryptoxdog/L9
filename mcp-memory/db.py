import structlog
from typing import Any, Dict, List, Optional

import asyncpg

from .config import settings

logger = structlog.get_logger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def init_db() -> None:
    """
    Initialize global asyncpg connection pool and ensure pgvector extension exists.
    """
    global _pool
    if _pool is not None:
        return

    _pool = await asyncpg.create_pool(
        dsn=settings.MEMORY_DSN,
        min_size=5,
        max_size=20,
        command_timeout=60,
    )

    async with _pool.acquire() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    logger.info("Database connection pool initialized for MCP memory server")


async def close_db() -> None:
    """
    Close the global connection pool.
    """
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


async def execute(query: str, *args: Any) -> str:
    """
    Execute a statement and return command status string.
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized")

    async with _pool.acquire() as conn:
        return await conn.execute(query, *args)


async def fetch_one(query: str, *args: Any) -> Optional[Dict[str, Any]]:
    """
    Fetch a single row as a dict.
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized")

    async with _pool.acquire() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row is not None else None


async def fetch_all(query: str, *args: Any) -> List[Dict[str, Any]]:
    """
    Fetch all rows as list of dicts.
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized")

    async with _pool.acquire() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(r) for r in rows]


async def insert_many(query: str, args_list: List[tuple]) -> int:
    """
    Insert multiple rows using executemany, return affected row count.
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized")

    async with _pool.acquire() as conn:
        # asyncpg executemany returns None; we approximate by len(args_list)
        await conn.executemany(query, args_list)
        return len(args_list)

