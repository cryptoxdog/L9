"""
Phase 2: Instantiate Agent Instance

Harvested from: L9-Agent-Bootstrap-Architecture.md
Purpose: Create agent instance in memory and register in Neo4j.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

import structlog

if TYPE_CHECKING:
    from core.agents.schemas import AgentConfig
    from memory.substrate_service import MemorySubstrateService

logger = structlog.get_logger(__name__)


@dataclass
class AgentInstance:
    """Runtime agent instance with full initialization state"""
    instance_id: str
    agent_id: str
    name: str
    config: "AgentConfig"
    kernel_state: str = "LOADING"
    status: str = "INITIALIZING"
    created_at: datetime = field(default_factory=datetime.utcnow)
    initialized_at: Optional[datetime] = None
    initialization_signature: Optional[str] = None
    designation: Optional[str] = None
    role: Optional[str] = None
    mission: Optional[str] = None
    authority: Optional[str] = None


async def instantiate_agent(
    config: "AgentConfig",
    substrate_service: "MemorySubstrateService",
) -> AgentInstance:
    """
    Create agent instance and register in Neo4j.
    """
    # Generate unique instance ID
    instance_id = str(uuid.uuid4())
    
    # Create instance
    instance = AgentInstance(
        instance_id=instance_id,
        agent_id=config.agent_id,
        name=config.name,
        config=config,
        kernel_state="LOADING",
        created_at=datetime.utcnow(),
    )
    
    # Register in Neo4j if available
    if hasattr(substrate_service, 'neo4j_driver') and substrate_service.neo4j_driver:
        try:
            async with substrate_service.neo4j_driver.session() as session:
                await session.run("""
                    MERGE (a:Agent {agent_id: $agent_id})
                    SET a.instance_id = $instance_id,
                        a.name = $name,
                        a.kernel_state = 'LOADING',
                        a.status = 'INITIALIZING',
                        a.created_at = $created_at
                """, {
                    "instance_id": instance_id,
                    "agent_id": config.agent_id,
                    "name": config.name,
                    "created_at": instance.created_at.isoformat(),
                })
            logger.info(
                "Agent registered in Neo4j",
                agent_id=config.agent_id,
                instance_id=instance_id,
            )
        except Exception as e:
            logger.warning(
                "Failed to register agent in Neo4j, continuing",
                error=str(e),
            )
    
    logger.info(
        "Instantiated agent",
        agent_id=config.agent_id,
        instance_id=instance_id,
    )
    return instance

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "COR-FOUN-008",
    "component_name": "Phase 2 Instantiate",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "foundation",
    "domain": "agent_execution",
    "type": "utility",
    "status": "active",
    "governance_level": "critical",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Implements AgentInstance for phase 2 instantiate functionality",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
