"""
L9 Mac Protocol
Message schema for reverse tunnel communications.
JSON-only protocol definition.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MacMessage(BaseModel):
    """
    Mac protocol message schema.
    Used for reverse tunnel communications from Mac to VPS.
    """

    token: str = Field(..., description="Authentication token")
    cmd: str = Field(..., description="Command to execute")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    cwd: Optional[str] = Field(None, description="Working directory")
    timeout: Optional[int] = Field(None, description="Command timeout in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123",
                "cmd": "ls",
                "args": ["-la"],
                "cwd": "/opt/l9",
                "timeout": 30,
            }
        }


class MacResponse(BaseModel):
    """
    Mac protocol response schema.
    """

    success: bool = Field(..., description="Whether command succeeded")
    output: str = Field(default="", description="Command stdout")
    error: str = Field(default="", description="Command stderr")
    exit_code: int = Field(..., description="Command exit code")
    timestamp: str = Field(..., description="ISO8601 timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "output": "file1.txt\nfile2.txt\n",
                "error": "",
                "exit_code": 0,
                "timestamp": "2025-01-29T12:00:00Z",
            }
        }


def parse_mac_message(data: Dict[str, Any]) -> MacMessage:
    """Parse and validate Mac protocol message."""
    return MacMessage(**data)


def create_mac_response(
    success: bool,
    output: str = "",
    error: str = "",
    exit_code: int = 0,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Create Mac protocol response dict."""
    from datetime import datetime

    if timestamp is None:
        timestamp = datetime.utcnow().isoformat()

    response = MacResponse(
        success=success,
        output=output,
        error=error,
        exit_code=exit_code,
        timestamp=timestamp,
    )
    return response.dict()
