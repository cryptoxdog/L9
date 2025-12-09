import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .auth import verify_agent_token
from .connection_manager import manager
from .models.packets import AgentEvent

app = FastAPI(title="L9 Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(x) for x in settings.allowed_origins] or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/agent/{agent_id}")
async def agent_ws(websocket: WebSocket, agent_id: str, token: str = Query(...)):
    verify_agent_token(token)
    await manager.connect(agent_id, websocket)

    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            _ = AgentEvent(**data)  # TODO: route to memory/log
    except WebSocketDisconnect:
        manager.disconnect(agent_id)

