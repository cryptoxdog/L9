"""
Memory Substrate Service Protocol
==================================

Abstract interface for memory backends (Postgres, Neo4j, Redis).
Defines contract all implementations must follow.
"""

from typing import Protocol, List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SubstrateException(Exception):
    """Base exception for substrate operations."""
    pass


class SubstrateConnectionError(SubstrateException):
    """Failed to connect to substrate backend."""
    pass


class SubstrateTimeoutError(SubstrateException):
    """Substrate operation timed out."""
    pass


class SubstrateValidationError(SubstrateException):
    """Invalid input to substrate."""
    pass


class SubstrateService(Protocol):
    """
    Abstract protocol for memory backends.
    
    Any backend must implement these async methods:
    - write_packet
    - search_packets
    - semantic_search
    - delete_expired
    - health_check
    - close
    """
    
    async def write_packet(self, packet) -> str:
        """
        Write a memory packet.
        
        Returns:
            chunk_id (str) on success
            
        Raises:
            SubstrateException: On write failure
        """
        ...
    
    async def search_packets(
        self,
        query: str,
        segment: str,
        agent_id: str,
        limit: int = 10
    ) -> List:
        """
        Search packets by keyword in segment.
        
        Returns:
            List of matching packets
        """
        ...
    
    async def semantic_search(
        self,
        embedding: List[float],
        segment: str,
        agent_id: str,
        limit: int = 10
    ) -> List:
        """
        Semantic search via vector similarity.
        
        Returns:
            List of (packet, similarity_score) tuples
        """
        ...
    
    async def delete_expired(self) -> int:
        """
        Delete packets past expires_at timestamp.
        
        Returns:
            Count of deleted packets
        """
        ...
    
    async def health_check(self) -> bool:
        """
        Check if substrate is healthy.
        
        Returns:
            True if healthy
        """
        ...
    
    async def close(self) -> None:
        """Close connections and cleanup."""
        ...


class CompositeSubstrate:
    """
    Orchestrates multiple backends (Postgres, Neo4j, Redis).
    Writes to all, reads from preferred tier (cache -> Postgres -> Neo4j).
    """
    
    def __init__(
        self,
        postgres_backend=None,
        neo4j_backend=None,
        redis_cache=None,
        logger=None
    ):
        self.postgres = postgres_backend
        self.neo4j = neo4j_backend
        self.redis = redis_cache
        self.logger = logger or logging.getLogger(__name__)
    
    async def write_packet(self, packet) -> str:
        """Write to all backends in parallel."""
        results = []
        
        # Write to Postgres (source of truth)
        if self.postgres:
            try:
                chunk_id = await self.postgres.write_packet(packet)
                results.append(("postgres", chunk_id))
            except SubstrateException as e:
                self.logger.error(f"Postgres write failed: {e}")
                raise
        
        # Write to Neo4j (async, no error propagation)
        if self.neo4j:
            try:
                await self.neo4j.write_packet(packet)
                results.append(("neo4j", packet.chunk_id))
            except SubstrateException as e:
                self.logger.warning(f"Neo4j write failed (async): {e}")
        
        # Cache invalidation in Redis
        if self.redis:
            try:
                cache_key = f"search:{packet.segment}:{packet.agent_id}"
                # Implementation: invalidate cache pattern
            except SubstrateException as e:
                self.logger.warning(f"Redis cache clear failed: {e}")
        
        return results[0][1] if results else None
    
    async def search_packets(
        self,
        query: str,
        segment: str,
        agent_id: str,
        limit: int = 10
    ) -> List:
        """
        Read from cache -> Postgres -> Neo4j (in priority order).
        """
        
        # 1. Try Redis cache first
        if self.redis:
            try:
                cached = await self.redis.search_packets(query, segment, agent_id, limit)
                if cached:
                    self.logger.debug(f"Cache hit: {len(cached)} packets")
                    return cached
            except SubstrateException:
                pass  # Fall through to Postgres
        
        # 2. Postgres (primary)
        if self.postgres:
            try:
                results = await self.postgres.search_packets(query, segment, agent_id, limit)
                return results if results else []
            except SubstrateException as e:
                self.logger.error(f"Postgres search failed: {e}")
        
        # 3. Neo4j fallback
        if self.neo4j:
            try:
                results = await self.neo4j.search_packets(query, segment, agent_id, limit)
                return results if results else []
            except SubstrateException as e:
                self.logger.error(f"Neo4j search failed: {e}")
        
        raise SubstrateException("No backends available for search")
    
    async def health_check(self) -> Dict[str, bool]:
        """Check all backends."""
        health = {}
        
        if self.postgres:
            try:
                await self.postgres.health_check()
                health["postgres"] = True
            except:
                health["postgres"] = False
        
        if self.neo4j:
            try:
                await self.neo4j.health_check()
                health["neo4j"] = True
            except:
                health["neo4j"] = False
        
        if self.redis:
            try:
                await self.redis.health_check()
                health["redis"] = True
            except:
                health["redis"] = False
        
        return health
    
    async def delete_expired(self) -> int:
        """Delete expired packets."""
        if self.postgres:
            return await self.postgres.delete_expired()
        return 0
    
    async def close(self) -> None:
        """Close all connections."""
        if self.postgres:
            await self.postgres.close()
        if self.neo4j:
            await self.neo4j.close()
        if self.redis:
            await self.redis.close()

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "TOO-OPER-008",
    "component_name": "Substrate Service",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "tools",
    "type": "service",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Provides substrate service components including SubstrateException, SubstrateConnectionError, SubstrateTimeoutError",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
