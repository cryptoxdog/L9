#!/usr/bin/env python3
"""
L9 Runtime - Minimal FastAPI Wrapper with Security
Clean architecture with L (CTO) integration
"""
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from l9_runtime.loop import runtime_loop
from l.startup import startup as l_startup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Key from environment
API_KEY = os.getenv("API_KEY")

# Simple rate limiter
rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds

# Initialize FastAPI
app = FastAPI(
    title="L9 Runtime",
    version="3.6.1",
    description="L9 Reasoning Agent with L (CTO) Integration and Security"
)

# Include memory test endpoints
from l.api.memory_test_endpoints import router as memory_test_router
app.include_router(memory_test_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(x_api_key: str = Header(None)) -> bool:
    """
    Verify API key from header.
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        True if valid, raises HTTPException if invalid
    """
    if not API_KEY:
        # API key not configured, allow access (development mode)
        logger.warning("API_KEY not configured - running in development mode")
        return True
    
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True


def check_rate_limit(client_id: str) -> bool:
    """
    Simple rate limiter.
    
    Args:
        client_id: Client identifier (IP or API key)
        
    Returns:
        True if within limits, raises HTTPException if exceeded
    """
    now = datetime.now()
    
    # Clean old entries
    rate_limit_store[client_id] = [
        timestamp for timestamp in rate_limit_store[client_id]
        if now - timestamp < timedelta(seconds=RATE_LIMIT_WINDOW)
    ]
    
    # Check limit
    if len(rate_limit_store[client_id]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s"
        )
    
    # Record request
    rate_limit_store[client_id].append(now)
    return True


@app.on_event("startup")
async def startup_event():
    """
    L9 Startup Sequence
    
    1. Boot L (CTO)
    2. Initialize L9 Runtime
    3. Discover and load modules
    """
    logger.info("=" * 60)
    logger.info("L9 STARTUP SEQUENCE")
    logger.info("=" * 60)
    
    # 1. Boot L (CTO)
    logger.info("Step 1: Booting L (CTO Agent)...")
    l_result = l_startup.boot()
    logger.info(f"L Status: {l_result['status']}")
    logger.info(f"L Version: {l_result['version']}")
    logger.info(f"L Role: {l_result['role']}")
    
    # Store L startup result in app state
    app.state.l_status = l_result
    
    # 2. Initialize L9 Runtime
    logger.info("Step 2: Initializing L9 Runtime Loop...")
    runtime_loop.initialize()
    logger.info(f"L9 Runtime: {len(runtime_loop.modules)} modules loaded")
    logger.info(f"Modules: {list(runtime_loop.modules.keys())}")
    
    # Store runtime in app state
    app.state.runtime_loop = runtime_loop
    
    logger.info("=" * 60)
    logger.info("L9 READY")
    logger.info("=" * 60)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "3.6.0",
        "l_status": app.state.l_status.get("status") if hasattr(app.state, "l_status") else "unknown",
        "runtime_initialized": runtime_loop.initialized
    }


@app.post("/directive")
async def execute_directive(
    directive: dict,
    request: Request,
    x_api_key: str = Header(None)
):
    """
    Execute directive through L9 Runtime with security.
    
    Requires X-API-Key header for authentication.
    Subject to rate limiting.
    
    Request body:
    {
        "command": "module_command",
        "param1": "value1",
        ...
    }
    """
    # Verify API key
    verify_api_key(x_api_key)
    
    # Check rate limit
    client_id = x_api_key or request.client.host
    check_rate_limit(client_id)
    
    try:
        result = runtime_loop.dispatch(directive)
        return JSONResponse(content=result)
    except Exception as e:
        logger.exception(f"Directive execution failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "module": "runtime",
                "operation": "dispatch",
                "output": None,
                "error": str(e)
            }
        )


@app.get("/modules")
async def list_modules(x_api_key: str = Header(None)):
    """List all loaded modules (requires API key)."""
    verify_api_key(x_api_key)
    
    return {
        "modules": list(runtime_loop.modules.keys()),
        "count": len(runtime_loop.modules)
    }


@app.get("/introspection")
async def introspection(x_api_key: str = Header(None)):
    """Get runtime introspection data (requires API key)."""
    verify_api_key(x_api_key)
    
    from l9_runtime.introspection_api import get_runtime_status
    return get_runtime_status()


@app.get("/l/status")
async def l_status(x_api_key: str = Header(None)):
    """Get L (CTO) status (requires API key)."""
    verify_api_key(x_api_key)
    
    if hasattr(app.state, "l_status"):
        return app.state.l_status
    else:
        return {"error": "L not initialized"}


@app.get("/l/heartbeat")
async def l_heartbeat():
    """L ↔ Runtime heartbeat endpoint (no auth required)."""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "runtime_initialized": runtime_loop.initialized,
        "l_online": hasattr(app.state, "l_status") and app.state.l_status.get("status") == "L Online"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "L9 Runtime",
        "version": "3.6.1",
        "architecture": "Clean architecture with L (CTO) integration",
        "endpoints": {
            "health": "/health",
            "directive": "/directive (POST)",
            "modules": "/modules",
            "introspection": "/introspection",
            "l_status": "/l/status",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting L9 Runtime on {host}:{port}")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

