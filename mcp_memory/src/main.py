"""FastAPI MCP Memory Server."""

import logging
import structlog
import time
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio

from src.config import settings
from src.db import init_db, close_db
from src.mcp_server import get_mcp_tools, MCPToolCall, handle_tool_call
from src.routes import memory, health

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = structlog.get_logger(__name__)

# =============================================================================
# Rate Limiting (in-memory, per-IP)
# =============================================================================
RATE_LIMIT_REQUESTS = 60  # Max requests per window
RATE_LIMIT_WINDOW = 60  # Window in seconds (1 minute)
FAILED_AUTH_LIMIT = 5  # Max failed auth attempts before block
FAILED_AUTH_BLOCK_SECONDS = 300  # Block for 5 minutes after too many failures

# Track requests per IP: {ip: [(timestamp, success), ...]}
request_log: dict = defaultdict(list)
# Track failed auth attempts: {ip: [timestamp, ...]}
failed_auth_log: dict = defaultdict(list)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info("✓ Database initialized")
    asyncio.create_task(memory.cleanup_task())
    yield
    logger.info("Closing database connections...")
    await close_db()
    logger.info("✓ Shutdown complete")


app = FastAPI(
    title="L9 MCP Memory Server",
    description="OpenAI embeddings + pgvector semantic search for Cursor",
    version="1.0.0",
    lifespan=lifespan,
)


def get_client_ip(request: Request) -> str:
    """Get client IP, respecting X-Forwarded-For for proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(ip: str) -> None:
    """Check if IP has exceeded rate limit. Raises 429 if so."""
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW
    
    # Clean old entries
    request_log[ip] = [(ts, ok) for ts, ok in request_log[ip] if ts > cutoff]
    
    if len(request_log[ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP: {ip}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")


def check_auth_block(ip: str) -> None:
    """Check if IP is blocked due to failed auth attempts."""
    now = time.time()
    cutoff = now - FAILED_AUTH_BLOCK_SECONDS
    
    # Clean old entries
    failed_auth_log[ip] = [ts for ts in failed_auth_log[ip] if ts > cutoff]
    
    if len(failed_auth_log[ip]) >= FAILED_AUTH_LIMIT:
        logger.warning(f"IP blocked due to failed auth attempts: {ip}")
        raise HTTPException(status_code=403, detail="Too many failed attempts. Blocked temporarily.")


def record_failed_auth(ip: str) -> None:
    """Record a failed authentication attempt."""
    failed_auth_log[ip].append(time.time())
    logger.warning(f"Failed auth attempt from IP: {ip} (total: {len(failed_auth_log[ip])})")


class CallerIdentity:
    """Caller identity determined from API key.
    
    See: mcp_memory/memory-setup-instructions.md for governance spec.
    - L: L-CTO kernel (full read/write/delete for shared userid)
    - C: Cursor IDE (read all, write/delete own memories only)
    """
    def __init__(self, caller_id: str, user_id: str):
        self.caller_id = caller_id  # "L" or "C"
        self.user_id = user_id      # Shared userid
        self.is_l = caller_id == "L"
        self.is_c = caller_id == "C"
    
    @property
    def creator(self) -> str:
        """Metadata creator value for this caller."""
        return "L-CTO" if self.is_l else "Cursor-IDE"
    
    @property
    def source(self) -> str:
        """Metadata source value for this caller."""
        return "l9-kernel" if self.is_l else "cursor-ide"


async def verify_api_key(request: Request, authorization: str = Header(None)) -> CallerIdentity:
    """Verify API key and return caller identity with rate limiting and brute-force protection.
    
    Returns CallerIdentity with:
    - caller_id: "L" or "C"
    - user_id: Shared userid (L_CTO_USER_ID)
    - creator/source: For metadata enforcement
    """
    ip = get_client_ip(request)
    
    # Check if IP is blocked
    check_auth_block(ip)
    
    # Check rate limit
    check_rate_limit(ip)
    
    # Record this request
    request_log[ip].append((time.time(), True))
    
    if not authorization or not authorization.startswith("Bearer "):
        record_failed_auth(ip)
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )
    token = authorization.replace("Bearer ", "")
    
    # Determine caller from API key
    if token == settings.MCP_API_KEY_L:
        return CallerIdentity(caller_id="L", user_id=settings.L_CTO_USER_ID)
    elif token == settings.MCP_API_KEY_C:
        return CallerIdentity(caller_id="C", user_id=settings.L_CTO_USER_ID)
    else:
        record_failed_auth(ip)
        raise HTTPException(status_code=403, detail="Invalid API key")


@app.get("/")
async def root():
    return {
        "status": "L9 MCP Memory Server",
        "version": "1.0.0",
        "mcp_version": "2025-03-26",
    }


@app.get("/health")
async def health_check():
    return await health.health_check()


@app.get("/mcp/tools")
async def list_tools(request: Request, caller: CallerIdentity = Depends(verify_api_key)):
    return {"tools": get_mcp_tools(), "caller": caller.caller_id}


@app.post("/mcp/call")
async def call_tool(request: Request, caller: CallerIdentity = Depends(verify_api_key)):
    """Execute MCP tool with caller-enforced governance.
    
    Caller identity (L or C) determines:
    - user_id: Shared L_CTO_USER_ID (L and C collaborate in same space)
    - metadata.creator: "L-CTO" or "Cursor-IDE" (enforced server-side)
    - metadata.source: "l9-kernel" or "cursor-ide" (enforced server-side)
    - write/delete scope: C can only modify own memories (creator="Cursor-IDE")
    """
    try:
        payload = await request.json()
        tool_name, tool_args = (
            payload.get("tool_name"),
            payload.get("arguments", {}),
        )
        # Use shared user_id from caller identity (not payload)
        # This enforces L + C operate in same semantic space
        user_id = caller.user_id
        tool_call = MCPToolCall(name=tool_name, arguments=tool_args)
        result = await handle_tool_call(tool_call, user_id, caller)
        return {"status": "success", "result": result, "caller": caller.caller_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Tool call error")
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(memory.router, prefix="/memory", tags=["memory"])


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.MCP_HOST,
        port=settings.MCP_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
