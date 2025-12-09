from pydantic import BaseModel, Field
from typing import Dict, Any, Literal
from datetime import datetime

OpType = Literal["open_url","click","type_text","run_preset","heartbeat","status"]


class CommandPacket(BaseModel):
    op: OpType
    args: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    issued_at: datetime
    signature: str


class AgentEvent(BaseModel):
    agent_id: str
    event: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

