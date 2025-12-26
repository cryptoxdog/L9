"""
L9 Research Factory - Graph Runtime
Version: 1.0.0

Runtime wrapper for research graph execution with substrate integration.
"""

import structlog
from typing import Any, Optional
from uuid import uuid4

from services.research.graph_state import ResearchGraphState, create_initial_state
from services.research.research_graph import build_research_graph, run_research
from services.research.memory_adapter import get_memory_adapter, init_memory_adapter
from memory.substrate_repository import init_repository, close_repository, get_repository

logger = structlog.get_logger(__name__)


class ResearchGraphRuntime:
    """
    Runtime for managing research graph execution.
    
    Provides:
    - Graph initialization
    - Execution with substrate integration
    - Checkpoint management
    - Error handling
    """
    
    def __init__(self):
        """Initialize runtime."""
        self._graph = None
        self._initialized = False
    
    async def initialize(self, database_url: str) -> None:
        """
        Initialize the runtime.
        
        Args:
            database_url: Database URL for memory substrate
        """
        if self._initialized:
            return
        
        # Initialize substrate repository
        repo = await init_repository(database_url)
        
        # Initialize memory adapter
        init_memory_adapter(repo)
        
        # Build graph
        self._graph = build_research_graph()
        
        self._initialized = True
        logger.info("Research graph runtime initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the runtime."""
        await close_repository()
        self._initialized = False
        logger.info("Research graph runtime shutdown")
    
    async def execute(
        self,
        query: str,
        user_id: str = "anonymous",
        thread_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Execute research graph.
        
        Args:
            query: Research query
            user_id: User identifier
            thread_id: Optional thread ID
            
        Returns:
            Research result dict
        """
        if not self._initialized:
            raise RuntimeError("Runtime not initialized. Call initialize() first.")
        
        thread_id = thread_id or str(uuid4())
        
        logger.info(f"Executing research: query={query[:50]}..., thread={thread_id}")
        
        result = await run_research(
            query=query,
            user_id=user_id,
            thread_id=thread_id,
        )
        
        return result
    
    async def resume(
        self,
        thread_id: str,
    ) -> Optional[dict[str, Any]]:
        """
        Resume research from checkpoint.
        
        Args:
            thread_id: Thread ID to resume
            
        Returns:
            Research result dict, or None if no checkpoint found
        """
        if not self._initialized:
            raise RuntimeError("Runtime not initialized. Call initialize() first.")
        
        adapter = get_memory_adapter()
        state = await adapter.load_checkpoint(thread_id)
        
        if not state:
            logger.warning(f"No checkpoint found for thread: {thread_id}")
            return None
        
        logger.info(f"Resuming research from checkpoint: thread={thread_id}")
        
        # Re-execute from current state
        result = await self._graph.ainvoke(state)
        
        return result.get("final_output", {})
    
    async def get_status(self, thread_id: str) -> Optional[dict[str, Any]]:
        """
        Get status of a research thread.
        
        Args:
            thread_id: Thread ID to check
            
        Returns:
            Status dict, or None if not found
        """
        adapter = get_memory_adapter()
        state = await adapter.load_checkpoint(thread_id)
        
        if not state:
            return None
        
        return {
            "thread_id": thread_id,
            "query": state.get("original_query", ""),
            "refined_goal": state.get("refined_goal", ""),
            "steps_completed": sum(
                1 for s in state.get("plan", [])
                if s.get("status") == "completed"
            ),
            "total_steps": len(state.get("plan", [])),
            "evidence_count": len(state.get("evidence", [])),
            "critic_score": state.get("critic_score", 0.0),
            "retry_count": state.get("retry_count", 0),
            "has_output": bool(state.get("final_output")),
        }


# Singleton runtime instance
_runtime: Optional[ResearchGraphRuntime] = None


def get_runtime() -> ResearchGraphRuntime:
    """Get or create runtime singleton."""
    global _runtime
    if _runtime is None:
        _runtime = ResearchGraphRuntime()
    return _runtime


async def init_runtime(database_url: str) -> ResearchGraphRuntime:
    """Initialize runtime with database URL."""
    runtime = get_runtime()
    await runtime.initialize(database_url)
    return runtime


async def shutdown_runtime() -> None:
    """Shutdown runtime."""
    global _runtime
    if _runtime:
        await _runtime.shutdown()
        _runtime = None

