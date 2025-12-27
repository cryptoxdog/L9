"""
Emma Agent Module — L9 Secure AI OS Integration.

Production-ready semi-autonomous agent with:
- Unified memory backend (Redis + PostgreSQL + Neo4j)
- Governed execution with escalation support
- Multi-channel webhook integration (Slack, Twilio, WhatsApp)
- Prometheus metrics and structured logging
- Circuit breaker patterns and connection pooling
"""

__version__ = "1.0.0"
__author__ = "L9 Collective"
__license__ = "Proprietary"

from emma_agent.controller import EmmaController
from emma_agent.modules.memory_manager import MemoryManager
from emma_agent.modules.governance_handler import GovernanceHandler
from emma_agent.modules.escalation_manager import EscalationManager
from emma_agent.infra.database import DatabasePool
from emma_agent.infra.cache import CacheManager
from emma_agent.infra.metrics import MetricsCollector
from emma_agent.infra.health import HealthChecker

__all__ = [
    "EmmaController",
    "MemoryManager",
    "GovernanceHandler",
    "EscalationManager",
    "DatabasePool",
    "CacheManager",
    "MetricsCollector",
    "HealthChecker",
]
