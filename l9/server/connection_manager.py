from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._agents: Dict[str, WebSocket] = {}

    async def connect(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        self._agents[agent_id] = websocket

    def disconnect(self, agent_id: str):
        self._agents.pop(agent_id, None)

    def get(self, agent_id: str) -> WebSocket | None:
        return self._agents.get(agent_id)

    async def send_to_agent(self, agent_id: str, message: str):
        ws = self._agents.get(agent_id)
        if ws:
            await ws.send_text(message)


manager = ConnectionManager()

