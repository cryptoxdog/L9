"""
L9 Tools API Router
Version: 1.0.0

Tool execution endpoints using ActionToolOrchestrator.
All tool calls are validated, safety-checked, and logged.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from api.auth import verify_api_key
from typing import Dict, Any, Optional
import structlog

from orchestrators.action_tool.interface import (
    ActionToolRequest,
)
from orchestrators.action_tool.orchestrator import ActionToolOrchestrator

logger = structlog.get_logger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================


class ToolExecuteRequest(BaseModel):
    """Request model for tool execution."""

    tool_id: str = Field(..., description="Canonical tool identity")
    arguments: Dict[str, Any] = Field(
        default_factory=dict, description="Tool arguments"
    )
    max_retries: int = Field(default=3, description="Max retry attempts")
    require_approval: bool = Field(default=False, description="Require human approval")


class ToolExecuteResponse(BaseModel):
    """Response model for tool execution."""

    success: bool = Field(..., description="Whether operation succeeded")
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Tool execution result"
    )
    safety_level: str = Field(default="safe", description="Safety assessment")
    retries_used: int = Field(default=0, description="Number of retries used")
    message: str = Field(default="", description="Result message")


# ============================================================================
# Dependency: Get ActionToolOrchestrator from app.state
# ============================================================================


def get_action_tool_orchestrator(request: Request) -> ActionToolOrchestrator:
    """Get ActionToolOrchestrator from app.state."""
    orchestrator = getattr(request.app.state, "action_tool_orchestrator", None)
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="ActionToolOrchestrator not initialized. Check server logs.",
        )
    return orchestrator


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/test")
async def tools_test(
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """Test endpoint to verify tools router is reachable."""
    return {"ok": True, "msg": "tools endpoint reachable"}


@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    request: ToolExecuteRequest,
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
    orchestrator: ActionToolOrchestrator = Depends(get_action_tool_orchestrator),
):
    """
    Execute a tool via ActionToolOrchestrator.

    The orchestrator handles:
    - Tool validation
    - Safety assessment
    - Execution with retries
    - Packet logging
    """
    try:
        logger.info(
            "Tool execution request",
            tool_id=request.tool_id,
            max_retries=request.max_retries,
            require_approval=request.require_approval,
        )

        # Build orchestrator request
        action_request = ActionToolRequest(
            tool_id=request.tool_id,
            arguments=request.arguments,
            max_retries=request.max_retries,
            require_approval=request.require_approval,
        )

        # Execute via orchestrator
        result = await orchestrator.execute(action_request)

        logger.info(
            "Tool execution complete",
            tool_id=request.tool_id,
            success=result.success,
            safety_level=result.safety_level.value,
            retries_used=result.retries_used,
        )

        return ToolExecuteResponse(
            success=result.success,
            result=result.result,
            safety_level=result.safety_level.value,
            retries_used=result.retries_used,
            message=result.message,
        )
    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")
