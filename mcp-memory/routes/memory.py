import asyncio
import structlog
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

from ..config import settings
from ..db import execute, fetch_all, fetch_one
from ..embeddings import embed_text
from ..models import (
    MemoryResponse,
    MemoryStatsResponse,
    SaveMemoryRequest,
    SearchMemoryRequest,
    SearchMemoryResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/save", response_model=MemoryResponse)
async def save_memory_endpoint(req: SaveMemoryRequest) -> MemoryResponse:
    return await _save_memory(req)


async def save_memory(
    userid: str,
    content: str,
    kind: str,
    scope: str,
    duration: str,
    tags: Optional[List[str]],
    importance: float,
    metadata: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Internal helper used by MCP tool path.
    """
    req = SaveMemoryRequest(
        userid=userid,
        content=content,
        kind=kind,
        scope=scope,
        duration=duration,
        tags=tags,
        importance=importance,
        metadata=metadata,
    )
    resp = await _save_memory(req)
    return resp.model_dump()


async def _save_memory(req: SaveMemoryRequest) -> MemoryResponse:
    try:
        embedding = await embed_text(req.content)

        if req.duration == "short":
            table = "memory.shortterm"
            expires_at = datetime.utcnow() + timedelta(hours=settings.MEMORY_SHORTTERM_HOURS)
            query = (
                f"INSERT INTO {table} "
                "(userid, kind, content, embedding, importance, metadata, expiresat) "
                "VALUES ($1, $2, $3, $4::vector, $5, $6, $7) "
                "RETURNING id, userid, kind, content, importance, (metadata::text) AS metadatatext, createdat"
            )
            row = await fetch_one(
                query,
                req.userid,
                req.kind,
                req.content,
                embedding,
                req.importance or 1.0,
                req.metadata,
                expires_at,
            )
            if row is None:
                raise RuntimeError("Insert failed for short-term memory")

            await execute(
                "INSERT INTO memory.auditlog (operation, tablename, memoryid, userid, status, details) "
                "VALUES ($1, $2, $3, $4, $5, $6)",
                "INSERT",
                table,
                row["id"],
                req.userid,
                "success",
                {"duration": req.duration, "kind": req.kind},
            )

            return MemoryResponse(
                id=row["id"],
                userid=row["userid"],
                kind=row["kind"],
                content=row["content"],
                importance=row["importance"],
                tags=None,
                created_at=row["createdat"],
            )

        if req.duration == "medium":
            table = "memory.mediumterm"
            expires_at = datetime.utcnow() + timedelta(hours=settings.MEMORY_MEDIUMTERM_HOURS)
            query = (
                f"INSERT INTO {table} "
                "(userid, kind, content, embedding, importance, metadata, expiresat) "
                "VALUES ($1, $2, $3, $4::vector, $5, $6, $7) "
                "RETURNING id, userid, kind, content, importance, (metadata::text) AS metadatatext, createdat"
            )
            row = await fetch_one(
                query,
                req.userid,
                req.kind,
                req.content,
                embedding,
                req.importance or 1.0,
                req.metadata,
                expires_at,
            )
            if row is None:
                raise RuntimeError("Insert failed for medium-term memory")

            await execute(
                "INSERT INTO memory.auditlog (operation, tablename, memoryid, userid, status, details) "
                "VALUES ($1, $2, $3, $4, $5, $6)",
                "INSERT",
                table,
                row["id"],
                req.userid,
                "success",
                {"duration": req.duration, "kind": req.kind},
            )

            return MemoryResponse(
                id=row["id"],
                userid=row["userid"],
                kind=row["kind"],
                content=row["content"],
                importance=row["importance"],
                tags=None,
                created_at=row["createdat"],
            )

        if req.duration == "long":
            table = "memory.longterm"
            query = (
                "INSERT INTO memory.longterm "
                "(userid, scope, kind, content, embedding, importance, tags, metadata) "
                "VALUES ($1, $2, $3, $4, $5::vector, $6, $7, $8) "
                "RETURNING id, userid, kind, content, importance, tags, createdat"
            )
            row = await fetch_one(
                query,
                req.userid,
                req.scope,
                req.kind,
                req.content,
                embedding,
                req.importance or 1.0,
                req.tags,
                req.metadata,
            )
            if row is None:
                raise RuntimeError("Insert failed for long-term memory")

            await execute(
                "INSERT INTO memory.auditlog (operation, tablename, memoryid, userid, status, details) "
                "VALUES ($1, $2, $3, $4, $5, $6)",
                "INSERT",
                table,
                row["id"],
                req.userid,
                "success",
                {"duration": req.duration, "kind": req.kind},
            )

            return MemoryResponse(
                id=row["id"],
                userid=row["userid"],
                kind=row["kind"],
                content=row["content"],
                importance=row["importance"],
                tags=row["tags"],
                created_at=row["createdat"],
            )

        raise ValueError(f"Invalid duration {req.duration}")
    except Exception as exc:
        logger.exception("Error saving memory")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/search", response_model=SearchMemoryResponse)
async def search_memory_endpoint(req: SearchMemoryRequest) -> SearchMemoryResponse:
    return await _search_memory(req)


async def search_memory(
    userid: str,
    query: str,
    scopes: Optional[List[str]],
    kinds: Optional[List[str]],
    topk: int,
    threshold: float,
    duration: str,
) -> Dict[str, Any]:
    req = SearchMemoryRequest(
        userid=userid,
        query=query,
        scopes=scopes,
        kinds=kinds,
        topk=topk,
        threshold=threshold,
        duration=duration,
    )
    resp = await _search_memory(req)
    return resp.model_dump()


async def _search_memory(req: SearchMemoryRequest) -> SearchMemoryResponse:
    start_time = time.time()
    try:
        embed_start = time.time()
        query_embedding = await embed_text(req.query)
        embed_time_ms = (time.time() - embed_start) * 1000.0

        results: List[Dict[str, Any]] = []
        durations: List[str] = ["short", "medium", "long"] if req.duration == "all" else [req.duration]

        for d in durations:
            if d == "short":
                table = "memory.shortterm"
                where_clauses = ["userid = $1", "expiresat > CURRENT_TIMESTAMP"]
                params: List[Any] = [req.userid]
            elif d == "medium":
                table = "memory.mediumterm"
                where_clauses = ["userid = $1", "expiresat > CURRENT_TIMESTAMP"]
                params = [req.userid]
            else:
                table = "memory.longterm"
                where_clauses = ["userid = $1"]
                params = [req.userid]

            if d == "long" and req.scopes:
                idx_start = len(params) + 1
                placeholders = ", ".join(f"${i}" for i in range(idx_start, idx_start + len(req.scopes)))
                where_clauses.append(f"scope IN ({placeholders})")
                params.extend(req.scopes)

            if req.kinds:
                idx_start = len(params) + 1
                placeholders = ", ".join(f"${i}" for i in range(idx_start, idx_start + len(req.kinds)))
                where_clauses.append(f"kind IN ({placeholders})")
                params.extend(req.kinds)

            sim_param_idx = len(params) + 1
            threshold_idx = sim_param_idx + 1
            limit_idx = threshold_idx + 1

            where_clauses.append(f"1 - (embedding <=> ${sim_param_idx}::vector) >= ${threshold_idx}")
            params.extend([query_embedding, req.threshold or settings.VECTOR_SEARCH_THRESHOLD, req.topk or settings.VECTOR_SEARCH_TOP_K])

            where_sql = " AND ".join(where_clauses)
            query_sql = (
                f"SELECT id, userid, kind, content, importance, "
                f"1 - (embedding <=> ${sim_param_idx}::vector) AS similarity, "
                f"(metadata::text) AS metadatatext, createdat "
                f"FROM {table} "
                f"WHERE {where_sql} "
                f"ORDER BY similarity DESC "
                f"LIMIT ${limit_idx}"
            )
            params.append(req.topk or settings.VECTOR_SEARCH_TOP_K)

            rows = await fetch_all(query_sql, *params)
            results.extend(rows)

        results.sort(key=lambda x: x.get("similarity") or 0.0, reverse=True)
        results = results[: (req.topk or settings.VECTOR_SEARCH_TOP_K)]
        search_time_ms = (time.time() - start_time) * 1000.0

        memory_results = [
            MemoryResponse(
                id=r["id"],
                userid=r["userid"],
                kind=r["kind"],
                content=r["content"],
                importance=r["importance"],
                tags=None,
                created_at=r["createdat"],
                similarity=r.get("similarity"),
            )
            for r in results
        ]

        await execute(
            "INSERT INTO memory.auditlog (operation, userid, status, details) "
            "VALUES ($1, $2, $3, $4)",
            "SEARCH",
            req.userid,
            "success",
            {"query": req.query, "results_count": len(memory_results)},
        )

        return SearchMemoryResponse(
            results=memory_results,
            query_embedding_time_ms=embed_time_ms,
            search_time_ms=search_time_ms,
            total_results=len(memory_results),
        )
    except Exception as exc:
        logger.exception("Error searching memory")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/stats", response_model=MemoryStatsResponse)
async def stats_endpoint(userid: Optional[str] = None, duration: str = "all") -> MemoryStatsResponse:
    return await _get_memory_stats(userid, duration)


async def get_memory_stats(userid: Optional[str], duration: str) -> Dict[str, Any]:
    resp = await _get_memory_stats(userid, duration)
    return resp.model_dump()


async def _get_memory_stats(userid: Optional[str], duration: str) -> MemoryStatsResponse:
    where_user = "" if userid is None else "WHERE userid = $1"
    params: List[Any] = [] if userid is None else [userid]

    short_sql = f"SELECT COUNT(*) AS c, COALESCE(AVG(importance), 0) AS avgimp FROM memory.shortterm {where_user}"
    medium_sql = f"SELECT COUNT(*) AS c, COALESCE(AVG(importance), 0) AS avgimp FROM memory.mediumterm {where_user}"
    long_sql = f"SELECT COUNT(*) AS c, COALESCE(AVG(importance), 0) AS avgimp FROM memory.longterm {where_user}"
    unique_sql = "SELECT COUNT(DISTINCT userid) AS u FROM memory.longterm"

    short_row = await fetch_one(short_sql, *params) or {"c": 0, "avgimp": 0.0}
    medium_row = await fetch_one(medium_sql, *params) or {"c": 0, "avgimp": 0.0}
    long_row = await fetch_one(long_sql, *params) or {"c": 0, "avgimp": 0.0}
    unique_row = await fetch_one(unique_sql) or {"u": 0}

    total_count = short_row["c"] + medium_row["c"] + long_row["c"]
    avg_importance = (
        (short_row["avgimp"] + medium_row["avgimp"] + long_row["avgimp"]) / 3.0 if total_count > 0 else 0.0
    )

    return MemoryStatsResponse(
        shortterm_count=short_row["c"],
        mediumterm_count=medium_row["c"],
        longterm_count=long_row["c"],
        total_count=total_count,
        unique_users=unique_row["u"],
        avg_importance=avg_importance,
    )


async def delete_expired_memories(dryrun: bool = True) -> Dict[str, Any]:
    """
    Delete expired rows from shortterm and mediumterm.
    """
    if dryrun:
        short_sql = "SELECT COUNT(*) AS c FROM memory.shortterm WHERE expiresat <= CURRENT_TIMESTAMP"
        medium_sql = "SELECT COUNT(*) AS c FROM memory.mediumterm WHERE expiresat <= CURRENT_TIMESTAMP"
        short_row = await fetch_one(short_sql) or {"c": 0}
        medium_row = await fetch_one(medium_sql) or {"c": 0}
        return {
            "shortterm_expired": short_row["c"],
            "mediumterm_expired": medium_row["c"],
            "dryrun": True,
        }

    short_deleted = await execute("DELETE FROM memory.shortterm WHERE expiresat <= CURRENT_TIMESTAMP")
    medium_deleted = await execute("DELETE FROM memory.mediumterm WHERE expiresat <= CURRENT_TIMESTAMP")
    return {
        "shortterm_deleted": short_deleted,
        "mediumterm_deleted": medium_deleted,
        "dryrun": False,
    }


async def cleanup_task() -> None:
    """
    Background cleanup loop; started at app startup.
    """
    while True:
        try:
            interval_seconds = settings.MEMORY_CLEANUP_INTERVAL_MINUTES * 60
            await asyncio.sleep(interval_seconds)
            await execute("DELETE FROM memory.shortterm WHERE expiresat <= CURRENT_TIMESTAMP")
            await execute("DELETE FROM memory.mediumterm WHERE expiresat <= CURRENT_TIMESTAMP")
            logger.info("Cleanup task completed")
        except Exception as exc:
            logger.error("Cleanup task error: %s", exc, exc_info=True)

