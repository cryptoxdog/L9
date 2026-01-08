"""
L9 ActionTool Orchestrator - Interface
Version: 1.0.0

Validates and executes tools, retries, safety, logs tool packets.
"""

from typing import Protocol, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ToolSafetyLevel(str, Enum):
    """Tool safety levels."""

    SAFE = "safe"
    REQUIRES_APPROVAL = "requires_approval"
    DANGEROUS = "dangerous"


class ActionToolRequest(BaseModel):
    """Request to action_tool orchestrator."""

    tool_id: str = Field(default="", description="Canonical tool identity")
    arguments: Dict[str, Any] = Field(
        default_factory=dict, description="Tool arguments"
    )
    max_retries: int = Field(default=3, description="Max retry attempts")
    require_approval: bool = Field(default=False, description="Require human approval")


class ActionToolResponse(BaseModel):
    """Response from action_tool orchestrator."""

    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Result message")
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Tool execution result"
    )
    retries_used: int = Field(default=0, description="Number of retries used")
    safety_level: ToolSafetyLevel = Field(
        default=ToolSafetyLevel.SAFE, description="Safety assessment"
    )


class IActionToolOrchestrator(Protocol):
    """Interface for ActionTool Orchestrator."""

    async def execute(self, request: ActionToolRequest) -> ActionToolResponse:
        """Execute action_tool orchestration."""
        ...

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "ORC-INTE-010",
    "component_name": "Interface",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "intelligence",
    "domain": "orchestration",
    "type": "utility",
    "status": "active",
    "governance_level": "high",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Provides interface components including ToolSafetyLevel, ActionToolRequest, ActionToolResponse",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
