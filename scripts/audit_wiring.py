# /l9/scripts/audit_wiring.py
"""Runtime wiring audit - checks what's actually initialized"""
import sys
import os
import structlog

logger = structlog.get_logger(__name__)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

async def audit_wiring():
    logger.info("=== L9 WIRING AUDIT ===\n")
    
    # 1. Check memory substrate
    try:
        from memory.substrate_service import MemorySubstrateService
        logger.info("✓ MemorySubstrateService import works")
        # Try to instantiate (may fail if DB not connected)
        try:
            substrate = MemorySubstrateService()
            logger.info("✓ MemorySubstrateService instantiation works")
        except Exception as e:
            logger.info(f"✗ MemorySubstrateService instantiation failed: {e}")
    except ImportError as e:
        logger.info(f"✗ MemorySubstrateService import failed: {e}")
    
    # 2. Check Neo4j driver
    try:
        from neo4j import GraphDatabase
        logger.info("✓ Neo4j driver library available")
        
        # Check if driver is configured
        neo4j_uri = os.getenv("NEO4J_URI", "NOT_SET")
        logger.info(f"  NEO4J_URI: {neo4j_uri}")
    except ImportError:
        logger.info("✗ Neo4j driver library not installed")
    
    # 3. Check AgentGraphLoader
    try:
        from core.agents.graph_state.agent_graph_loader import AgentGraphLoader
        logger.info("✓ AgentGraphLoader import works")
    except ImportError as e:
        logger.info(f"✗ AgentGraphLoader import failed: {e}")
    
    # 4. Check tool registry
    try:
        from core.tools.registry_adapter import get_tool_registry_adapter
        registry = get_tool_registry_adapter()
        tools = registry.list_tools()
        logger.info(f"✓ ToolRegistry accessible, {len(tools)} tools registered")
        logger.info(f"  Tools: {', '.join(t['id'] for t in tools[:5])}...")
    except Exception as e:
        logger.info(f"✗ ToolRegistry check failed: {e}")
    
    # 5. Check feature flags
    flags = {
        "L9_GRAPH_AGENT_STATE": os.getenv("L9_GRAPH_AGENT_STATE", "NOT_SET"),
        "L9_ENABLE_MEMORY": os.getenv("L9_ENABLE_MEMORY", "NOT_SET"),
        "L9_ENABLE_GRAPH": os.getenv("L9_ENABLE_GRAPH", "NOT_SET"),
    }
    logger.info("\n=== FEATURE FLAGS ===")
    for flag, value in flags.items():
        logger.info(f"  {flag}: {value}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(audit_wiring())
