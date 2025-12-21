"""
L9 Core Tools - Tool Dependency Graph
======================================

Tracks tool dependencies in Neo4j for:
- Understanding blast radius (what breaks if API X goes down)
- Auto-generating architecture diagrams
- Detecting circular dependencies
- API usage monitoring

Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """Definition of a tool for graph registration."""
    name: str
    description: str = ""
    external_apis: list[str] = field(default_factory=list)
    internal_dependencies: list[str] = field(default_factory=list)
    agent_id: str | None = None
    category: str = "general"
    is_destructive: bool = False
    requires_confirmation: bool = False


class ToolGraph:
    """
    Tool dependency graph backed by Neo4j.
    
    Graph structure:
        (Tool)-[:USES]->(API)
        (Tool)-[:DEPENDS_ON]->(Tool)
        (Agent)-[:HAS_TOOL]->(Tool)
    """
    
    @staticmethod
    async def _get_neo4j():
        """Get Neo4j client or None."""
        try:
            from memory.graph_client import get_neo4j_client
            return await get_neo4j_client()
        except ImportError:
            return None
    
    @staticmethod
    async def register_tool(tool: ToolDefinition) -> bool:
        """
        Register a tool and its dependencies in Neo4j.
        
        Creates:
        - Tool node
        - API nodes for external dependencies
        - USES relationships to APIs
        - DEPENDS_ON relationships to other tools
        - HAS_TOOL relationship from agent (if agent_id provided)
        
        Args:
            tool: Tool definition to register
            
        Returns:
            True if registered successfully
        """
        neo4j = await ToolGraph._get_neo4j()
        if not neo4j:
            logger.debug(f"Neo4j unavailable - skipping tool registration: {tool.name}")
            return False
        
        try:
            # Create tool node
            await neo4j.create_entity(
                entity_type="Tool",
                entity_id=tool.name,
                properties={
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "is_destructive": tool.is_destructive,
                    "requires_confirmation": tool.requires_confirmation,
                    "registered_at": datetime.utcnow().isoformat(),
                },
            )
            
            # Create API nodes and USES relationships
            for api in tool.external_apis:
                await neo4j.create_entity(
                    entity_type="API",
                    entity_id=api,
                    properties={"name": api, "type": "external"},
                )
                await neo4j.create_relationship(
                    from_type="Tool",
                    from_id=tool.name,
                    to_type="API",
                    to_id=api,
                    rel_type="USES",
                )
            
            # Create DEPENDS_ON relationships to other tools
            for dep in tool.internal_dependencies:
                await neo4j.create_relationship(
                    from_type="Tool",
                    from_id=tool.name,
                    to_type="Tool",
                    to_id=dep,
                    rel_type="DEPENDS_ON",
                )
            
            # Link to agent if specified
            if tool.agent_id:
                await neo4j.create_relationship(
                    from_type="Agent",
                    from_id=tool.agent_id,
                    to_type="Tool",
                    to_id=tool.name,
                    rel_type="HAS_TOOL",
                )
            
            logger.info(f"Registered tool in graph: {tool.name}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to register tool {tool.name}: {e}")
            return False
    
    @staticmethod
    async def get_api_dependents(api_name: str) -> list[str]:
        """
        Get all tools that depend on an API.
        
        Use case: "What breaks if Perplexity goes down?"
        
        Args:
            api_name: API identifier
            
        Returns:
            List of tool names that use this API
        """
        neo4j = await ToolGraph._get_neo4j()
        if not neo4j:
            return []
        
        try:
            result = await neo4j.run_query("""
                MATCH (t:Tool)-[:USES]->(a:API {id: $api_name})
                RETURN t.id as tool_name
            """, {"api_name": api_name})
            
            return [r["tool_name"] for r in result] if result else []
        except Exception:
            return []
    
    @staticmethod
    async def get_tool_dependencies(tool_name: str) -> dict[str, list[str]]:
        """
        Get all dependencies of a tool.
        
        Returns:
            Dict with 'apis' and 'tools' keys
        """
        neo4j = await ToolGraph._get_neo4j()
        if not neo4j:
            return {"apis": [], "tools": []}
        
        try:
            # Get APIs
            api_result = await neo4j.run_query("""
                MATCH (t:Tool {id: $tool_name})-[:USES]->(a:API)
                RETURN a.id as api_name
            """, {"tool_name": tool_name})
            
            # Get tools
            tool_result = await neo4j.run_query("""
                MATCH (t:Tool {id: $tool_name})-[:DEPENDS_ON]->(d:Tool)
                RETURN d.id as dep_name
            """, {"tool_name": tool_name})
            
            return {
                "apis": [r["api_name"] for r in api_result] if api_result else [],
                "tools": [r["dep_name"] for r in tool_result] if tool_result else [],
            }
        except Exception:
            return {"apis": [], "tools": []}
    
    @staticmethod
    async def get_blast_radius(api_name: str) -> dict[str, list[str]]:
        """
        Get full blast radius if an API goes down.
        
        Traverses: API <- USES <- Tool <- DEPENDS_ON <- Tool (recursively)
        
        Returns:
            Dict with 'direct' (tools using API) and 'indirect' (tools depending on those)
        """
        neo4j = await ToolGraph._get_neo4j()
        if not neo4j:
            return {"direct": [], "indirect": []}
        
        try:
            # Direct dependents
            direct = await ToolGraph.get_api_dependents(api_name)
            
            # Indirect dependents (tools that depend on direct tools)
            indirect_result = await neo4j.run_query("""
                MATCH (t:Tool)-[:USES]->(:API {id: $api_name})
                MATCH (dependent:Tool)-[:DEPENDS_ON*1..5]->(t)
                RETURN DISTINCT dependent.id as tool_name
            """, {"api_name": api_name})
            
            indirect = [r["tool_name"] for r in indirect_result] if indirect_result else []
            
            return {
                "direct": direct,
                "indirect": [t for t in indirect if t not in direct],
            }
        except Exception:
            return {"direct": [], "indirect": []}
    
    @staticmethod
    async def detect_circular_dependencies() -> list[list[str]]:
        """
        Detect circular dependencies in tool graph.
        
        Returns:
            List of cycles (each cycle is a list of tool names)
        """
        neo4j = await ToolGraph._get_neo4j()
        if not neo4j:
            return []
        
        try:
            result = await neo4j.run_query("""
                MATCH path = (t:Tool)-[:DEPENDS_ON*2..10]->(t)
                RETURN [node in nodes(path) | node.id] as cycle
                LIMIT 10
            """)
            
            return [r["cycle"] for r in result] if result else []
        except Exception:
            return []
    
    @staticmethod
    async def get_all_tools() -> list[dict[str, Any]]:
        """Get all registered tools."""
        neo4j = await ToolGraph._get_neo4j()
        if not neo4j:
            return []
        
        try:
            result = await neo4j.run_query("""
                MATCH (t:Tool)
                OPTIONAL MATCH (t)-[:USES]->(a:API)
                RETURN t, collect(a.id) as apis
            """)
            
            tools = []
            for r in result or []:
                tool = dict(r["t"])
                tool["apis"] = r["apis"]
                tools.append(tool)
            
            return tools
        except Exception:
            return []
    
    @staticmethod
    async def log_tool_call(
        tool_name: str,
        agent_id: str,
        success: bool,
        duration_ms: int | None = None,
        error: str | None = None,
    ) -> bool:
        """
        Log a tool call event.
        
        Creates:
        - Event node for the tool call
        - Relationships to tool and agent
        
        Enables tracking:
        - Tool usage frequency
        - Error rates per tool
        - Performance metrics
        """
        neo4j = await ToolGraph._get_neo4j()
        if not neo4j:
            return False
        
        try:
            from uuid import uuid4
            
            event_id = f"tool_call:{uuid4()}"
            
            await neo4j.create_event(
                event_id=event_id,
                event_type="tool_call",
                timestamp=datetime.utcnow().isoformat(),
                properties={
                    "tool_name": tool_name,
                    "agent_id": agent_id,
                    "success": success,
                    "duration_ms": duration_ms,
                    "error": error,
                },
            )
            
            # Link to tool
            await neo4j.create_relationship(
                from_type="Event",
                from_id=event_id,
                to_type="Tool",
                to_id=tool_name,
                rel_type="INVOKED",
            )
            
            # Link to agent
            await neo4j.create_relationship(
                from_type="Event",
                from_id=event_id,
                to_type="Agent",
                to_id=agent_id,
                rel_type="BY_AGENT",
            )
            
            return True
        except Exception:
            return False


# =============================================================================
# Pre-defined L9 Tool Definitions
# =============================================================================

L9_TOOLS = [
    ToolDefinition(
        name="web_search",
        description="Search the web using Firecrawl",
        external_apis=["Firecrawl", "Perplexity"],
        category="research",
    ),
    ToolDefinition(
        name="llm_chat",
        description="Chat with OpenAI models",
        external_apis=["OpenAI"],
        category="ai",
    ),
    ToolDefinition(
        name="memory_write",
        description="Write to L9 memory substrate",
        external_apis=["PostgreSQL"],
        category="memory",
    ),
    ToolDefinition(
        name="memory_search",
        description="Search L9 memory with embeddings",
        external_apis=["PostgreSQL", "OpenAI"],
        internal_dependencies=["memory_write"],
        category="memory",
    ),
    ToolDefinition(
        name="slack_send",
        description="Send message to Slack",
        external_apis=["Slack"],
        category="communication",
    ),
    ToolDefinition(
        name="email_send",
        description="Send email",
        external_apis=["SMTP"],
        category="communication",
    ),
    ToolDefinition(
        name="calendar_create",
        description="Create calendar event",
        external_apis=["Google Calendar"],
        category="scheduling",
    ),
]


async def register_l9_tools() -> int:
    """
    Register all L9 tools in the graph.
    
    Call this at startup to populate the tool graph.
    
    Returns:
        Number of tools registered
    """
    count = 0
    for tool in L9_TOOLS:
        if await ToolGraph.register_tool(tool):
            count += 1
    
    logger.info(f"Registered {count}/{len(L9_TOOLS)} tools in Neo4j graph")
    return count


__all__ = [
    "ToolDefinition",
    "ToolGraph",
    "L9_TOOLS",
    "register_l9_tools",
]

