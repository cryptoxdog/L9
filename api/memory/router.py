"""
L9 Memory API Router
Version: 1.1.0

Memory substrate API endpoints using MemorySubstrateService.
All packets are automatically ingested via canonical ingest_packet().
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from api.auth import verify_api_key
from typing import Optional, List
import structlog

from memory.substrate_service import get_service
from memory.substrate_models import PacketEnvelopeIn, SemanticSearchRequest
from memory.ingestion import ingest_packet

logger = structlog.get_logger(__name__)

router = APIRouter()


class PacketRequest(BaseModel):
    """Request model for packet ingestion."""
    packet_type: str
    payload: dict
    metadata: Optional[dict] = None
    provenance: Optional[dict] = None
    confidence: Optional[dict] = None


class PacketResponse(BaseModel):
    """Response model for packet ingestion."""
    packet_id: str
    status: str
    written_tables: List[str]
    error_message: Optional[str] = None


@router.post("/test")
async def memory_test(
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """Test endpoint to verify memory router is reachable."""
    return {"ok": True, "msg": "memory endpoint reachable"}


@router.post("/packet", response_model=PacketResponse)
async def create_packet(
    request: PacketRequest,
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """
    Ingest a packet into memory substrate.
    
    This is the canonical entrypoint for all packet ingestion.
    All packets pass through ingest_packet() which runs the full DAG pipeline.
    """
    try:
        # Convert request to PacketEnvelopeIn
        packet_in = PacketEnvelopeIn(
            packet_type=request.packet_type,
            payload=request.payload,
            metadata=request.metadata,
            provenance=request.provenance,
            confidence=request.confidence,
        )
        
        # Canonical ingestion entrypoint
        result = await ingest_packet(packet_in)
        
        return PacketResponse(
            packet_id=str(result.packet_id),
            status=result.status,
            written_tables=result.written_tables,
            error_message=result.error_message,
        )
    except RuntimeError as e:
        # Memory system not initialized
        logger.error(f"Memory system not initialized: {e}")
        raise HTTPException(
            status_code=503,
            detail="Memory system not available. Check server logs for initialization errors."
        )
    except Exception as e:
        logger.error(f"Packet ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Packet ingestion failed: {str(e)}")


@router.post("/semantic/search")
async def semantic_search(
    request: SemanticSearchRequest,
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """Perform semantic search on memory substrate."""
    try:
        service = await get_service()
        result = await service.semantic_search(request)
        return result.model_dump(mode="json")
    except RuntimeError as e:
        logger.error(f"Memory system not initialized: {e}")
        raise HTTPException(
            status_code=503,
            detail="Memory system not available."
        )
    except Exception as e:
        logger.error(f"Semantic search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/stats")
async def get_stats(
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """Get memory system statistics."""
    try:
        service = await get_service()
        health = await service.health_check()
        
        # Get packet count
        from memory.substrate_repository import SubstrateRepository
        repo = service._repository
        
        async with repo.acquire() as conn:
            packet_count = await conn.fetchval("SELECT COUNT(*) FROM packet_store")
            embedding_count = await conn.fetchval("SELECT COUNT(*) FROM semantic_memory")
            fact_count = await conn.fetchval("SELECT COUNT(*) FROM knowledge_facts")
        
        return {
            "status": "operational",
            "packets": packet_count,
            "embeddings": embedding_count,
            "facts": fact_count,
            "health": health,
        }
    except RuntimeError as e:
        logger.error(f"Memory system not initialized: {e}")
        return {
            "status": "unavailable",
            "error": "Memory system not initialized",
        }
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")
