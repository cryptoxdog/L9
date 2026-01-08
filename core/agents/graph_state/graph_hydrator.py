"""
Graph Hydrator
==============

Converts Neo4j graph state to AgentInstance for runtime execution.
Bridges the gap between graph-backed state and the existing agent framework.

The hydrator combines:
- Immutable system kernels (Master, Safety) from YAML
- Mutable agent state (responsibilities, directives, SOPs) from Neo4j

Version: 1.0.0
Created: 2026-01-05
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any
from dataclasses import dataclass

import structlog

from .agent_graph_loader import AgentGraphState, AgentGraphLoader

if TYPE_CHECKING:
    from neo4j import AsyncDriver
    from core.agents.agent_instance import AgentInstance
    from core.kernels.kernel_loader import KernelStack

logger = structlog.get_logger(__name__)


@dataclass
class HydratedAgentContext:
    """
    Context for a hydrated agent combining graph state and kernels.
    
    This is the runtime representation passed to the executor.
    """
    agent_id: str
    designation: str
    role: str
    mission: str
    authority_level: str
    
    # From graph
    responsibilities: list[str]
    critical_directives: list[str]
    all_directives: list[dict]
    sops: dict[str, list[str]]
    available_tools: list[str]
    tools_requiring_approval: list[str]
    
    # From kernels (immutable)
    system_prompt: str
    safety_constraints: list[str]
    
    # Relationships
    supervisor_id: Optional[str] = None
    
    def to_system_prompt_context(self) -> str:
        """Generate system prompt context from hydrated state."""
        lines = [
            f"# Agent Identity: {self.designation}",
            f"Role: {self.role}",
            f"Mission: {self.mission}",
            f"Authority Level: {self.authority_level}",
            "",
            "## Responsibilities",
        ]
        
        for resp in self.responsibilities:
            lines.append(f"- {resp}")
        
        lines.extend([
            "",
            "## Critical Directives (NEVER violate)",
        ])
        
        for directive in self.critical_directives:
            lines.append(f"- {directive}")
        
        lines.extend([
            "",
            "## Available Tools",
        ])
        
        for tool in self.available_tools:
            approval = " [REQUIRES APPROVAL]" if tool in self.tools_requiring_approval else ""
            lines.append(f"- {tool}{approval}")
        
        if self.supervisor_id:
            lines.extend([
                "",
                f"## Supervisor: {self.supervisor_id}",
                "You MUST respect supervisor authority on all decisions.",
            ])
        
        return "\n".join(lines)


class GraphHydrator:
    """
    Hydrates agent state from Neo4j graph into runtime context.
    
    The hybrid approach:
    1. Load immutable system kernels (Master, Safety) from YAML
    2. Load mutable agent state from Neo4j graph
    3. Combine into HydratedAgentContext for execution
    
    Benefits:
    - System law (safety, governance) remains immutable
    - Agent-specific state can evolve at runtime
    - Fast startup (~100ms for graph query)
    - Full audit trail for state changes
    """
    
    def __init__(
        self,
        neo4j_driver: "AsyncDriver",
        kernel_stack: Optional["KernelStack"] = None,
    ):
        self.loader = AgentGraphLoader(neo4j_driver)
        self.kernel_stack = kernel_stack
    
    async def hydrate(
        self,
        agent_id: str,
        include_kernels: bool = True,
    ) -> HydratedAgentContext:
        """
        Hydrate agent context from graph + kernels.
        
        Args:
            agent_id: Agent to hydrate (e.g., "L")
            include_kernels: Whether to include YAML kernel content
        
        Returns:
            HydratedAgentContext ready for execution
        """
        logger.info("Hydrating agent from graph", agent_id=agent_id)
        
        # Load mutable state from Neo4j
        graph_state = await self.loader.load(agent_id)
        
        # Build system prompt from kernels if available
        system_prompt = ""
        safety_constraints = []
        
        if include_kernels and self.kernel_stack:
            system_prompt = self._build_system_prompt_from_kernels()
            safety_constraints = self._extract_safety_constraints()
        
        # Build hydrated context
        context = HydratedAgentContext(
            agent_id=graph_state.agent_id,
            designation=graph_state.designation,
            role=graph_state.role,
            mission=graph_state.mission,
            authority_level=graph_state.authority_level,
            responsibilities=[
                f"{r.title}: {r.description}"
                for r in graph_state.responsibilities
            ],
            critical_directives=[
                d.text for d in graph_state.directives
                if d.severity == "CRITICAL"
            ],
            all_directives=[
                {
                    "text": d.text,
                    "context": d.context,
                    "severity": d.severity,
                }
                for d in graph_state.directives
            ],
            sops={
                sop.name: sop.steps
                for sop in graph_state.sops
            },
            available_tools=[t.name for t in graph_state.tools],
            tools_requiring_approval=[
                t.name for t in graph_state.tools
                if t.requires_approval
            ],
            system_prompt=system_prompt,
            safety_constraints=safety_constraints,
            supervisor_id=graph_state.supervisor_id,
        )
        
        logger.info(
            "Hydrated agent context",
            agent_id=agent_id,
            responsibilities=len(context.responsibilities),
            critical_directives=len(context.critical_directives),
            tools=len(context.available_tools),
        )
        
        return context
    
    def _build_system_prompt_from_kernels(self) -> str:
        """Extract system prompt from kernel stack."""
        if not self.kernel_stack:
            return ""
        
        # This would integrate with existing kernel_loader
        # For now, return placeholder
        try:
            master_kernel = self.kernel_stack.get("master")
            if master_kernel and hasattr(master_kernel, "system_prompt"):
                return master_kernel.system_prompt
        except Exception as e:
            logger.warning("Could not load kernel system prompt", error=str(e))
        
        return ""
    
    def _extract_safety_constraints(self) -> list[str]:
        """Extract safety constraints from kernel stack."""
        if not self.kernel_stack:
            return []
        
        try:
            safety_kernel = self.kernel_stack.get("safety")
            if safety_kernel and hasattr(safety_kernel, "constraints"):
                return safety_kernel.constraints
        except Exception as e:
            logger.warning("Could not load safety constraints", error=str(e))
        
        return []
    
    async def refresh(self, agent_id: str) -> HydratedAgentContext:
        """
        Force refresh of agent state from graph.
        
        Call this after self-modify operations.
        """
        self.loader.invalidate_cache(agent_id)
        return await self.hydrate(agent_id)
    
    async def check_tool_approval(
        self,
        agent_id: str,
        tool_name: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Check if tool requires approval.
        
        Returns:
            (requires_approval, approval_source)
        """
        state = await self.loader.load(agent_id)
        
        for tool in state.tools:
            if tool.name == tool_name:
                return (tool.requires_approval, tool.approval_source)
        
        # Unknown tool - require approval by default
        return (True, "igor")
    
    async def validate_directive_compliance(
        self,
        agent_id: str,
        proposed_action: str,
    ) -> tuple[bool, list[str]]:
        """
        Validate proposed action against critical directives.
        
        Returns:
            (is_compliant, list of violated directives)
        """
        state = await self.loader.load(agent_id)
        
        violations = []
        critical_directives = state.get_critical_directives()
        
        # Simple keyword-based check (production would use LLM)
        for directive in critical_directives:
            # Check for obvious violations
            if "NO deletion" in directive.text and "delete" in proposed_action.lower():
                violations.append(directive.text)
            elif "MUST respect Igor" in directive.text and "override igor" in proposed_action.lower():
                violations.append(directive.text)
        
        return (len(violations) == 0, violations)

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "COR-FOUN-011",
    "component_name": "Graph Hydrator",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "foundation",
    "domain": "agent_execution",
    "type": "utility",
    "status": "active",
    "governance_level": "critical",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Provides graph hydrator components including HydratedAgentContext, GraphHydrator",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
