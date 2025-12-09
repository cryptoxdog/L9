"""
L9 Reasoning Agent V3.5 - FastAPI Runtime
Production deployment entry point
"""
import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="L9 Reasoning Agent",
    version="3.5",
    description="L9 Reasoning Agent Runtime API"
)

# Environment validation
REQUIRED_ENV_VARS = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_ANON_KEY"
]

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    # Don't exit - let the app start but log the error


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Traefik and monitoring.
    Returns 200 OK if service is healthy.
    """
    health_status = {
        "status": "ok",
        "service": "l9-runtime",
        "version": "3.5"
    }
    
    # Check environment variables
    env_status = {}
    for var in REQUIRED_ENV_VARS:
        env_status[var] = "present" if os.getenv(var) else "missing"
    health_status["environment"] = env_status
    
    # Check Redis if enabled
    redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    health_status["redis_enabled"] = redis_enabled
    
    status_code = 200 if not missing_vars else 503
    return JSONResponse(status_code=status_code, content=health_status)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "L9 Reasoning Agent V3.5",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "operational",
        "version": "3.5",
        "environment": {
            "supabase_configured": bool(os.getenv("SUPABASE_URL")),
            "redis_enabled": os.getenv("REDIS_ENABLED", "false").lower() == "true"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting L9 Runtime on {host}:{port}")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

