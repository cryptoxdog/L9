"""
L9 Research Swarm Orchestrator
==============================

Runs concurrent research agents, analyst pass, dreamers, convergence.
"""

from .interface import (
    IResearchSwarmOrchestrator,
    ResearchSwarmRequest,
    ResearchSwarmResponse,
)
from .orchestrator import ResearchSwarmOrchestrator
from .convergence import Convergence

__all__ = [
    "IResearchSwarmOrchestrator",
    "ResearchSwarmRequest",
    "ResearchSwarmResponse",
    "ResearchSwarmOrchestrator",
    "Convergence",
]

