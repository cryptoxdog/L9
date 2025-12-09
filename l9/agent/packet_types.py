from pydantic import BaseModel
from typing import Dict, Any, Literal
from datetime import datetime

OpType = Literal["open_url","click","type_text","run_preset","heartbeat","status"]


class CommandPacket(BaseModel):
    op: OpType
    args: Dict[str, Any]
    metadata: Dict[str, Any]
    issued_at: datetime
    signature: str

