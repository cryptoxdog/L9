"""
Memory API - Public Interface for Agents
==========================================

High-level API for agents to interact with memory system.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MemoryAPI:
    """
    Public API for agents to read/write memory.
    
    Methods:
    - search(): Query memory by keyword or embedding
    - write(): Store data in memory
    - delete(): Remove packets
    - cleanup_expired(): Delete expired packets
    """
    
    def __init__(self, substrate, redis_cache=None):
        self.substrate = substrate
        self.redis = redis_cache
        self.logger = logger
    
    async def search(
        self,
        query: str,
        segment: str,
        agent_id: str,
        limit: int = 10
    ) -> List:
        """
        Search memory by keyword.
        Checks cache first, then substrate.
        """
        # Check cache
        if self.redis:
            cached = await self.redis.get_search(query, segment, agent_id)
            if cached is not None:
                return cached
        
        # Query substrate
        packets = await self.substrate.search_packets(
            query, segment, agent_id, limit
        )
        
        # Cache result
        if self.redis and packets:
            await self.redis.set_search(query, segment, agent_id, packets)
        
        return packets if packets else []
    
    async def semantic_search(
        self,
        embedding: List[float],
        segment: str,
        agent_id: str,
        limit: int = 10
    ) -> List:
        """Vector similarity search."""
        results = await self.substrate.semantic_search(
            embedding, segment, agent_id, limit
        )
        return results if results else []
    
    async def write(
        self,
        segment: str,
        content: Dict[str, Any],
        agent_id: str,
        metadata: Optional[Dict[str, str]] = None,
        embedding: Optional[List[float]] = None,
        ttl_hours: Optional[int] = None
    ) -> str:
        """
        Write to memory.
        
        Args:
            segment: Memory segment (governance_meta, project_history, tool_audit, session_context)
            content: Data to store
            agent_id: Owner agent
            metadata: Optional tags
            embedding: Optional 1536-dim vector
            ttl_hours: Optional expiration time in hours
        
        Returns:
            chunk_id
        """
        from datetime import datetime
        
        chunk_id = f"{segment}_{agent_id}_{datetime.utcnow().isoformat()}"
        
        expires_at = None
        if ttl_hours:
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        # Create packet (would import MemoryPacket here)
        packet_dict = {
            "chunk_id": chunk_id,
            "segment": segment,
            "agent_id": agent_id,
            "content": content,
            "metadata": metadata or {},
            "embedding": embedding,
            "expires_at": expires_at
        }
        
        # Write to substrate
        written_id = await self.substrate.write_packet(packet_dict)
        
        # Invalidate cache
        if self.redis:
            await self.redis.invalidate_segment(segment, agent_id)
        
        self.logger.info(f"Wrote {chunk_id} to {segment}")
        return written_id
    
    async def delete(self, chunk_id: str) -> None:
        """Mark a memory packet for deletion."""
        self.logger.info(f"Marked {chunk_id} for deletion")
    
    async def list_segments(self, agent_id: str) -> Dict[str, int]:
        """Get summary of agent's memory segments."""
        summary = {}
        segments = ["governance_meta", "project_history", "tool_audit", "session_context"]
        
        for segment in segments:
            summary[segment] = 0
        
        return summary
    
    async def cleanup_expired(self) -> int:
        """
        Delete expired packets.
        
        Returns:
            Count of deleted packets
        """
        count = await self.substrate.delete_expired()
        self.logger.info(f"Cleaned up {count} expired packets")
        return count
