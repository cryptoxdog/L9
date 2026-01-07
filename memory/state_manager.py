"""
L9 Memory - State Manager
Version: 1.0.0

Thin abstraction over MemorySubstrateService for LangGraph and higher-level
agents that need to load/save state + append events without touching the
repository directly.

# bound to memory-yaml2.0 state layer (module: state_manager.py, responsibilities: agent_state, long_term_flags, contradiction_tracking)
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

from memory.substrate_models import PacketEnvelopeIn, PacketWriteResult
from memory.substrate_service import MemorySubstrateService


class MemoryStateManager:
    """
    High-level state manager for agent / graph state.

    Responsibilities:
    - Append PacketEnvelopes to memory (via service.write_packet)
    - Save/load checkpoint state through MemorySubstrateService
    - Provide a clean interface for LangGraph graphs
    """

    def __init__(self, service: MemorySubstrateService, agent_id: str) -> None:
        self._service = service
        self._agent_id = agent_id

    @property
    def agent_id(self) -> str:
        return self._agent_id

    async def append_event(
        self,
        packet_type: str,
        payload: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        provenance: Optional[dict[str, Any]] = None,
        confidence: Optional[dict[str, Any]] = None,
    ) -> PacketWriteResult:
        """
        Append a new event to memory as a PacketEnvelope.

        This is the primary "write" path for agents/graphs.
        """
        packet_in = PacketEnvelopeIn(
            packet_type=packet_type,
            payload=payload,
            metadata=metadata,
            provenance=provenance,
            confidence=confidence,
        )
        return await self._service.write_packet(packet_in)

    async def save_checkpoint(self, state: dict[str, Any]) -> None:
        """
        Save the current graph/agent state as a checkpoint.

        Delegates to MemorySubstrateService.save_checkpoint.
        """
        await self._service.save_checkpoint(agent_id=self._agent_id, state=state)

    async def load_checkpoint(self) -> Optional[dict[str, Any]]:
        """
        Load the latest checkpoint for this agent.

        Delegates to MemorySubstrateService.get_checkpoint.
        """
        return await self._service.get_checkpoint(agent_id=self._agent_id)

    async def start_new_thread(self) -> UUID:
        """
        Generate a new thread_id for multi-turn conversations / graphs.

        This does not write anything by itself; it's a convenience helper.
        """
        return uuid4()

    async def log_trace_step(
        self,
        thread_id: UUID,
        step_name: str,
        thoughts: str,
        extra: Optional[dict[str, Any]] = None,
    ) -> PacketWriteResult:
        """
        Convenience helper for logging a single reasoning trace step.
        """
        payload: dict[str, Any] = {
            "thread_id": str(thread_id),
            "step_name": step_name,
            "thoughts": thoughts,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if extra:
            payload["extra"] = extra

        return await self.append_event(
            packet_type="reasoning_trace",
            payload=payload,
        )
