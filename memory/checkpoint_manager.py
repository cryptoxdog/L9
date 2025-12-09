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

