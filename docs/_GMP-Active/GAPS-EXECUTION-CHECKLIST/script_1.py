
# I'll read the file contents to analyze what's been done
import re

file_content = """
We need to examine:
1. tool_graph.py - check for register_tool() signature and tool metadata
2. registry_adapter.py - check for L-CTO tool bindings
3. executor.py - check for tool dispatch and approval gates
4. server.py - check for startup calls
5. kernel_registry.py - check for L-CTO config loading
6. settings.py - check for feature flags

Let me trace through the key implementation signatures...
"""

# Based on the sizes and description, let me create a checklist
gaps_checklist = {
    "P0_TOOL_EXECUTORS": {
        "description": "Tool executor wrappers in runtime/l_tools.py",
        "expected_tools": [
            "memory_search(query, segment, limit)",
            "memory_write(packet, segment)",
            "gmp_run(gmp_id, params)",
            "git_commit(message, files)",
            "mac_agent_exec(command, timeout)",
            "mcp_call_tool(tool_name, params)",
            "world_model_query(query_type)",
            "kernel_read(kernel_name, property)"
        ],
        "status": "UNKNOWN"
    },
    "P1_TOOL_REGISTRATION": {
        "description": "register_l_tools() in services/tools/tool_registry.py",
        "expected_functions": [
            "register_l_tools(tool_graph: ToolGraph)",
            "Creates ToolDefinition for each tool",
            "Sets governance metadata (scope, risk_level, requires_approval)",
            "Stores in Neo4j"
        ],
        "status": "UNKNOWN"
    },
    "P2_STARTUP_HOOK": {
        "description": "register_l_tools() called in server.py startup",
        "expected_code": [
            "@app.on_event('startup') or lifespan context",
            "register_l_tools(tool_graph)",
            "Verify tools registered before accepting requests"
        ],
        "status": "UNKNOWN"
    },
    "P3_TOOL_SCHEMAS": {
        "description": "Input schemas for all tools (ToolInput classes)",
        "expected_schemas": {
            "memory_search": "query: str, segment: str, limit: int = 10",
            "memory_write": "packet: dict, segment: str",
            "gmp_run": "gmp_id: str, params: dict",
            "git_commit": "message: str, files: List[str]",
            "mac_agent": "command: str, timeout: int = 30",
            "mcp_call": "tool_name: str, params: dict",
            "world_model_query": "query_type: str, params: dict",
            "kernel_read": "kernel_name: str, property: str",
        },
        "status": "UNKNOWN"
    },
    "P4_APPROVAL_GATES": {
        "description": "High-risk tools marked with requires_approval=True",
        "high_risk_tools": [
            "GMP_RUN (risk=high)",
            "GIT_COMMIT (risk=high)",
            "MAC_AGENT_EXEC_TASK (risk=high)",
            "MEMORY_WRITE (risk=medium)",
        ],
        "status": "UNKNOWN"
    },
    "P5_EXECUTOR_DISPATCH": {
        "description": "executor.py dispatches tool calls + checks approval gates",
        "expected_logic": [
            "get_approved_tools(agent_id, principal_id)",
            "for high_risk: check approval_manager.is_approved(task_id)",
            "if not approved: return PENDING_IGOR_APPROVAL",
            "else: execute tool"
        ],
        "status": "UNKNOWN"
    },
    "P6_TOOL_BINDINGS": {
        "description": "L-CTO has all tools bound in AgentCapabilities",
        "expected_tools_bound": [
            "MEMORY_SEARCH", "MEMORY_WRITE",
            "GMP_RUN", "GIT_COMMIT",
            "MAC_AGENT_EXEC_TASK",
            "MCP_CALL_TOOL",
            "WORLD_MODEL_QUERY"
        ],
        "status": "UNKNOWN"
    }
}

print("="*80)
print("L-CTO TOOL WIRING - COMPREHENSIVE GAP ANALYSIS")
print("="*80)
print()

for phase_id, phase in sorted(gaps_checklist.items()):
    print(f"\n{phase_id}")
    print(f"  Description: {phase['description']}")
    print(f"  Status: {phase['status']}")
    print(f"  Items to verify:")
    
    for key in phase:
        if key not in ["description", "status"]:
            items = phase[key]
            if isinstance(items, list):
                for item in items[:3]:  # Show first 3
                    print(f"    ✓ {item}")
                if len(items) > 3:
                    print(f"    ... and {len(items)-3} more")
            elif isinstance(items, dict):
                for k, v in list(items.items())[:3]:
                    print(f"    ✓ {k}: {v}")
                if len(items) > 3:
                    print(f"    ... and {len(items)-3} more")

print("\n" + "="*80)
print("NEXT STEP: Analyze actual file contents to confirm status")
print("="*80)
