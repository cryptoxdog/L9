"""
L9 ResearchSwarm Orchestrator - Interface
Version: 1.0.0

Runs concurrent research agents, analyst pass, dreamers, convergence.
"""

from typing import Protocol, List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ResearchSwarmRequest(BaseModel):
    """Request to research_swarm orchestrator."""

    query: str = Field(default="", description="Research query")
    agent_count: int = Field(default=3, description="Number of parallel agents")
    convergence_threshold: float = Field(default=0.8, description="Agreement threshold")


class ResearchSwarmResponse(BaseModel):
    """Response from research_swarm orchestrator."""

    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Result message")
    results: List[Dict[str, Any]] = Field(
        default_factory=list, description="Agent results"
    )
    consensus: Optional[str] = Field(default=None, description="Converged consensus")


class IResearchSwarmOrchestrator(Protocol):
    """Interface for ResearchSwarm Orchestrator."""

    async def execute(self, request: ResearchSwarmRequest) -> ResearchSwarmResponse:
        """Execute research_swarm orchestration."""
        ...

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "ORC-INTE-026",
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
    "purpose": "Provides interface components including ResearchSwarmRequest, ResearchSwarmResponse, IResearchSwarmOrchestrator",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
