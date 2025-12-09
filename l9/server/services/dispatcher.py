import json
from datetime import datetime
from ..models.packets import CommandPacket
from ..auth import sign_payload
from ..connection_manager import manager


async def dispatch_command(agent_id: str, op: str, args=None, metadata=None):
    args = args or {}
    metadata = metadata or {}
    base = {
        "op": op,
        "args": args,
        "metadata": metadata,
        "issued_at": datetime.utcnow(),
    }
    payload = json.dumps({
        "op": op,
        "args": args,
        "metadata": metadata,
        "issued_at": base["issued_at"].isoformat(),
    }, separators=(",", ":")).encode("utf-8")
    sig = sign_payload(payload)
    packet = CommandPacket(**{**base, "signature": sig})
    await manager.send_to_agent(agent_id, packet.json())

