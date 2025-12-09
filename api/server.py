"""
L9 API Server
=============

FastAPI application for L9 Phase 2 Secure AI OS.

Provides:
- REST API endpoints for OS, agent, and memory operations
- WebSocket endpoint for real-time agent communication
- World model API (optional, v1.1.0+)

Version: 0.3.1
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from api.memory.router import router as memory_router
import api.db as db
import api.os_routes as os_routes
import api.agent_routes as agent_routes

# Optional: World Model API (v1.1.0+)
try:
    from api.world_model_api import router as world_model_router
    _has_world_model = True
except ImportError:
    _has_world_model = False

# Initialize DB
db.init_db()

# FastAPI App
app = FastAPI(title="L9 Phase 2 Secure AI OS")

# Basic Root
@app.get("/")
def root():
    return {"status": "L9 Phase 2 AI OS", "version": "0.3.1"}

# --- Routers ---
# OS health + metrics + routing
app.include_router(os_routes.router, prefix="/os")

# Background agent tasking
app.include_router(agent_routes.router, prefix="/agent")

# Persistent memory router
app.include_router(memory_router, prefix="/memory")

# World Model router (v1.1.0+)
if _has_world_model:
    app.include_router(world_model_router)


# Startup + Shutdown events (if the modules expose them)
@app.on_event("startup")
async def on_startup():
    if hasattr(agent_routes, "startup"):
        await agent_routes.startup()

@app.on_event("shutdown")
async def on_shutdown():
    if hasattr(agent_routes, "shutdown"):
        await agent_routes.shutdown()


# =============================================================================
# WebSocket Agent Endpoint
# =============================================================================

from core.schemas.event_stream import AgentHandshake

# Import the shared singleton orchestrator instance
from runtime.websocket_orchestrator import ws_orchestrator


@app.websocket("/ws/agent")
async def agent_ws_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket entrypoint for L9 Mac Agents and other workers.
    
    Protocol:
    1) Client connects and sends AgentHandshake JSON.
    2) Server validates handshake and registers the agent_id.
    3) Subsequent frames are EventMessage JSON payloads.
    4) On disconnect, agent is automatically unregistered.
    
    Example client connection:
        import websockets
        import json
        
        async with websockets.connect("ws://localhost:8000/ws/agent") as ws:
            # Step 1: Send handshake
            await ws.send(json.dumps({
                "agent_id": "mac-agent-1",
                "agent_version": "1.0.0",
                "capabilities": ["shell", "memory_read"]
            }))
            
            # Step 2: Send/receive events
            await ws.send(json.dumps({
                "type": "heartbeat",
                "agent_id": "mac-agent-1",
                "payload": {"running_tasks": 0}
            }))
    """
    await websocket.accept()
    agent_id: str | None = None
    
    try:
        # Step 1: Wait for handshake
        raw = await websocket.receive_json()
        handshake = AgentHandshake.model_validate(raw)
        agent_id = handshake.agent_id
        
        # Register with orchestrator (store handshake metadata)
        await ws_orchestrator.register(
            agent_id,
            websocket,
            metadata={
                "agent_version": handshake.agent_version,
                "capabilities": handshake.capabilities,
                "hostname": handshake.hostname,
                "platform": handshake.platform,
            }
        )
        
        # Step 2: Message loop
        while True:
            data = await websocket.receive_json()
            await ws_orchestrator.handle_incoming(agent_id, data)
            
    except WebSocketDisconnect:
        # Clean disconnect
        if agent_id:
            await ws_orchestrator.unregister(agent_id)
    except Exception as exc:
        # Unexpected error - log and cleanup
        import logging
        logging.getLogger(__name__).error(
            "WebSocket error for agent %s: %s",
            agent_id or "unknown",
            exc
        )
        if agent_id:
            await ws_orchestrator.unregister(agent_id)
