"""
L9 Core Tools - Registry Adapter
================================

Adapts the existing tool registry for use with AgentExecutorService.

This adapter:
- Implements ToolRegistryProtocol expected by executor
- Wraps the existing services.research.tools.tool_registry
- Converts ToolMetadata to ToolBinding
- Dispatches tool calls and returns ToolCallResult
- Integrates with GovernanceEngineService for policy-based access control

Version: 2.0.0 (Governance Integration)
"""

from __future__ import annotations

import asyncio
import structlog
from datetime import datetime
from typing import Any, Optional, Protocol, TYPE_CHECKING
from uuid import uuid4

from core.agents.schemas import (
    ToolBinding,
    ToolCallResult,
)
from core.schemas.capabilities import ToolName, DEFAULT_L_CAPABILITIES

if TYPE_CHECKING:
    from core.governance.engine import GovernanceEngineService

logger = structlog.get_logger(__name__)


# =============================================================================
# Tool Executor Protocol
# =============================================================================


class ToolExecutor(Protocol):
    """Protocol for tool executors."""

    async def execute(self, **kwargs) -> Any:
        """Execute the tool with arguments."""
        ...


# =============================================================================
# Risk Levels
# =============================================================================


class RiskLevel:
    """Risk levels for tools."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Side-effect tools that require governance approval
SIDE_EFFECT_TOOLS = {
    "http_request",  # Can make external requests
}

# Tools with elevated risk
HIGH_RISK_TOOLS = {
    "shell_exec",
    "file_write",
    "database_write",
}


# =============================================================================
# Executor Tool Registry
# =============================================================================


class ExecutorToolRegistry:
    """
    Tool registry adapter for AgentExecutorService.

    Wraps the existing tool registry and provides:
    - ToolBinding conversion for agent context
    - Tool dispatch with result wrapping
    - Governance engine integration for policy-based access
    - Rate limiting checks

    Attributes:
        base_registry: The underlying tool registry
        governance_engine: Optional governance engine for policy evaluation
    """

    def __init__(
        self,
        base_registry: Optional[Any] = None,
        governance_enabled: bool = True,
        governance_engine: Optional["GovernanceEngineService"] = None,
    ):
        """
        Initialize the adapter.

        Args:
            base_registry: Existing ToolRegistry (auto-creates if None)
            governance_enabled: Whether to enforce governance (legacy flag)
            governance_engine: GovernanceEngineService for policy evaluation
        """
        # Get or create base registry
        if base_registry is None:
            try:
                from services.research.tools.tool_registry import get_tool_registry

                self._registry = get_tool_registry()
            except ImportError:
                logger.warning("Could not import tool_registry, using empty registry")
                self._registry = None
        else:
            self._registry = base_registry

        self._governance_enabled = governance_enabled
        self._governance_engine = governance_engine
        self._approved_overrides: dict[
            str, set[str]
        ] = {}  # agent_id -> approved tool IDs

        logger.info(
            "ExecutorToolRegistry initialized: governance=%s, engine=%s, tools=%d",
            governance_enabled,
            "attached" if governance_engine else "none",
            len(self._registry.list_all()) if self._registry else 0,
        )

    def set_governance_engine(self, engine: "GovernanceEngineService") -> None:
        """Attach a governance engine for policy evaluation."""
        self._governance_engine = engine
        logger.info("Governance engine attached to tool registry")

    # =========================================================================
    # ToolRegistryProtocol Implementation
    # =========================================================================

    def get_approved_tools(
        self,
        agent_id: str,
        principal_id: str,
    ) -> list[ToolBinding]:
        """
        Get list of tools approved for an agent.

        Converts ToolMetadata to ToolBinding format expected by AgentInstance.
        Uses governance engine for policy-based filtering if available,
        falls back to hardcoded rules otherwise.

        Args:
            agent_id: Agent identifier
            principal_id: Principal requesting tools

        Returns:
            List of approved ToolBinding objects
        """
        if self._registry is None:
            return []

        bindings: list[ToolBinding] = []

        for tool_meta in self._registry.list_enabled():
            # Map registry tool ID to ToolName enum when possible so we can
            # enforce capabilities for L using DEFAULT_L_CAPABILITIES.
            tool_enum: Optional[ToolName] = None
            try:
                tool_enum = ToolName(tool_meta.id)
            except ValueError:
                tool_enum = None

            # Enforce AgentCapabilities for L (agent ids that alias L)
            if agent_id in ("L", "l-cto", "l9-standard-v1") and tool_enum is not None:
                cap = DEFAULT_L_CAPABILITIES.get_capability(tool_enum)
                if not cap or not cap.allowed:
                    logger.debug(
                        "Tool %s denied for agent %s by capabilities profile",
                        tool_meta.id,
                        agent_id,
                    )
                    continue

            # Use governance engine if available
            if self._governance_engine:
                allowed = self._governance_engine.is_allowed(
                    subject=agent_id,
                    action="tool.execute",
                    resource=tool_meta.id,
                    context={"principal_id": principal_id},
                )
                if not allowed:
                    logger.debug(
                        "Tool %s denied for agent %s by governance policy",
                        tool_meta.id,
                        agent_id,
                    )
                    continue
            elif self._governance_enabled:
                # Fallback to hardcoded rules
                if tool_meta.id in SIDE_EFFECT_TOOLS:
                    if not self._is_approved(agent_id, tool_meta.id):
                        logger.debug(
                            "Tool %s denied for agent %s (side-effect, not approved)",
                            tool_meta.id,
                            agent_id,
                        )
                        continue

                if tool_meta.id in HIGH_RISK_TOOLS:
                    logger.debug(
                        "Tool %s denied for agent %s (high-risk)",
                        tool_meta.id,
                        agent_id,
                    )
                    continue

            # Convert to ToolBinding (tool_id is canonical identity)
            # Use registry's schema method if available
            if hasattr(self._registry, "get_tool_schema"):
                schema = self._registry.get_tool_schema(tool_meta.id)
            else:
                schema = self._get_tool_schema(tool_meta.id)

            binding = ToolBinding(
                tool_id=tool_meta.id,
                display_name=tool_meta.name,  # UI/logs only
                description=tool_meta.description,
                input_schema=schema,
                enabled=True,
            )
            bindings.append(binding)

        logger.debug(
            "Approved %d tools for agent %s",
            len(bindings),
            agent_id,
        )

        return bindings

    async def dispatch_tool_call(
        self,
        tool_id: str,
        arguments: dict[str, Any],
        context: dict[str, Any],
    ) -> ToolCallResult:
        """
        Dispatch a tool call and return result.

        Uses tool_id as the sole identity for lookup and dispatch.
        Governance is checked via engine if available.

        Args:
            tool_id: Canonical tool identity
            arguments: Arguments for tool
            context: Execution context

        Returns:
            ToolCallResult with success/failure, result, and tool_id
        """
        call_id = uuid4()
        start_time = datetime.utcnow()

        try:
            # Get tool from registry using tool_id
            if self._registry is None:
                return ToolCallResult(
                    call_id=call_id,
                    tool_id=tool_id,
                    success=False,
                    error="Tool registry not available",
                )

            tool_meta = self._registry.get(tool_id)
            if tool_meta is None:
                return ToolCallResult(
                    call_id=call_id,
                    tool_id=tool_id,
                    success=False,
                    error=f"Tool not found: {tool_id}",
                )

            # Check if tool is enabled
            if not tool_meta.enabled:
                return ToolCallResult(
                    call_id=call_id,
                    tool_id=tool_id,
                    success=False,
                    error=f"Tool is disabled: {tool_id}",
                )

            # Governance check - use engine if available, else fallback
            agent_id = context.get("agent_id", "unknown")

            if self._governance_engine:
                # Use policy-based governance
                allowed = self._governance_engine.is_allowed(
                    subject=agent_id,
                    action="tool.execute",
                    resource=tool_id,
                    context=context,
                )
                if not allowed:
                    return ToolCallResult(
                        call_id=call_id,
                        tool_id=tool_id,
                        success=False,
                        error=f"Tool {tool_id} denied by governance policy",
                    )
            elif self._governance_enabled:
                # Fallback to hardcoded rules
                if tool_id in SIDE_EFFECT_TOOLS:
                    if not self._is_approved(agent_id, tool_id):
                        return ToolCallResult(
                            call_id=call_id,
                            tool_id=tool_id,
                            success=False,
                            error=f"Tool {tool_id} requires governance approval",
                        )

            # Use registry's execute_tool if available (handles timeout)
            if hasattr(self._registry, "execute_tool"):
                logger.info(
                    "Executing tool via registry: %s with arguments: %s",
                    tool_id,
                    arguments,
                )
                result = await self._registry.execute_tool(tool_id, arguments)

                if result["success"]:
                    return ToolCallResult(
                        call_id=call_id,
                        tool_id=tool_id,
                        success=True,
                        result=result["result"],
                        duration_ms=result["duration_ms"],
                    )
                else:
                    return ToolCallResult(
                        call_id=call_id,
                        tool_id=tool_id,
                        success=False,
                        error=result["error"],
                        duration_ms=result.get("duration_ms", 0),
                    )

            # Fallback: direct execution (legacy path)
            executor = self._registry.get_executor(tool_id)
            if executor is None:
                return ToolCallResult(
                    call_id=call_id,
                    tool_id=tool_id,
                    success=False,
                    error=f"No executor registered for tool: {tool_id}",
                )

            logger.info(
                "Executing tool: %s with arguments: %s",
                tool_id,
                arguments,
            )

            # Handle both sync and async executors
            if hasattr(executor, "execute"):
                if asyncio.iscoroutinefunction(executor.execute):
                    result = await executor.execute(**arguments)
                else:
                    result = executor.execute(**arguments)
            elif callable(executor):
                if asyncio.iscoroutinefunction(executor):
                    result = await executor(**arguments)
                else:
                    result = executor(**arguments)
            else:
                return ToolCallResult(
                    call_id=call_id,
                    tool_id=tool_id,
                    success=False,
                    error=f"Tool executor is not callable: {tool_id}",
                )

            # Calculate duration
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            logger.info(
                "Tool %s completed in %dms",
                tool_id,
                duration_ms,
            )

            return ToolCallResult(
                call_id=call_id,
                tool_id=tool_id,
                success=True,
                result=result,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.exception("Tool execution failed: %s", str(e))

            return ToolCallResult(
                call_id=call_id,
                tool_id=tool_id,
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )

    # =========================================================================
    # Governance
    # =========================================================================

    def approve_tool(self, agent_id: str, tool_id: str) -> None:
        """
        Explicitly approve a tool for an agent.

        Used to grant access to side-effect tools.

        Args:
            agent_id: Agent identifier
            tool_id: Tool to approve
        """
        if agent_id not in self._approved_overrides:
            self._approved_overrides[agent_id] = set()
        self._approved_overrides[agent_id].add(tool_id)

        logger.info("Approved tool %s for agent %s", tool_id, agent_id)

    def revoke_tool(self, agent_id: str, tool_id: str) -> None:
        """
        Revoke approval for a tool.

        Args:
            agent_id: Agent identifier
            tool_id: Tool to revoke
        """
        if agent_id in self._approved_overrides:
            self._approved_overrides[agent_id].discard(tool_id)

        logger.info("Revoked tool %s for agent %s", tool_id, agent_id)

    def _is_approved(self, agent_id: str, tool_id: str) -> bool:
        """Check if a tool is explicitly approved for an agent."""
        return (
            agent_id in self._approved_overrides
            and tool_id in self._approved_overrides[agent_id]
        )

    # =========================================================================
    # Schema Helpers
    # =========================================================================

    def _get_tool_schema(self, tool_id: str) -> dict[str, Any]:
        """
        Get JSON Schema for a tool's parameters.

        Returns a basic schema based on tool type.
        In production, tools would provide their own schemas.
        """
        # Basic schemas for known tools
        schemas = {
            "perplexity_search": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                },
                "required": ["query"],
            },
            "http_request": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to request",
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE"],
                        "default": "GET",
                    },
                    "body": {
                        "type": "object",
                        "description": "Request body (for POST/PUT)",
                    },
                },
                "required": ["url"],
            },
            "mock_search": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                },
                "required": ["query"],
            },
        }

        return schemas.get(tool_id, {"type": "object", "properties": {}})

    # =========================================================================
    # Registry Passthrough
    # =========================================================================

    def register_tool(
        self,
        tool_id: str,
        name: str,
        description: str,
        executor: Any,
        tool_type: str = "custom",
        **kwargs,
    ) -> None:
        """
        Register a new tool.

        Args:
            tool_id: Unique tool identifier
            name: Human-readable name
            description: Tool description
            executor: Callable or object with execute method
            tool_type: Tool type category
            **kwargs: Additional metadata
        """
        if self._registry is None:
            logger.error("Cannot register tool: no base registry")
            return

        try:
            from services.research.tools.tool_registry import ToolMetadata, ToolType

            # Try to get tool type enum, default to MOCK if unknown
            try:
                tt = ToolType(tool_type)
            except ValueError:
                tt = ToolType.MOCK

            metadata = ToolMetadata(
                id=tool_id,
                name=name,
                description=description,
                tool_type=tt,
                **kwargs,
            )
            self._registry.register(metadata, executor)

        except ImportError:
            logger.error("Cannot register tool: tool_registry not available")

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools."""
        if self._registry is None:
            return []

        return [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "enabled": t.enabled,
                "type": t.tool_type,
            }
            for t in self._registry.list_all()
        ]


# =============================================================================
# Factory Function
# =============================================================================


def create_executor_tool_registry(
    governance_enabled: bool = True,
    base_registry: Optional[Any] = None,
    governance_engine: Optional["GovernanceEngineService"] = None,
) -> ExecutorToolRegistry:
    """
    Factory function to create an ExecutorToolRegistry.

    Args:
        governance_enabled: Whether to enforce governance (legacy)
        base_registry: Optional base registry to wrap
        governance_engine: Optional GovernanceEngineService for policy evaluation

    Returns:
        Configured ExecutorToolRegistry
    """
    return ExecutorToolRegistry(
        base_registry=base_registry,
        governance_enabled=governance_enabled,
        governance_engine=governance_engine,
    )


def get_tool_registry_adapter() -> ExecutorToolRegistry:
    """
    Get a default ExecutorToolRegistry instance.

    Used as a FastAPI dependency.
    """
    return create_executor_tool_registry(governance_enabled=True)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "ExecutorToolRegistry",
    "create_executor_tool_registry",
    "RiskLevel",
    "SIDE_EFFECT_TOOLS",
    "HIGH_RISK_TOOLS",
    "register_l_tools",
]


# =============================================================================
# L-CTO Tool Registration
# =============================================================================


async def register_l_tools() -> int:
    """
    Register all L-CTO tools in the tool registry with governance metadata.

    Called once at server startup.
    Each tool gets:
      - Execution function from runtime.l_tools
      - Governance metadata (scope, risk_level, requires_approval)
      - Input schema for validation
      - Registration in base registry for dispatch

    Returns:
        Number of tools registered

    Raises:
        Exception: If registration fails
    """
    from core.tools.tool_graph import ToolGraph, ToolDefinition
    from runtime.l_tools import (
        memory_search,
        memory_write,
        gmp_run,
        git_commit,
        mac_agent_exec_task,
        mcp_call_tool,
        world_model_query,
        kernel_read,
    )
    from runtime.long_plan_tool import (
        long_plan_execute_tool,
        long_plan_simulate_tool,
    )
    from services.research.tools.tool_registry import (
        get_tool_registry,
        ToolMetadata,
        ToolType,
    )

    # Get base registry for executor registration
    base_registry = get_tool_registry()

    # =========================================================================
    # SymPy Symbolic Computation Tools (GMP-SYMPY-TASK4)
    # =========================================================================
    sympy_tool = None
    try:
        from services.symbolic_computation.tools.symbolic_tool import SymPyTool

        sympy_tool = SymPyTool()
        logger.info("SymPyTool initialized for registration")
    except ImportError as e:
        logger.debug(f"SymPyTool not available: {e}")

    # Map tool names to their executor functions
    TOOL_EXECUTORS = {
        "memory_search": memory_search,
        "memory_write": memory_write,
        "gmp_run": gmp_run,
        "git_commit": git_commit,
        "mac_agent_exec_task": mac_agent_exec_task,
        "mcp_call_tool": mcp_call_tool,
        "world_model_query": world_model_query,
        "kernel_read": kernel_read,
        "long_plan.execute": long_plan_execute_tool,
        "long_plan.simulate": long_plan_simulate_tool,
    }

    # Add SymPy tools if available
    if sympy_tool:
        TOOL_EXECUTORS["symbolic_evaluate"] = sympy_tool.evaluate
        TOOL_EXECUTORS["symbolic_codegen"] = sympy_tool.generate_code
        TOOL_EXECUTORS["symbolic_optimize"] = sympy_tool.optimize

    logger.info("Registering L-CTO tools...")

    # Define all L-CTO tools with metadata
    tools_to_register = [
        ToolDefinition(
            name="memory_search",
            description="Search L's memory substrate using semantic search",
            category="memory",
            scope="internal",
            risk_level="low",
            requires_igor_approval=False,
            requires_confirmation=False,
            is_destructive=False,
            agent_id="L",
        ),
        ToolDefinition(
            name="memory_write",
            description="Write to L's memory substrate",
            category="memory",
            scope="internal",
            risk_level="medium",
            requires_igor_approval=False,
            requires_confirmation=False,
            is_destructive=False,
            agent_id="L",
        ),
        ToolDefinition(
            name="gmp_run",
            description="Execute a GMP (Governance Management Process)",
            category="governance",
            scope="requires_igor_approval",
            risk_level="high",
            requires_igor_approval=True,
            requires_confirmation=True,
            is_destructive=False,
            agent_id="L",
        ),
        ToolDefinition(
            name="git_commit",
            description="Commit code changes to git repository",
            category="vcs",
            scope="requires_igor_approval",
            risk_level="high",
            requires_igor_approval=True,
            requires_confirmation=True,
            is_destructive=True,
            agent_id="L",
        ),
        ToolDefinition(
            name="mac_agent_exec_task",
            description="Execute command via Mac agent",
            category="execution",
            scope="requires_igor_approval",
            risk_level="high",
            requires_igor_approval=True,
            requires_confirmation=True,
            is_destructive=True,
            agent_id="L",
        ),
        ToolDefinition(
            name="mcp_call_tool",
            description="Call a tool via MCP (Model Context Protocol)",
            category="external",
            scope="external",
            risk_level="medium",
            requires_igor_approval=False,
            requires_confirmation=False,
            is_destructive=False,
            agent_id="L",
        ),
        ToolDefinition(
            name="world_model_query",
            description="Query the world model",
            category="world_model",
            scope="internal",
            risk_level="low",
            requires_igor_approval=False,
            requires_confirmation=False,
            is_destructive=False,
            agent_id="L",
        ),
        ToolDefinition(
            name="kernel_read",
            description="Read a property from a kernel",
            category="kernel",
            scope="internal",
            risk_level="low",
            requires_igor_approval=False,
            requires_confirmation=False,
            is_destructive=False,
            agent_id="L",
        ),
        ToolDefinition(
            name="long_plan.execute",
            description="Execute a long plan through LangGraph DAG",
            category="orchestration",
            scope="internal",
            risk_level="medium",
            requires_igor_approval=False,
            requires_confirmation=True,
            is_destructive=True,
            agent_id="L",
        ),
        ToolDefinition(
            name="long_plan.simulate",
            description="Simulate a long plan without executing (dry run)",
            category="orchestration",
            scope="internal",
            risk_level="low",
            requires_igor_approval=False,
            requires_confirmation=False,
            is_destructive=False,
            agent_id="L",
        ),
    ]

    # Add SymPy tool definitions if available (GMP-SYMPY-TASK4)
    if sympy_tool:
        tools_to_register.extend([
            ToolDefinition(
                name="symbolic_evaluate",
                description="Evaluate symbolic mathematical expressions numerically",
                category="computation",
                scope="internal",
                risk_level="low",
                requires_igor_approval=False,
                requires_confirmation=False,
                is_destructive=False,
                agent_id="L",
            ),
            ToolDefinition(
                name="symbolic_codegen",
                description="Generate compilable C/Fortran/Python code from symbolic expressions",
                category="computation",
                scope="internal",
                risk_level="low",
                requires_igor_approval=False,
                requires_confirmation=False,
                is_destructive=False,
                agent_id="L",
            ),
            ToolDefinition(
                name="symbolic_optimize",
                description="Optimize and simplify symbolic expressions using CSE",
                category="computation",
                scope="internal",
                risk_level="low",
                requires_igor_approval=False,
                requires_confirmation=False,
                is_destructive=False,
                agent_id="L",
            ),
        ])

    # Register each tool in BOTH Neo4j AND base registry
    registered_count = 0
    for tool_def in tools_to_register:
        try:
            # 1. Register in Neo4j (for graph queries and governance metadata)
            success = await ToolGraph.register_tool(tool_def)
            if success:
                logger.debug(f"Neo4j: registered {tool_def.name}")
            else:
                logger.debug(f"Neo4j: skipped {tool_def.name} (unavailable)")

            # 2. Register in base registry (for dispatch execution)
            executor_func = TOOL_EXECUTORS.get(tool_def.name)
            if executor_func:
                metadata = ToolMetadata(
                    id=tool_def.name,
                    name=tool_def.name,
                    description=tool_def.description,
                    tool_type=ToolType.CUSTOM,
                    allowed_roles=["l-cto", "researcher", "agent"],
                    rate_limit=60,
                    timeout_seconds=120
                    if tool_def.name in ["gmp_run", "mac_agent_exec_task"]
                    else 30,
                    enabled=True,
                    requires_api_key=False,
                    input_schema=None,  # Schemas are in core/schemas/l_tools.py
                )
                base_registry.register(metadata, executor_func)
                logger.info(
                    f"✓ Registered tool: {tool_def.name} (risk={tool_def.risk_level})"
                )
            else:
                logger.warning(f"No executor found for tool: {tool_def.name}")

            registered_count += 1
        except Exception as e:
            logger.error(f"✗ Failed to register {tool_def.name}: {e}")
            raise

    high_risk_count = sum(1 for t in tools_to_register if t.requires_igor_approval)
    logger.info(
        f"✓✓ L-CTO tools registered: {registered_count} total, "
        f"{high_risk_count} high-risk requiring approval, "
        f"executors wired to base registry"
    )

    return registered_count
