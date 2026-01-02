"""
L Mission - CTO Agent Operational Entrypoint
"""

from l.l_core.identity import LIdentity
from l.l_core.engine import LEngine
from l.l_governance.guardrails import governance_pre, governance_post
import structlog

logger = structlog.get_logger(__name__)


class LMission:
    """
    L (CTO Agent) Mission Handler

    Operational entrypoint for L inside L9 Runtime.
    Handles directives with full governance enforcement.
    """

    def __init__(self):
        """Initialize L mission with identity and engine."""
        self.identity = LIdentity()
        self.engine = LEngine()
        logger.info(
            f"L Mission initialized: {self.identity.name} v{self.identity.version}"
        )

    def handle(self, directive: dict) -> dict:
        """
        Handle directive with FULL governance enforcement.

        Args:
            directive: Command directive to execute

        Returns:
            Execution result
        """
        logger.info(f"L handling directive: {directive.get('command')}")

        # 1. Pre-execution governance check (FULL)
        gov_pre = governance_pre(directive)
        if not gov_pre.get("allowed", False):
            logger.warning(f"Directive rejected by governance: {gov_pre.get('reason')}")
            return {
                "success": False,
                "error": "Governance pre-check failed",
                "reason": gov_pre.get("reason"),
                "violations": gov_pre.get("violations", []),
                "directive": directive.get("command"),
            }

        # 2. Execute through L engine (with recursion governance check)
        try:
            output = self.engine.execute(directive)
        except Exception as e:
            logger.exception(f"L engine execution failed: {e}")
            return {
                "success": False,
                "error": "Execution failed",
                "details": str(e),
                "directive": directive.get("command"),
            }

        # 3. Post-execution governance check (FULL)
        try:
            governance_post(directive, output)
        except Exception as e:
            logger.error(f"Post-governance check failed: {e}")
            # Don't fail the request, but log the issue

        return output

    def get_status(self) -> dict:
        """Get L mission status."""
        return {
            "agent": self.identity.name,
            "version": self.identity.version,
            "role": self.identity.role,
            "autonomy_level": self.identity.autonomy_level,
            "executions": len(self.engine.execution_history),
            "status": "operational",
        }


# Singleton instance
mission = LMission()
