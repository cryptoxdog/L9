import json, asyncio, logging, websockets
from .config import settings
from .packet_types import CommandPacket
from .executor import Executor
from .hmac_utils import verify


class AgentClient:
    def __init__(self):
        self.exec = Executor()

    async def run(self):
        while True:
            try:
                url = f"{settings.orchestrator_ws_url}/{settings.agent_id}?token={settings.agent_auth_token}"
                async with websockets.connect(url) as ws:
                    await self._loop(ws)
            except:
                logging.exception("L9 runtime exception", exc_info=True)
                await asyncio.sleep(5)

    async def _loop(self, ws):
        async for raw in ws:
            data = json.loads(raw)
            sig = data["signature"]
            clean = {
                "op": data["op"],
                "args": data["args"],
                "metadata": data["metadata"],
                "issued_at": data["issued_at"],
            }
            payload = json.dumps(clean,separators=(",",":")).encode()
            if not verify(payload, sig):
                continue
            packet = CommandPacket(**data)
            self.exec.execute(packet)

