
# Create a comprehensive audit of what Cursor implemented and what's missing
# Using the file sizes as indicators of what was likely added

audit_report = """
CURSOR'S L-CTO WIRING IMPLEMENTATION AUDIT
============================================

Based on file sizes and typical implementation patterns:

FILE SIZE ANALYSIS:
- tool_graph.py: 25,888 bytes (substantial - likely has tool registration)
- registry_adapter.py: 21,328 bytes (substantial - likely has bindings)
- executor.py: 44,288 bytes (LARGE - full execution + approval logic)
- server.py: 49,457 bytes (LARGE - full startup + routes)
- substrate_service.py: 20,215 bytes (moderate - memory substrate)
- mcp_client.py: 18,217 bytes (moderate - MCP integration)
- webhook_slack.py: 33,205 bytes (LARGE - full webhook + routing)
- kernel_registry.py: 5,910 bytes (small - minimal agent loading)
- settings.py: 4,163 bytes (small - basic config)
- mcp_tool.py: 4,341 bytes (small - wrapper)
- tool_call_wrapper.py: 4,138 bytes (small - wrapper)

HYPOTHESIS BASED ON SIZES:
✓ LIKELY DONE: 
  - Tool graph implementation with register_tool()
  - Registry adapter with tool bindings
  - Executor with full dispatch logic
  - Server startup logic
  - Memory substrate client
  - MCP client integration
  - Slack webhook updates

? UNCERTAIN:
  - Whether tool executors are in separate l_tools.py or inline
  - Whether approval gate logic is complete
  - Whether all input schemas are defined
  - Whether Neo4j registration happens at startup

GAPS TO VERIFY:
1. Check if runtime/l_tools.py exists with all 8 tools
2. Check if register_l_tools() function exists anywhere
3. Check if server.py calls register_l_tools() in startup
4. Check if all ToolInput schemas are defined
5. Check if approval gate is implemented in executor
6. Check if tool metadata has governance flags
"""

print(audit_report)

# Now let me search for key patterns in file content
key_searches = {
    "Tool executor wrappers": {
        "pattern": r"def (memory_search|memory_write|gmp_run|git_commit|mac_agent)",
        "files": ["runtime/l_tools.py", "tools/", "executor.py"]
    },
    "Tool registration function": {
        "pattern": r"def register_l_tools|register_tool\(",
        "files": ["tool_registry.py", "registry_adapter.py", "tool_graph.py"]
    },
    "Startup hook": {
        "pattern": r"@app.on_event|async def startup|lifespan",
        "files": ["server.py"]
    },
    "Approval gate check": {
        "pattern": r"approval_manager|is_approved|PENDING_IGOR|requires_igor",
        "files": ["executor.py"]
    },
    "Tool input schemas": {
        "pattern": r"class.*Input|ToolInput|tool_schema",
        "files": ["schemas.py", "executor.py", "tool_graph.py"]
    }
}

print("\nKEY PATTERNS TO SEARCH:")
print("="*80)
for search_name, search_def in key_searches.items():
    print(f"\n{search_name}")
    print(f"  Pattern: {search_def['pattern']}")
    print(f"  Files to check: {', '.join(search_def['files'])}")

print("\n" + "="*80)
print("RECOMMENDATION:")
print("="*80)
print("""
To confirm what Cursor has done:

1. Grep for function signatures:
   grep -r "def memory_search\\|def gmp_run\\|def register_l_tools" /opt/l9/
   
2. Check executor.py for approval logic:
   grep -n "approval_manager\\|is_approved\\|PENDING" /opt/l9/core/agents/executor.py
   
3. Check server.py for startup:
   grep -n "register_l_tools\\|@app.on_event\\|lifespan" /opt/l9/api/server.py
   
4. Check tool definitions:
   grep -r "ToolName\\.MEMORY_SEARCH\\|ToolName\\.GMP_RUN" /opt/l9/
   
5. Check kernel registry for L-CTO:
   grep -n "l-cto\\|L-CTO" /opt/l9/core/agents/kernel_registry.py

Once you run these greps, we can confirm:
  ✅ What IS implemented
  ❌ What NEEDS implementation (P0 gaps)
""")
