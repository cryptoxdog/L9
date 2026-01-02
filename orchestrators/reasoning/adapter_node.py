"""
L9 Reasoning Orchestrator - AdapterNode
Version: 1.1.0

Specialized component for reasoning orchestration.
Adapts reasoning engine for LangGraph node integration.
"""

from __future__ import annotations

import structlog
from typing import Any, Optional, TypedDict

from .orchestrator import ReasoningOrchestrator
from .interface import ReasoningRequest, ReasoningMode

logger = structlog.get_logger(__name__)


class ReasoningNodeState(TypedDict):
    """State for reasoning LangGraph node."""

    context: str
    mode: str
    depth: int
    branch_factor: int
    result: Optional[dict[str, Any]]
    errors: list[str]


class ReasoningAdapterNode:
    """
    AdapterNode for Reasoning Orchestrator.

    Bridges reasoning orchestrator with LangGraph execution.
    Provides both sync and async interfaces for flexibility.
    """

    def __init__(self, orchestrator: ReasoningOrchestrator | None = None):
        """
        Initialize adapter node.

        Args:
            orchestrator: Optional pre-configured orchestrator
        """
        self._orchestrator = orchestrator or ReasoningOrchestrator()
        logger.info("ReasoningAdapterNode initialized")

    async def process(self, state: ReasoningNodeState) -> ReasoningNodeState:
        """
        Process state through reasoning orchestrator.

        LangGraph-compatible async node function.

        Args:
            state: ReasoningNodeState with context and parameters

        Returns:
            Updated state with reasoning result
        """
        logger.info(
            f"Processing reasoning: mode={state.get('mode', 'chain_of_thought')}"
        )

        errors = list(state.get("errors", []))

        try:
            request = ReasoningRequest(
                context=state.get("context", ""),
                mode=ReasoningMode(state.get("mode", "chain_of_thought")),
                depth=state.get("depth", 3),
                branch_factor=state.get("branch_factor", 3),
            )

            response = await self._orchestrator.execute(request)

            return {
                **state,
                "result": response.model_dump(),
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Reasoning adapter error: {e}")
            errors.append(f"reasoning_adapter error: {str(e)}")
            return {
                **state,
                "result": None,
                "errors": errors,
            }

    def __call__(self, state: ReasoningNodeState) -> ReasoningNodeState:
        """
        Sync callable for LangGraph integration.

        Wraps async process for synchronous execution.
        """
        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in async context - create new loop in thread
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, self.process(state)).result()
        else:
            return asyncio.run(self.process(state))


def create_reasoning_node(orchestrator: ReasoningOrchestrator | None = None):
    """
    Factory function to create a reasoning LangGraph node.

    Returns an async function suitable for graph.add_node().

    Args:
        orchestrator: Optional pre-configured orchestrator

    Returns:
        Async node function
    """
    adapter = ReasoningAdapterNode(orchestrator)
    return adapter.process


# Backwards compatibility alias
AdapterNode = ReasoningAdapterNode
