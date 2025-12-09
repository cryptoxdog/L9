from fastapi import HTTPException
from ..models.packets import CommandPacket

ALLOWED = {"open_url","click","type_text","run_preset","heartbeat","status"}


def validate(packet: CommandPacket):
    if packet.op not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported op: {packet.op}")

