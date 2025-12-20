"""
L9 Research Factory - Tool Registry
Version: 2.0.0

In-memory tool registry for research tools.
NO database persistence - tools are registered at startup.

Production-ready features (v2.0.0):
- Time-based sliding window rate limiting
- Tool schema support for OpenAI function calling
- Async execution with timeout handling
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
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
    CUSTOM = "custom"


class ToolSchema(BaseModel):
    """JSON Schema for tool parameters (OpenAI function calling compatible)."""
    type: str = Field(default="object")
    properties: dict[str, Any] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)
    
    class Config:
        extra = "allow"


class ToolMetadata(BaseModel):
    """
    Metadata for a registered tool.
    
    Describes tool capabilities, access control, and rate limits.
    """
    id: str = Field(..., description="Unique tool identifier (canonical identity)")
    name: str = Field(..., description="Human-readable name (display only)")
    description: str = Field("", description="Tool description")
    tool_type: ToolType = Field(..., description="Type of tool")
    allowed_roles: list[str] = Field(
        default=["researcher"],
        description="Roles allowed to use this tool"
    )
    rate_limit: int = Field(
        default=60,
        description="Max calls per minute (sliding window)"
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
    input_schema: Optional[ToolSchema] = Field(
        default=None,
        description="JSON Schema for tool parameters"
    )
    
    class Config:
        use_enum_values = True


class RateLimitWindow:
    """
    Sliding window rate limiter.
    
    Tracks calls within a time window and enforces limits.
    """
    
    def __init__(self, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            window_seconds: Size of sliding window
        """
        self._window_seconds = window_seconds
        self._calls: dict[str, list[datetime]] = defaultdict(list)
    
    def check_and_increment(self, key: str, limit: int) -> bool:
        """
        Check if under rate limit and increment if so.
        
        Args:
            key: Rate limit key (e.g., tool_id)
            limit: Maximum calls per window
            
        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self._window_seconds)
        
        # Prune old calls
        self._calls[key] = [t for t in self._calls[key] if t > cutoff]
        
        # Check limit
        if len(self._calls[key]) >= limit:
            return False
        
        # Record call
        self._calls[key].append(now)
        return True
    
    def get_remaining(self, key: str, limit: int) -> int:
        """Get remaining calls in current window."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self._window_seconds)
        current = len([t for t in self._calls[key] if t > cutoff])
        return max(0, limit - current)
    
    def reset(self, key: Optional[str] = None) -> None:
        """Reset rate limits for a key or all keys."""
        if key:
            self._calls[key] = []
        else:
            self._calls.clear()


class ToolRegistry:
    """
    In-memory registry of available tools.
    
    Stores tool metadata and tool instances for execution.
    No database persistence - tools are registered at runtime.
    
    Production features:
    - Time-based sliding window rate limiting (1-minute window)
    - Async tool execution with timeout
    - Tool schema extraction for function calling
    """
    
    def __init__(self, rate_window_seconds: int = 60):
        """
        Initialize empty registry.
        
        Args:
            rate_window_seconds: Sliding window for rate limiting
        """
        self._tools: dict[str, ToolMetadata] = {}
        self._executors: dict[str, Any] = {}  # Tool instances
        self._rate_limiter = RateLimitWindow(rate_window_seconds)
    
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
        Check if tool is within rate limit (sliding window).
        
        Uses time-based sliding window rate limiting.
        
        Returns:
            True if allowed (and increments counter), False if rate limited
        """
        metadata = self._tools.get(tool_id)
        if not metadata:
            return False
        
        return self._rate_limiter.check_and_increment(tool_id, metadata.rate_limit)
    
    def get_rate_limit_remaining(self, tool_id: str) -> int:
        """Get remaining calls in current rate limit window."""
        metadata = self._tools.get(tool_id)
        if not metadata:
            return 0
        return self._rate_limiter.get_remaining(tool_id, metadata.rate_limit)
    
    def reset_rate_limits(self, tool_id: Optional[str] = None) -> None:
        """Reset rate limit counters for a tool or all tools."""
        self._rate_limiter.reset(tool_id)
    
    def get_tool_schema(self, tool_id: str) -> dict[str, Any]:
        """
        Get OpenAI function calling schema for a tool.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            JSON Schema dict for function parameters
        """
        metadata = self._tools.get(tool_id)
        if not metadata:
            return {"type": "object", "properties": {}}
        
        if metadata.input_schema:
            return metadata.input_schema.model_dump()
        
        # Return default schema
        return {"type": "object", "properties": {}}
    
    async def execute_tool(
        self,
        tool_id: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a tool with timeout handling.
        
        Args:
            tool_id: Tool to execute
            arguments: Arguments for tool
            
        Returns:
            Dict with success, result/error, duration_ms
        """
        start_time = datetime.utcnow()
        
        metadata = self._tools.get(tool_id)
        if not metadata:
            return {
                "success": False,
                "error": f"Tool not found: {tool_id}",
                "duration_ms": 0,
            }
        
        if not metadata.enabled:
            return {
                "success": False,
                "error": f"Tool is disabled: {tool_id}",
                "duration_ms": 0,
            }
        
        # Check rate limit
        if not self.check_rate_limit(tool_id):
            return {
                "success": False,
                "error": f"Rate limit exceeded for {tool_id}",
                "duration_ms": 0,
            }
        
        executor = self._executors.get(tool_id)
        if not executor:
            return {
                "success": False,
                "error": f"No executor for tool: {tool_id}",
                "duration_ms": 0,
            }
        
        try:
            # Execute with timeout
            timeout = metadata.timeout_seconds
            
            if hasattr(executor, "execute"):
                if asyncio.iscoroutinefunction(executor.execute):
                    result = await asyncio.wait_for(
                        executor.execute(**arguments),
                        timeout=timeout,
                    )
                else:
                    # Wrap sync in executor
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, lambda: executor.execute(**arguments)),
                        timeout=timeout,
                    )
            elif callable(executor):
                if asyncio.iscoroutinefunction(executor):
                    result = await asyncio.wait_for(
                        executor(**arguments),
                        timeout=timeout,
                    )
                else:
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, lambda: executor(**arguments)),
                        timeout=timeout,
                    )
            else:
                return {
                    "success": False,
                    "error": f"Executor not callable: {tool_id}",
                    "duration_ms": 0,
                }
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info(f"Tool {tool_id} completed in {duration_ms}ms")
            
            return {
                "success": True,
                "result": result,
                "duration_ms": duration_ms,
            }
            
        except asyncio.TimeoutError:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.warning(f"Tool {tool_id} timed out after {timeout}s")
            return {
                "success": False,
                "error": f"Tool execution timed out after {timeout}s",
                "duration_ms": duration_ms,
            }
        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.exception(f"Tool {tool_id} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration_ms": duration_ms,
            }


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
    """Initialize default tools in registry with schemas."""
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
        input_schema=ToolSchema(
            type="object",
            properties={
                "query": {
                    "type": "string",
                    "description": "Search query to send to Perplexity",
                },
                "focus": {
                    "type": "string",
                    "description": "Search focus area",
                    "enum": ["internet", "academic", "writing", "wolfram", "youtube", "reddit"],
                },
            },
            required=["query"],
        ),
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
        input_schema=ToolSchema(
            type="object",
            properties={
                "url": {
                    "type": "string",
                    "description": "URL to request",
                },
                "method": {
                    "type": "string",
                    "description": "HTTP method",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "default": "GET",
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers",
                },
                "body": {
                    "type": "object",
                    "description": "Request body (for POST/PUT/PATCH)",
                },
            },
            required=["url"],
        ),
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
        input_schema=ToolSchema(
            type="object",
            properties={
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
            },
            required=["query"],
        ),
    )
    registry.register(mock_meta, MockSearchTool())
    
    # Calculator (commonly needed)
    calc_meta = ToolMetadata(
        id="calculate",
        name="Calculator",
        description="Perform mathematical calculations",
        tool_type=ToolType.MOCK,
        allowed_roles=["researcher", "planner"],
        rate_limit=1000,
        timeout_seconds=5,
        input_schema=ToolSchema(
            type="object",
            properties={
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate",
                },
            },
            required=["expression"],
        ),
    )
    
    # Simple calculator executor
    def calculate_executor(expression: str) -> dict:
        try:
            # Safe eval for simple math
            allowed_names = {"abs": abs, "round": round, "min": min, "max": max}
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return {"result": result, "expression": expression}
        except Exception as e:
            return {"error": str(e), "expression": expression}
    
    registry.register(calc_meta, calculate_executor)
    
    logger.info(f"Initialized {len(registry.list_all())} default tools")

