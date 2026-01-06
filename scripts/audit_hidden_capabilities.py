#!/usr/bin/env python3
"""
L9 Hidden Capabilities Auditor
==============================

Finds async methods in infrastructure files that aren't exposed to L.

Usage:
    python scripts/audit_hidden_capabilities.py

Updated: 2026-01-06 - Excludes internal/lifecycle methods
"""

import re
import os
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)

# Key infrastructure files to audit
INFRA_FILES = [
    "runtime/mcp_client.py",
    "runtime/redis_client.py",
    "runtime/l_tools.py",
    "memory/substrate_service.py",
    "core/tools/tool_graph.py",
    "clients/memory_client.py",
    "clients/world_model_client.py",
]

# Internal/lifecycle methods - NOT tool candidates
# These are infrastructure plumbing, not capabilities for L
EXCLUDED_METHODS = {
    # Connection lifecycle
    "connect", "disconnect", "close", "start", "stop",
    # Singleton factories
    "get_service", "init_service", "close_service",
    "get_redis_client", "close_redis_client",
    "get_memory_client", "close_memory_client",
    "get_world_model_client", "close_world_model_client",
    "get_mcp_client", "close_mcp_client",
    "create_substrate_service",
    # Internal protocol/wiring
    "send_request", "set_session_scope",
    "ensure_agent_exists", "log_tool_call",
    # Registration (internal wiring, not runtime tools)
    "register_tool", "register_tool_with_metadata",
    "register_l9_tools", "register_l_tools",
    # Already exposed under prefixed tool names (redis_*, memory_*, etc.)
    # Redis methods → exposed as redis_*
    "get", "set", "delete", "keys",
    "enqueue_task", "dequeue_task", "queue_size",
    "get_rate_limit", "set_rate_limit", 
    "increment_rate_limit", "decrement_rate_limit",
    "get_task_context", "set_task_context",
    # Memory substrate → exposed as memory_*
    "get_packet", "query_packets", "write_packet",
    "search_packets_by_thread", "search_packets_by_type",
    "semantic_search", "embed_text", "hybrid_search",
    "get_memory_events", "get_reasoning_traces", "get_checkpoint",
    "write_insights", "trigger_world_model_update",
    "get_facts_by_subject", "health_check",
    "fetch_lineage", "fetch_thread", "fetch_facts", "fetch_insights",
    "run_gc", "get_gc_stats",
    # Tool graph → exposed as tools_*
    "get_api_dependents", "get_tool_dependencies", "get_blast_radius",
    "detect_circular_dependencies", "get_all_tools", "get_l_tool_catalog",
    # World model → exposed as world_model_*
    "get_entity", "list_entities", "get_state_version",
    "snapshot", "restore", "list_snapshots",
    "send_insights_for_update", "list_updates",
    # MCP → exposed as mcp_*
    "list_tools", "call_tool", "stop_all_servers",
    # Simulation → exposed as simulation
    "simulation_execute",
}

# Get L's exposed tools from TOOL_EXECUTORS
def get_exposed_tools(root: Path) -> set[str]:
    """Extract tool names from TOOL_EXECUTORS dict."""
    l_tools = root / "runtime/l_tools.py"
    content = l_tools.read_text()
    
    # Find TOOL_EXECUTORS section
    match = re.search(r'TOOL_EXECUTORS[^{]*\{([^}]+)\}', content, re.DOTALL)
    if not match:
        return set()
    
    # Extract quoted tool names
    tools = re.findall(r'"([^"]+)":', match.group(1))
    return set(tools)


def get_async_methods(filepath: Path) -> list[tuple[str, int, str]]:
    """Extract async method definitions from a file."""
    if not filepath.exists():
        return []
    
    content = filepath.read_text()
    methods = []
    
    for i, line in enumerate(content.split('\n'), 1):
        # Match: async def method_name(
        match = re.match(r'\s*async def ([a-z_][a-z0-9_]*)\(', line)
        if match and not match.group(1).startswith('_'):
            # Get docstring if exists
            doc = ""
            idx = content.find(line)
            docstart = content.find('"""', idx + len(line))
            if docstart != -1 and docstart < idx + 500:
                docend = content.find('"""', docstart + 3)
                if docend != -1:
                    doc = content[docstart+3:docend].strip().split('\n')[0]
            methods.append((match.group(1), i, doc[:60]))
    
    return methods


def main():
    root = Path(__file__).parent.parent
    
    exposed = get_exposed_tools(root)
    logger.info(f"\n{'='*60}")
    logger.info(f"L9 HIDDEN CAPABILITIES AUDIT")
    logger.info(f"{'='*60}")
    logger.info(f"\nExposed tools to L: {len(exposed)}")
    
    for tool in sorted(exposed):
        logger.info(f"  ✓ {tool}")
    
    logger.info(f"\n{'='*60}")
    logger.info("HIDDEN CAPABILITIES BY FILE")
    logger.info(f"{'='*60}")
    
    total_hidden = 0
    
    for rel_path in INFRA_FILES:
        filepath = root / rel_path
        methods = get_async_methods(filepath)
        
        if not methods:
            continue
        
        # Filter to methods not in exposed tools and not excluded
        hidden = [(m, ln, doc) for m, ln, doc in methods 
                  if m not in exposed 
                  and m not in EXCLUDED_METHODS
                  and not m.startswith('_')]
        
        if hidden:
            logger.info(f"\n📁 {rel_path}")
            logger.info("-" * 50)
            for method, line, doc in hidden:
                total_hidden += 1
                doc_preview = f" → {doc}" if doc else ""
                logger.info(f"  Line {line:4d}: {method}(){doc_preview}")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"  Exposed tools:      {len(exposed)}")
    logger.info(f"  Excluded internal:  {len(EXCLUDED_METHODS)}")
    logger.info(f"  Hidden (actionable): {total_hidden}")
    
    if total_hidden == 0:
        logger.info("\n✅ All high-value capabilities are exposed!")
    else:
        logger.info("\nRecommendations:")
        logger.info("  1. Review each hidden method for L exposure value")
        logger.info("  2. Add high-value methods to runtime/l_tools.py TOOL_EXECUTORS")
        logger.info("  3. Register in core/tools/tool_graph.py L_INTERNAL_TOOLS")
        logger.info("  4. Add schemas to core/tools/registry_adapter.py")


if __name__ == "__main__":
    main()

