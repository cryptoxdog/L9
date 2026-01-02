"""
L-CTO Startup - CTO Agent Boot Sequence
"""

from l_cto.l_cto_core.identity import LIdentity
from l_cto.l_cto_interface.runtime_client import RuntimeClient
import structlog
from typing import Optional

logger = structlog.get_logger(__name__)


class LStartup:
    """
    l-cto Agent Startup Sequence

    Boots l-cto agent and initializes all subsystems:
    - Identity
    - Runtime client
    - Neo4j knowledge graph client (via singleton)
    """

    def __init__(self, neo4j_client=None):
        """
        Initialize startup components.
        
        Args:
            neo4j_client: Optional Neo4jClient instance (uses singleton if None)
        """
        self.identity = LIdentity()
        self.runtime = RuntimeClient()
        self.kg = neo4j_client  # Will be set in boot() if None

    async def boot(self) -> dict:
        """
        Execute L boot sequence with enforced init order.

        Order: memory → KG → runtime health → ready

        Returns:
            Boot result with detailed status
        """
        logger.info("=== l-cto Boot Sequence ===")

        # 1. Initialize KG client (Neo4j) - use singleton pattern
        logger.info("Step 1: Initializing Neo4j client...")
        try:
            # Use singleton Neo4j client from memory.graph_client
            # This ensures we use the same client as FastAPI lifespan
            if self.kg is None:
                from memory.graph_client import get_neo4j_client
                self.kg = await get_neo4j_client()
            
            if self.kg and self.kg.is_available():
                kg_status = "connected and available"
                logger.info(f"✅ Neo4j client: {kg_status}")
            elif self.kg:
                kg_status = "configured but not connected"
                logger.info(f"⚠️  Neo4j client: {kg_status}")
            else:
                kg_status = "not configured (NEO4J_PASSWORD missing or unavailable)"
                logger.info(f"⚠️  Neo4j client: {kg_status}")
        except Exception as e:
            logger.error(f"Neo4j initialization check failed: {e}")
            kg_status = f"error: {str(e)}"

        # 2. Test runtime connection
        logger.info("Step 2: Testing runtime connection...")
        try:
            runtime_health = self.runtime.health_check()
            runtime_status = runtime_health.get("status", "unknown")
            logger.info(f"✅ Runtime health: {runtime_status}")
        except Exception as e:
            logger.error(f"Runtime health check failed: {e}")
            runtime_status = f"error: {str(e)}"

        # 3. Return boot result (READY)
        boot_result = {
            "status": "l-cto Online",
            "version": self.identity.version,
            "role": self.identity.role,
            "subsystems": {"kg": kg_status, "runtime": runtime_status},
            "identity": self.identity.get_identity(),
            "boot_timestamp": "2025-12-30T00:00:00Z",
        }

        logger.info(f"=== l-cto boot complete: {boot_result['status']} ===")
        return boot_result

    async def shutdown(self):
        """Gracefully shutdown l-cto agent."""
        logger.info("l-cto shutdown initiated")

        # Note: Neo4j connection is managed by FastAPI lifespan
        # We don't close it here to avoid conflicts
        # The singleton pattern ensures proper cleanup in lifespan shutdown
        
        logger.info("l-cto shutdown complete")


# Singleton instance
startup = LStartup()
