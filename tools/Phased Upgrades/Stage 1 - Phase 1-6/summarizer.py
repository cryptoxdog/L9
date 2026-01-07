"""
Memory Summarizer - Auto-compress old context and prune
========================================================
"""

import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MemorySummarizer:
    """
    Automatic memory compression and pruning.
    
    Policies:
    - Keep last 50 chunks per segment
    - Compress older chunks into 1 summary
    - Delete expired packets
    """
    
    def __init__(self, memory_api):
        self.memory_api = memory_api
        self.logger = logger
        self._cleanup_task = None
    
    def schedule_cleanup(self, interval_hours: int = 24) -> None:
        """Schedule periodic memory cleanup."""
        interval_sec = interval_hours * 3600
        self._cleanup_task = asyncio.create_task(self._cleanup_loop(interval_sec))
    
    async def _cleanup_loop(self, interval_sec: int) -> None:
        """Run cleanup in background."""
        while True:
            try:
                await asyncio.sleep(interval_sec)
                await self.cleanup_all_agents()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup loop failed: {e}")
    
    async def cleanup_all_agents(self) -> None:
        """
        Clean up memory for all agents.
        """
        self.logger.info("Starting memory cleanup...")
        
        # Delete expired packets
        count = await self.memory_api.cleanup_expired()
        self.logger.info(f"Deleted {count} expired packets")
    
    async def compress_old_memory(
        self,
        agent_id: str,
        days: int = 7
    ) -> None:
        """
        Compress packets older than N days into 1 summary.
        """
        self.logger.info(f"Compressing memory for {agent_id} older than {days} days")
        
        # Query old packets
        # For now, just delete expired ones
        await self.memory_api.cleanup_expired()
    
    async def prune_session_context(self, agent_id: str, max_chunks: int = 50) -> None:
        """
        Limit session context to recent N chunks.
        """
        # Search session context
        old_sessions = await self.memory_api.search(
            query="",
            segment="session_context",
            agent_id=agent_id,
            limit=1000
        )
        
        if len(old_sessions) > max_chunks:
            # Mark old ones for deletion
            for session in old_sessions[max_chunks:]:
                chunk_id = session.get("chunk_id") if isinstance(session, dict) else session.chunk_id
                await self.memory_api.delete(chunk_id)
                self.logger.debug(f"Pruned old session {chunk_id}")
    
    async def cancel_cleanup(self) -> None:
        """Stop background cleanup."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self.logger.info("Cleanup task cancelled")
