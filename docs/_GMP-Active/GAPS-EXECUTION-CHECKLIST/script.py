# noqa: print-forbidden
# Analyze C's edits - read and summarize each file
import re

files_to_analyze = {
    "tool_graph.py": "file:46",
    "registry_adapter.py": "file:47", 
    "mcp_tool.py": "file:48",
    "mcp_client.py": "file:49",
    "substrate_service.py": "file:50",
    "kernel_registry.py": "file:51",
    "executor.py": "file:52",
    "webhook_slack.py": "file:53",
    "tool_call_wrapper.py": "file:54",
    "server.py": "file:55",
    "settings.py": "file:56"
}

# Summary dict
summary = {}

# Key patterns to search for
patterns = {
    "tool_registration": r"(register_tool|ToolName\.|register_l_tools)",
    "memory_search": r"(memory_search|MEMORY_SEARCH|semantic_search)",
    "memory_write": r"(memory_write|MEMORY_WRITE)",
    "approval": r"(approval|ApprovalManager|requires_igor)",
    "l_tools": r"(l_tools|L_TOOLS|LTools)",
    "neo4j": r"(neo4j|Neo4j|graph_db)",
    "startup": r"(startup|lifespan|on_startup|init)",
    "schema": r"(ToolInput|ToolSchema|parameters)",
    "gmp": r"(GMP|gmp_run|GMPRUN)",
    "mac_agent": r"(MAC_AGENT|mac_agent|MacAgent)",
    "git": r"(GIT_COMMIT|git_commit|GitCommit)",
}

print("="*80)
print("CURSOR EDITS ANALYSIS - FILE BY FILE")
print("="*80)

# Read files from attachment metadata
analysis = {
    "tool_graph.py": {
        "size": 25888,
        "key_items": []
    },
    "registry_adapter.py": {
        "size": 21328,
        "key_items": []
    },
    "executor.py": {
        "size": 44288,
        "key_items": []
    },
    "server.py": {
        "size": 49457,
        "key_items": []
    },
    "kernel_registry.py": {
        "size": 5910,
        "key_items": []
    },
    "settings.py": {
        "size": 4163,
        "key_items": []
    },
    "substrate_service.py": {
        "size": 20215,
        "key_items": []
    },
    "mcp_client.py": {
        "size": 18217,
        "key_items": []
    },
    "mcp_tool.py": {
        "size": 4341,
        "key_items": []
    },
    "tool_call_wrapper.py": {
        "size": 4138,
        "key_items": []
    },
    "webhook_slack.py": {
        "size": 33205,
        "key_items": []
    }
}

for filename, size in [
    ("tool_graph.py", 25888),
    ("registry_adapter.py", 21328),
    ("executor.py", 44288),
    ("server.py", 49457),
    ("kernel_registry.py", 5910),
    ("settings.py", 4163),
]:
    print(f"\n{'='*80}")
    print(f"FILE: {filename} ({size} bytes)")
    print(f"{'='*80}")
    if filename == "tool_graph.py":
        print("✓ ROLE: Neo4j tool graph - manages tool definitions & bindings")
        print("  - Likely has: register_tool(), get_l_tool_catalog()")
        print("  - Should have: Tool metadata (scope, risk_level, requires_approval)")
    elif filename == "registry_adapter.py":
        print("✓ ROLE: Tool registry adapter - maps tools to executors")
        print("  - Likely has: get_approved_tools(), register_tool()")
        print("  - Should have: L-CTO tool bindings")
    elif filename == "executor.py":
        print("✓ ROLE: Agent executor service - runs tasks")
        print("  - ~44KB suggests: Full execution loop, tool dispatch")
        print("  - Should have: Tool invocation, approval gate checks")
    elif filename == "server.py":
        print("✓ ROLE: FastAPI app - routes, startup")
        print("  - ~49KB suggests: Full server setup, lifespan hooks")
        print("  - Should have: register_l_tools() call in startup")
    elif filename == "kernel_registry.py":
        print("✓ ROLE: Kernel-aware agent registry")
        print("  - Should have: L-CTO agent config loading")
    elif filename == "settings.py":
        print("✓ ROLE: Configuration")
        print("  - Should have: Feature flags (L9_ENABLE_*)")

print("\n" + "="*80)
print("CURSOR'S STATED P0 GAPS TO CLOSE")
print("="*80)
print("""
1. Creating tool executor wrappers in runtime/l_tools.py
   - Status: ???
   - Need: MEMORY_SEARCH, MEMORY_WRITE, GMP_RUN, GIT_COMMIT, MAC_AGENT, MCP_CALL

2. Modifying services/research/tools/tool_registry.py to register L's tools
   - Status: ???
   - Need: register_l_tools() function

3. Adding startup call to register_l_tools() for Neo4j graph
   - Status: ???
   - Need: In server.py lifespan/startup

4. Adding input schemas for all L tools
   - Status: ???
   - Need: ToolInput classes for each tool
""")
