"""
L9 MCP Memory Server - Main Entry Point

Run with:
    uvicorn mcp-memory.main:app --host 127.0.0.1 --port 9001
or:
    python -m mcp-memory.main
"""

import asyncio
import secrets
from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from .config import settings
from .db import init_db, close_db
from .routes import router
from .routes.memory import cleanup_task
from .mcpserver import get_mcp_tools, handle_tool_call, MCPToolCall
logger = structlog.get_logger(__name__)

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validate MCP API key from Authorization header.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    # Strip 'Bearer ' prefix if present
    if api_key.lower().startswith("bearer "):
        api_key = api_key[7:]

    if not secrets.compare_digest(api_key, settings.MCP_API_KEY):
        raise HTTPException(status_code=403, detail="Invalid API key")

    return api_key


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    App lifespan: init DB, start cleanup task, shutdown cleanly.
    """
    logger.info("Starting MCP Memory Server on %s:%s", settings.MCP_HOST, settings.MCP_PORT)

    # Initialize database
    await init_db()
    logger.info("✓ Database connected")

    # Start background cleanup task
    cleanup = asyncio.create_task(cleanup_task())

    yield

    # Shutdown
    cleanup.cancel()
    try:
        await cleanup
    except asyncio.CancelledError:
        pass

    await close_db()
    logger.info("MCP Memory Server shutdown complete")


app = FastAPI(
    title="L9 MCP Memory Server",
    description="MCP-compatible memory server with semantic search (pgvector)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST routes
app.include_router(router)


# ============================================================================
# MCP Protocol Endpoints
# ============================================================================


@app.get("/mcp/tools")
async def mcp_list_tools(_: str = Depends(verify_api_key)):
    """
    MCP protocol: list available tools.
    """
    return {"tools": [t.model_dump() for t in get_mcp_tools()]}


@app.post("/mcp/call")
async def mcp_call(
    request: Request,
    _: str = Depends(verify_api_key),
):
    """
    MCP protocol: call a tool.

    Expected JSON body:
        { "name": "saveMemory", "arguments": {...} }
    """
    body = await request.json()
    tool = MCPToolCall(name=body.get("name"), arguments=body.get("arguments", {}))

    # Extract userid from arguments (required for most calls)
    userid = tool.arguments.get("userid", "default")

    try:
        result = await handle_tool_call(tool, userid)
        return {"result": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("MCP tool call failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "mcp-memory.main:app",
        host=settings.MCP_HOST,
        port=settings.MCP_PORT,
        reload=(settings.MCP_ENV == "development"),
        log_level=settings.LOG_LEVEL.lower(),
    )

