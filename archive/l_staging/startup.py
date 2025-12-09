"""
L Startup - CTO Agent Boot Sequence
"""
from l.l_core.identity import LIdentity
from l.l_interface.runtime_client import RuntimeClient
from l.memory.memory_router_v4 import MemoryRouterV4
from l.l_memory.kg_client import KGClient
from l.l_governance.guardrails import governance_pre
import logging

logger = logging.getLogger(__name__)


class LStartup:
    """
    L (CTO Agent) Startup Sequence
    
    Boots L and initializes all subsystems:
    - Identity
    - Runtime client
    - Memory client
    - Knowledge graph client
    """
    
    def __init__(self):
        """Initialize startup components."""
        self.identity = LIdentity()
        self.runtime = RuntimeClient()
        self.memory = MemoryRouterV4()
        self.kg = KGClient()
    
    def boot(self) -> dict:
        """
        Execute L boot sequence with enforced init order.
        
        Order: memory → KG → runtime health → ready
        
        Returns:
            Boot result with detailed status
        """
        logger.info("=== L (CTO) Boot Sequence ===")
        
        # 1. Governance pre-check for startup
        logger.info("Step 1: Governance pre-check...")
        gov_check = governance_pre({"command": "startup"})
        if not gov_check.get("allowed", False):
            logger.error(f"Startup rejected by governance: {gov_check.get('reason')}")
            return {
                "status": "Failed",
                "error": "Governance check failed",
                "reason": gov_check.get("reason"),
                "violations": gov_check.get("violations", [])
            }
        logger.info("✅ Governance check passed")
        
        # 2. Initialize memory router (FIRST)
        logger.info("Step 2: Initializing memory router v4...")
        try:
            # Memory router auto-connects in __init__
            memory_status = "ready" if self.memory._sb_alive else "supabase offline"
            if self.memory._sb_alive and self.memory._kg_alive:
                memory_status = "ready (dual-backend)"
            logger.info(f"✅ Memory router: {memory_status}")
        except Exception as e:
            logger.error(f"Memory initialization failed: {e}")
            memory_status = f"error: {str(e)}"
        
        # 3. Initialize KG client (SECOND)
        logger.info("Step 3: Initializing KG client...")
        try:
            self.kg.init()
            kg_status = "connected" if self.kg.connected else "not configured"
            logger.info(f"✅ KG client: {kg_status}")
        except Exception as e:
            logger.error(f"KG initialization failed: {e}")
            kg_status = f"error: {str(e)}"
        
        # 4. Test runtime connection (THIRD)
        logger.info("Step 4: Testing runtime connection...")
        try:
            runtime_health = self.runtime.health_check()
            runtime_status = runtime_health.get("status", "unknown")
            logger.info(f"✅ Runtime health: {runtime_status}")
        except Exception as e:
            logger.error(f"Runtime health check failed: {e}")
            runtime_status = f"error: {str(e)}"
        
        # 5. Return boot result (READY)
        boot_result = {
            "status": "L Online",
            "version": self.identity.version,
            "role": self.identity.role,
            "subsystems": {
                "memory": memory_status,
                "kg": kg_status,
                "runtime": runtime_status
            },
            "identity": self.identity.get_identity(),
            "boot_timestamp": "2025-11-24T19:45:00Z"
        }
        
        logger.info(f"=== L boot complete: {boot_result['status']} ===")
        return boot_result
    
    def shutdown(self):
        """Gracefully shutdown L."""
        logger.info("L shutdown initiated")
        
        # Close KG connection
        if self.kg.connected:
            self.kg.close()
        
        logger.info("L shutdown complete")


# Singleton instance
startup = LStartup()

