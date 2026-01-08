"""
L9 Memory - Checkpoint Manager
Version: 1.0.0

Wraps MemorySubstrateService checkpoint operations with a slightly higher-level
API suitable for LangGraph graphs and agent controllers.
"""

from __future__ import annotations

from typing import Any, Optional

from memory.substrate_service import MemorySubstrateService


class CheckpointManager:
    """
    Simple manager for saving/loading checkpoints per agent.

    This is intentionally thin; all persistence logic lives inside
    MemorySubstrateService and SubstrateRepository.
    """

    def __init__(self, service: MemorySubstrateService) -> None:
        self._service = service

    async def save(self, agent_id: str, state: dict[str, Any]) -> None:
        """Persist latest state for an agent."""
        await self._service.save_checkpoint(agent_id=agent_id, state=state)

    async def load(self, agent_id: str) -> Optional[dict[str, Any]]:
        """Load latest state for an agent."""
        return await self._service.get_checkpoint(agent_id=agent_id)

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "MEM-LEAR-001",
    "component_name": "Checkpoint Manager",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "learning",
    "domain": "memory_substrate",
    "type": "utility",
    "status": "active",
    "governance_level": "critical",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Implements CheckpointManager for checkpoint manager functionality",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
