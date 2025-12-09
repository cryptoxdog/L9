"""
L9 Memory Substrate - Service Layer
Version: 1.0.0

Orchestrating service that coordinates repository, semantic, and graph layers.
Provides a unified interface for substrate operations.
"""

import logging
from typing import Any, Optional

from memory.substrate_models import (
    PacketEnvelope,
    PacketEnvelopeIn,
    PacketWriteResult,
    SemanticSearchRequest,
    SemanticSearchResult,
    SemanticHit,
)
from memory.substrate_repository import SubstrateRepository
from memory.substrate_semantic import (
    SemanticService,
    EmbeddingProvider,
    StubEmbeddingProvider,
    create_embedding_provider,
)
from memory.substrate_graph import SubstrateDAG, run_substrate_flow

logger = logging.getLogger(__name__)


class MemorySubstrateService:
    """
    Main service class for the Memory Substrate.
    
    Coordinates all substrate operations:
    - Packet ingestion and DAG processing
    - Semantic search
    - Memory retrieval
    - Health monitoring
    """
    
    def __init__(
        self,
        repository: SubstrateRepository,
        embedding_provider: Optional[EmbeddingProvider] = None,
    ):
        """
        Initialize the substrate service.
        
        Args:
            repository: Database repository instance
            embedding_provider: Embedding provider (defaults to stub if not provided)
        """
        self._repository = repository
        
        # Initialize embedding provider
        if embedding_provider is None:
            logger.warning("No embedding provider specified, using stub provider")
            embedding_provider = StubEmbeddingProvider()
        self._embedding_provider = embedding_provider
        
        # Initialize semantic service
        self._semantic_service = SemanticService(
            embedding_provider=embedding_provider,
            repository=repository,
        )
        
        # Initialize DAG
        self._dag = SubstrateDAG(
            repository=repository,
            semantic_service=self._semantic_service,
        )
        
        logger.info("MemorySubstrateService initialized")
    
    # =========================================================================
    # Packet Operations
    # =========================================================================
    
    async def write_packet(self, packet_in: PacketEnvelopeIn) -> PacketWriteResult:
        """
        Submit a packet to the substrate for processing.
        
        Runs the full DAG pipeline:
        1. Intake validation
        2. Reasoning block generation
        3. Memory writes
        4. Semantic embedding
        5. Checkpoint
        
        Args:
            packet_in: Input packet envelope
            
        Returns:
            PacketWriteResult with status and written tables
        """
        logger.info(f"Processing packet: type={packet_in.packet_type}")
        
        # Convert input to full envelope
        envelope = packet_in.to_envelope()
        
        # Run through DAG
        result = await self._dag.run(envelope)
        
        logger.info(
            f"Packet {envelope.packet_id} processed: "
            f"status={result.status}, tables={result.written_tables}"
        )
        
        return result
    
    async def get_packet(self, packet_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve a packet by ID.
        
        Args:
            packet_id: UUID string of the packet
            
        Returns:
            Packet envelope as dict or None if not found
        """
        from uuid import UUID
        try:
            row = await self._repository.get_packet(UUID(packet_id))
            if row:
                return row.envelope
            return None
        except Exception as e:
            logger.error(f"Error retrieving packet {packet_id}: {e}")
            return None
    
    # =========================================================================
    # Semantic Search Operations
    # =========================================================================
    
    async def semantic_search(self, request: SemanticSearchRequest) -> SemanticSearchResult:
        """
        Search semantic memory for similar content.
        
        Args:
            request: Search request with query and parameters
            
        Returns:
            SemanticSearchResult with hits
        """
        logger.info(f"Semantic search: query='{request.query[:50]}...'")
        
        hits = await self._semantic_service.search(
            query=request.query,
            top_k=request.top_k,
            agent_id=request.agent_id,
        )
        
        return SemanticSearchResult(
            query=request.query,
            hits=[
                SemanticHit(
                    embedding_id=h["embedding_id"],
                    score=h["score"],
                    payload=h["payload"],
                )
                for h in hits
            ],
        )
    
    async def embed_text(self, text: str, payload: dict[str, Any], agent_id: Optional[str] = None) -> str:
        """
        Directly embed and store text in semantic memory.
        
        Args:
            text: Text to embed
            payload: Metadata payload
            agent_id: Optional agent identifier
            
        Returns:
            embedding_id
        """
        return await self._semantic_service.embed_and_store(
            text=text,
            payload=payload,
            agent_id=agent_id,
        )
    
    # =========================================================================
    # Memory Event Operations
    # =========================================================================
    
    async def get_memory_events(
        self,
        agent_id: str,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Retrieve memory events for an agent.
        
        Args:
            agent_id: Agent identifier
            event_type: Optional event type filter
            limit: Maximum events to return
            
        Returns:
            List of memory events as dicts
        """
        rows = await self._repository.get_memory_events(
            agent_id=agent_id,
            event_type=event_type,
            limit=limit,
        )
        return [row.model_dump(mode="json") for row in rows]
    
    # =========================================================================
    # Reasoning Trace Operations
    # =========================================================================
    
    async def get_reasoning_traces(
        self,
        agent_id: Optional[str] = None,
        packet_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Retrieve reasoning traces.
        
        Args:
            agent_id: Optional agent filter
            packet_id: Optional packet filter
            limit: Maximum traces to return
            
        Returns:
            List of reasoning traces as dicts
        """
        from uuid import UUID
        pid = UUID(packet_id) if packet_id else None
        
        rows = await self._repository.get_reasoning_traces(
            agent_id=agent_id,
            packet_id=pid,
            limit=limit,
        )
        return [row.model_dump(mode="json") for row in rows]
    
    # =========================================================================
    # Checkpoint Operations
    # =========================================================================
    
    async def get_checkpoint(self, agent_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve the latest checkpoint for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Checkpoint state as dict or None
        """
        row = await self._repository.get_checkpoint(agent_id)
        if row:
            return row.model_dump(mode="json")
        return None
    
    # =========================================================================
    # Insight & Knowledge Operations (v1.1.0+)
    # =========================================================================
    
    async def write_insights(
        self,
        insights: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Write extracted insights to the substrate.
        
        Persists insights and associated facts to knowledge_facts table.
        
        Args:
            insights: List of ExtractedInsight dicts
            
        Returns:
            Status dict with counts
        """
        facts_written = 0
        
        for insight in insights:
            # Write associated facts
            for fact in insight.get("facts", []):
                await self._repository.insert_knowledge_fact(
                    subject=fact.get("subject", "unknown"),
                    predicate=fact.get("predicate", "unknown"),
                    object_value=fact.get("object"),
                    confidence=fact.get("confidence"),
                    source_packet=insight.get("source_packet"),
                )
                facts_written += 1
        
        return {
            "status": "ok",
            "insights_processed": len(insights),
            "facts_written": facts_written,
        }
    
    async def trigger_world_model_update(
        self,
        insights: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Trigger world model update from insights.
        
        Stub implementation - logs intent and returns success.
        In production, this would call WorldModelOrchestrator.
        
        Args:
            insights: List of insights to propagate
            
        Returns:
            Status dict
        """
        logger.info(f"World model update triggered with {len(insights)} insights")
        
        # Filter to insights that should trigger updates
        triggering = [i for i in insights if i.get("trigger_world_model", False)]
        
        if not triggering:
            return {
                "status": "skipped",
                "reason": "no_triggering_insights",
            }
        
        # Stub: In production, this calls the world model orchestrator
        # For now, we just log and return success
        logger.info(f"Would propagate {len(triggering)} insights to world model")
        
        return {
            "status": "ok",
            "insights_propagated": len(triggering),
            "message": "World model update queued (stub)",
        }
    
    async def get_facts_by_subject(
        self,
        subject: str,
        predicate: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Retrieve knowledge facts by subject.
        
        Args:
            subject: Subject to search for
            predicate: Optional predicate filter
            limit: Maximum facts to return
            
        Returns:
            List of facts as dicts
        """
        rows = await self._repository.get_facts_by_subject(
            subject=subject,
            predicate=predicate,
            limit=limit,
        )
        return [row.model_dump(mode="json") for row in rows]
    
    # =========================================================================
    # Health & Status
    # =========================================================================
    
    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check on all substrate components.
        
        Returns:
            Health status dict
        """
        db_health = await self._repository.health_check()
        
        return {
            "status": db_health["status"],
            "components": {
                "database": db_health,
                "embedding_provider": {
                    "type": type(self._embedding_provider).__name__,
                    "dimensions": self._embedding_provider.dimensions,
                },
                "dag": {
                    "status": "ready",
                },
            },
        }


# =============================================================================
# Factory Function
# =============================================================================

async def create_substrate_service(
    database_url: str,
    embedding_provider_type: str = "stub",
    embedding_model: str = "text-embedding-3-large",
    openai_api_key: Optional[str] = None,
    db_pool_size: int = 5,
    db_max_overflow: int = 10,
) -> MemorySubstrateService:
    """
    Factory function to create a fully configured MemorySubstrateService.
    
    Args:
        database_url: Postgres DSN
        embedding_provider_type: "openai" or "stub"
        embedding_model: Model name for OpenAI
        openai_api_key: API key for OpenAI
        db_pool_size: Connection pool size
        db_max_overflow: Pool overflow limit
        
    Returns:
        Configured MemorySubstrateService
    """
    # Create repository
    repository = SubstrateRepository(
        database_url=database_url,
        pool_size=db_pool_size,
        max_overflow=db_max_overflow,
    )
    await repository.connect()
    
    # Create embedding provider
    embedding_provider = create_embedding_provider(
        provider_type=embedding_provider_type,
        model=embedding_model,
        api_key=openai_api_key,
    )
    
    # Create and return service
    return MemorySubstrateService(
        repository=repository,
        embedding_provider=embedding_provider,
    )


# Singleton instance
_service: Optional[MemorySubstrateService] = None


async def get_service() -> MemorySubstrateService:
    """Get service singleton (must be initialized first)."""
    if _service is None:
        raise RuntimeError("Service not initialized. Call init_service() first.")
    return _service


async def init_service(
    database_url: str,
    **kwargs,
) -> MemorySubstrateService:
    """Initialize the service singleton."""
    global _service
    _service = await create_substrate_service(database_url, **kwargs)
    return _service


async def close_service() -> None:
    """Close the service and release resources."""
    global _service
    if _service:
        await _service._repository.disconnect()
        _service = None

