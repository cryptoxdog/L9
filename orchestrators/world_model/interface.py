"""
L9 WorldModel Orchestrator - Interface
Version: 1.0.0

Drives world-model lifecycle, ingest updates, schedule propagation.
"""

from typing import Protocol, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class WorldModelOperation(str, Enum):
    """World model operation types."""

    INGEST = "ingest"
    PROPAGATE = "propagate"
    SNAPSHOT = "snapshot"
    RESTORE = "restore"


class WorldModelRequest(BaseModel):
    """Request to world_model orchestrator."""

    operation: WorldModelOperation = Field(
        default=WorldModelOperation.INGEST, description="Operation type"
    )
    updates: List[Dict[str, Any]] = Field(
        default_factory=list, description="Updates to ingest"
    )
    snapshot_id: Optional[str] = Field(
        default=None, description="Snapshot ID for restore"
    )


class WorldModelResponse(BaseModel):
    """Response from world_model orchestrator."""

    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Result message")
    affected_entities: List[str] = Field(
        default_factory=list, description="Affected entity IDs"
    )
    state_version: int = Field(default=0, description="Current state version")


class IWorldModelOrchestrator(Protocol):
    """Interface for WorldModel Orchestrator."""

    async def execute(self, request: WorldModelRequest) -> WorldModelResponse:
        """Execute world_model orchestration."""
        ...

    async def update_from_insights(
        self,
        insights: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Update world model from extracted insights."""
        ...

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "ORC-INTE-028",
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
    "purpose": "Provides interface components including WorldModelOperation, WorldModelRequest, WorldModelResponse",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
