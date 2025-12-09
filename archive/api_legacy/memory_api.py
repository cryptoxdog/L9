"""
L9 Memory Substrate - FastAPI Router
Version: 1.0.0

REST API endpoints for the memory substrate:
- POST /packet - Submit a PacketEnvelope
- POST /semantic/search - Search semantic memory
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import APIRouter, FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse

from memory.substrate_models import (
    PacketEnvelopeIn,
    PacketWriteResult,
    SemanticSearchRequest,
    SemanticSearchResult,
)
from memory.substrate_service import (
    MemorySubstrateService,
    create_substrate_service,
)
from config.memory_substrate_settings import get_settings, MemorySubstrateSettings

logger = logging.getLogger(__name__)


# =============================================================================
# Application State & Dependencies
# =============================================================================

class AppState:
    """Application state container."""
    service: Optional[MemorySubstrateService] = None


app_state = AppState()


async def get_substrate_service() -> MemorySubstrateService:
    """Dependency to get the substrate service."""
    if app_state.service is None:
        raise HTTPException(
            status_code=503,
            detail="Substrate service not initialized"
        )
    return app_state.service


# =============================================================================
# Router Definition
# =============================================================================

router = APIRouter(tags=["memory-substrate"])


@router.post(
    "/packet",
    response_model=PacketWriteResult,
    summary="Submit a PacketEnvelope",
    description="Submit a packet to the memory substrate for processing through the DAG pipeline.",
)
async def write_packet(
    packet: PacketEnvelopeIn,
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> PacketWriteResult:
    """
    Submit a PacketEnvelope into the substrate.
    
    The packet flows through the DAG:
    1. Intake validation
    2. Reasoning block generation
    3. Memory writes (packet_store, agent_memory_events)
    4. Semantic embedding (if applicable)
    5. Checkpoint save
    
    Returns the packet_id and list of tables written to.
    """
    try:
        result = await service.write_packet(packet)
        return result
    except Exception as e:
        logger.exception(f"Error processing packet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/semantic/search",
    response_model=SemanticSearchResult,
    summary="Search semantic memory",
    description="Search semantic memory using natural language query via pgvector.",
)
async def semantic_search(
    request: SemanticSearchRequest,
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> SemanticSearchResult:
    """
    Search semantic memory using pgvector.
    
    Generates embedding for the query and finds top-k similar entries
    in the semantic_memory table.
    """
    try:
        result = await service.semantic_search(request)
        return result
    except Exception as e:
        logger.exception(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/packet/{packet_id}",
    summary="Retrieve a packet by ID",
    description="Fetch a stored PacketEnvelope by its UUID.",
)
async def get_packet(
    packet_id: str,
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> dict[str, Any]:
    """Retrieve a packet by ID."""
    result = await service.get_packet(packet_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Packet not found")
    return result


@router.get(
    "/events/{agent_id}",
    summary="Get memory events for an agent",
    description="Retrieve memory events for a specific agent.",
)
async def get_memory_events(
    agent_id: str,
    event_type: Optional[str] = None,
    limit: int = 100,
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> list[dict[str, Any]]:
    """Get memory events for an agent."""
    return await service.get_memory_events(
        agent_id=agent_id,
        event_type=event_type,
        limit=limit,
    )


@router.get(
    "/traces",
    summary="Get reasoning traces",
    description="Retrieve reasoning traces with optional filters.",
)
async def get_reasoning_traces(
    agent_id: Optional[str] = None,
    packet_id: Optional[str] = None,
    limit: int = 100,
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> list[dict[str, Any]]:
    """Get reasoning traces."""
    return await service.get_reasoning_traces(
        agent_id=agent_id,
        packet_id=packet_id,
        limit=limit,
    )


@router.get(
    "/checkpoint/{agent_id}",
    summary="Get agent checkpoint",
    description="Retrieve the latest checkpoint for an agent.",
)
async def get_checkpoint(
    agent_id: str,
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> dict[str, Any]:
    """Get the latest checkpoint for an agent."""
    result = await service.get_checkpoint(agent_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No checkpoint found")
    return result


@router.get(
    "/health",
    summary="Health check",
    description="Check health of the memory substrate service.",
)
async def health_check(
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> dict[str, Any]:
    """Perform health check."""
    return await service.health_check()


# =============================================================================
# Thread & Lineage Endpoints (v1.1.0+)
# =============================================================================

@router.get(
    "/thread/{thread_id}",
    summary="Get thread packets",
    description="Retrieve all packets in a conversation thread.",
)
async def get_thread(
    thread_id: str,
    limit: int = 100,
    order: str = "asc",
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> dict[str, Any]:
    """Get packets in a thread."""
    from uuid import UUID
    from memory.retrieval import get_retrieval_pipeline, init_retrieval_pipeline
    
    pipeline = init_retrieval_pipeline(service._repository, service._semantic_service)
    return await pipeline.fetch_thread(UUID(thread_id), limit, order)


@router.get(
    "/lineage/{packet_id}",
    summary="Get packet lineage",
    description="Traverse packet lineage (ancestors or descendants).",
)
async def get_lineage(
    packet_id: str,
    direction: str = "ancestors",
    max_depth: int = 10,
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> dict[str, Any]:
    """Get packet lineage graph."""
    from uuid import UUID
    from memory.retrieval import init_retrieval_pipeline
    
    pipeline = init_retrieval_pipeline(service._repository, service._semantic_service)
    return await pipeline.fetch_lineage(UUID(packet_id), direction, max_depth)


# =============================================================================
# Knowledge & Insight Endpoints (v1.1.0+)
# =============================================================================

@router.get(
    "/facts",
    summary="Query knowledge facts",
    description="Retrieve knowledge facts with optional filters.",
)
async def query_facts(
    subject: Optional[str] = None,
    predicate: Optional[str] = None,
    source_packet: Optional[str] = None,
    limit: int = 100,
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> list[dict[str, Any]]:
    """Query knowledge facts."""
    from uuid import UUID
    from memory.retrieval import init_retrieval_pipeline
    
    pipeline = init_retrieval_pipeline(service._repository)
    source_uuid = UUID(source_packet) if source_packet else None
    return await pipeline.fetch_facts(subject, predicate, source_uuid, limit)


@router.get(
    "/insights",
    summary="Query insights",
    description="Retrieve extracted insights with optional filters.",
)
async def query_insights(
    packet_id: Optional[str] = None,
    insight_type: Optional[str] = None,
    limit: int = 50,
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> list[dict[str, Any]]:
    """Query extracted insights."""
    from uuid import UUID
    from memory.retrieval import init_retrieval_pipeline
    
    pipeline = init_retrieval_pipeline(service._repository)
    pid = UUID(packet_id) if packet_id else None
    return await pipeline.fetch_insights(pid, insight_type, limit)


# =============================================================================
# Hybrid Search Endpoint (v1.1.0+)
# =============================================================================

@router.post(
    "/hybrid/search",
    summary="Hybrid search",
    description="Search using semantic + structured filters.",
)
async def hybrid_search(
    query: str,
    top_k: int = 10,
    filters: Optional[dict[str, Any]] = None,
    agent_id: Optional[str] = None,
    min_score: float = 0.5,
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> dict[str, Any]:
    """Perform hybrid search."""
    from memory.retrieval import init_retrieval_pipeline
    
    pipeline = init_retrieval_pipeline(service._repository, service._semantic_service)
    return await pipeline.hybrid_search(query, top_k, filters, agent_id, min_score)


# =============================================================================
# Garbage Collection Endpoint (v1.1.0+)
# =============================================================================

@router.post(
    "/gc/run",
    summary="Run garbage collection",
    description="Trigger manual garbage collection cycle.",
)
async def run_gc(
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> dict[str, Any]:
    """Run garbage collection."""
    from memory.housekeeping import init_housekeeping_engine
    
    engine = init_housekeeping_engine(service._repository)
    return await engine.run_full_gc()


@router.get(
    "/gc/stats",
    summary="Get GC statistics",
    description="Retrieve garbage collection statistics.",
)
async def get_gc_stats(
    service: MemorySubstrateService = Depends(get_substrate_service),
) -> dict[str, Any]:
    """Get GC statistics."""
    from memory.housekeeping import init_housekeeping_engine
    
    engine = init_housekeeping_engine(service._repository)
    return await engine.get_gc_stats()


# =============================================================================
# Application Factory
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup/shutdown."""
    # Startup
    logger.info("Starting Memory Substrate API...")
    
    try:
        settings = get_settings()
        
        # Determine embedding provider type
        provider_type = "stub"
        if settings.openai_api_key:
            provider_type = "openai"
        
        app_state.service = await create_substrate_service(
            database_url=settings.database_url,
            embedding_provider_type=provider_type,
            embedding_model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
            db_pool_size=settings.db_pool_size,
            db_max_overflow=settings.db_max_overflow,
        )
        logger.info("Memory Substrate service initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Memory Substrate API...")
    if app_state.service:
        await app_state.service._repository.disconnect()
        app_state.service = None
    logger.info("Memory Substrate API shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI app
    """
    settings = get_settings()
    
    app = FastAPI(
        title="L9 Memory Substrate API",
        description="Hybrid memory + reasoning substrate for L9 and PlasticOS",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Include router with prefix
    app.include_router(router, prefix=settings.api_prefix)
    
    # Root health endpoint
    @app.get("/")
    async def root():
        return {
            "service": "L9 Memory Substrate",
            "version": "1.0.0",
            "status": "running",
        }
    
    @app.get("/health")
    async def root_health():
        if app_state.service:
            return await app_state.service.health_check()
        return {"status": "starting"}
    
    return app


# =============================================================================
# Main Entry Point (for direct execution)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "api.memory_api:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )

