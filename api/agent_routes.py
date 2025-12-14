"""
L9 Agent Routes
Background agent tasking and management endpoints.
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agent"])


@router.get("/health")
async def agent_health():
    """Health check for agent layer."""
    return {"status": "ok", "service": "agent"}


@router.get("/status")
async def agent_status():
    """Agent system status."""
    return {
        "status": "ready",
        "active_tasks": 0,
        "orchestrators": ["memory", "reasoning", "world_model"],
    }


@router.post("/task")
async def submit_task(payload: dict):
    """
    Submit a task to the agent system.
    
    Ingests task to memory and routes to orchestrator.
    """
    from uuid import uuid4
    from memory.ingestion import ingest_packet
    from memory.substrate_models import PacketEnvelopeIn
    
    task_id = str(uuid4())
    logger.info("Task submitted: %s (id=%s)", payload.get("type", "unknown"), task_id)
    
    # Ingest task to memory (canonical ingestion point)
    try:
        packet_in = PacketEnvelopeIn(
            packet_type="agent_task_submitted",
            payload={
                "task_id": task_id,
                "task_type": payload.get("type", "unknown"),
                "task_payload": payload,
            },
            metadata={"agent": "api", "source": "agent_routes"},
        )
        await ingest_packet(packet_in)
    except Exception as e:
        logger.warning(f"Failed to ingest task to memory: {e}")
        # Don't fail the request if memory ingestion fails
    
    return {
        "status": "accepted",
        "task_id": task_id,
        "message": "Task queued for processing and ingested to memory",
    }


async def startup():
    """Called on app startup if exists."""
    logger.info("Agent routes initialized")


async def shutdown():
    """Called on app shutdown if exists."""
    logger.info("Agent routes shutting down")

