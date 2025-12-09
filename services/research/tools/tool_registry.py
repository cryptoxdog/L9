"""
L9 Research Factory - Tool Registry
Version: 1.0.0

In-memory tool registry for research tools.
NO database persistence - tools are registered at startup.
"""

import logging
from enum import Enum
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolType(str, Enum):
    """Types of available tools."""
    SEARCH = "search"
    HTTP = "http"
    PERPLEXITY = "perplexity"
    MOCK = "mock"


class ToolMetadata(BaseModel):
    """
    Metadata for a registered tool.
    
    Describes tool capabilities, access control, and rate limits.
    """
    id: str = Field(..., description="Unique tool identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field("", description="Tool description")
    tool_type: ToolType = Field(..., description="Type of tool")
    allowed_roles: list[str] = Field(
        default=["researcher"],
        description="Roles allowed to use this tool"
    )
    rate_limit: int = Field(
        default=60,
        description="Max calls per minute"
    )
    timeout_seconds: int = Field(
        default=30,
        description="Timeout for tool execution"
    )
    enabled: bool = Field(
        default=True,
        description="Whether tool is enabled"
    )
    requires_api_key: bool = Field(
        default=False,
        description="Whether tool requires API key"
    )
    
    class Config:
        use_enum_values = True


class ToolRegistry:
    """
    In-memory registry of available tools.
    
    Stores tool metadata and tool instances for execution.
    No database persistence - tools are registered at runtime.
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._tools: dict[str, ToolMetadata] = {}
        self._executors: dict[str, Any] = {}  # Tool instances
        self._rate_counters: dict[str, int] = {}
    
    def register(
        self,
        metadata: ToolMetadata,
        executor: Optional[Any] = None,
    ) -> None:
        """
        Register a tool with the registry.
        
        Args:
            metadata: Tool metadata
            executor: Optional tool instance for execution
        """
        self._tools[metadata.id] = metadata
        if executor:
            self._executors[metadata.id] = executor
        
        logger.info(f"Registered tool: {metadata.name} ({metadata.id})")
    
    def get(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool metadata by ID."""
        return self._tools.get(tool_id)
    
    def get_executor(self, tool_id: str) -> Optional[Any]:
        """Get tool executor instance by ID."""
        return self._executors.get(tool_id)
    
    def get_by_type(self, tool_type: ToolType) -> list[ToolMetadata]:
        """Get all tools of a specific type."""
        return [
            t for t in self._tools.values()
            if t.tool_type == tool_type and t.enabled
        ]
    
    def get_for_role(self, role: str) -> list[ToolMetadata]:
        """Get all tools available for a role."""
        return [
            t for t in self._tools.values()
            if role in t.allowed_roles and t.enabled
        ]
    
    def list_all(self) -> list[ToolMetadata]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def list_enabled(self) -> list[ToolMetadata]:
        """List only enabled tools."""
        return [t for t in self._tools.values() if t.enabled]
    
    def disable(self, tool_id: str) -> None:
        """Disable a tool."""
        if tool_id in self._tools:
            self._tools[tool_id].enabled = False
            logger.info(f"Disabled tool: {tool_id}")
    
    def enable(self, tool_id: str) -> None:
        """Enable a tool."""
        if tool_id in self._tools:
            self._tools[tool_id].enabled = True
            logger.info(f"Enabled tool: {tool_id}")
    
    def check_rate_limit(self, tool_id: str) -> bool:
        """
        Check if tool is within rate limit.
        
        Returns True if allowed, False if rate limited.
        Note: Simple counter, should use time-based window in production.
        """
        metadata = self._tools.get(tool_id)
        if not metadata:
            return False
        
        current = self._rate_counters.get(tool_id, 0)
        if current >= metadata.rate_limit:
            return False
        
        self._rate_counters[tool_id] = current + 1
        return True
    
    def reset_rate_limits(self) -> None:
        """Reset all rate limit counters."""
        self._rate_counters.clear()


# Singleton instance
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create tool registry singleton."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
        _initialize_default_tools(_registry)
    return _registry


def _initialize_default_tools(registry: ToolRegistry) -> None:
    """Initialize default tools in registry."""
    from services.research.tools.tool_wrappers import (
        PerplexityTool,
        HTTPTool,
        MockSearchTool,
    )
    
    # Perplexity Search
    perplexity_meta = ToolMetadata(
        id="perplexity_search",
        name="Perplexity Search",
        description="Search and synthesize information using Perplexity AI",
        tool_type=ToolType.PERPLEXITY,
        allowed_roles=["researcher", "planner"],
        rate_limit=20,
        timeout_seconds=60,
        requires_api_key=True,
    )
    registry.register(perplexity_meta, PerplexityTool())
    
    # HTTP Request
    http_meta = ToolMetadata(
        id="http_request",
        name="HTTP Request",
        description="Make HTTP requests to external APIs",
        tool_type=ToolType.HTTP,
        allowed_roles=["researcher"],
        rate_limit=100,
        timeout_seconds=30,
    )
    registry.register(http_meta, HTTPTool())
    
    # Mock Search (for testing without API keys)
    mock_meta = ToolMetadata(
        id="mock_search",
        name="Mock Search",
        description="Mock search tool for testing",
        tool_type=ToolType.MOCK,
        allowed_roles=["researcher", "planner"],
        rate_limit=1000,
        timeout_seconds=5,
    )
    registry.register(mock_meta, MockSearchTool())
    
    logger.info(f"Initialized {len(registry.list_all())} default tools")

