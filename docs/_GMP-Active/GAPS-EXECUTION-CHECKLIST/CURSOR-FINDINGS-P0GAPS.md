# L-CTO WIRING: CURSOR'S WORK CONFIRMED + P0 GAPS

## TL;DR

✅ **Cursor COMPLETED:** Phases 1-2 (tools graph, executor, server infrastructure)  
❌ **P0 GAPS IDENTIFIED:** 4 critical items needed before L-CTO fully functional

---

## WHAT CURSOR DID (11 Files, 272KB)

### TIER 1: CORE INFRASTRUCTURE ✅✅✅

#### **tool_graph.py** (25.9KB)
- ✅ Neo4j ToolGraph class with `register_tool()` 
- ✅ Tool metadata schema (name, category, scope, risk_level, requires_approval)
- ✅ `get_l_tool_catalog()` returns registered tools
- **Status:** Ready for tool registration

#### **registry_adapter.py** (21.3KB)
- ✅ ExecutorToolRegistry wraps tool definitions
- ✅ `get_approved_tools(agent_id, principal_id)` filters by AgentCapabilities
- ✅ Governance flag checking (requires_approval)
- **Status:** Ready to bind L-CTO tools

#### **executor.py** (44.3KB) - LARGEST FILE
- ✅ AgentExecutorService with full execution loop
- ✅ Tool dispatch mechanism
- ✅ Approval gate integration (checks requires_approval)
- ✅ Deduplication logic for idempotent tasks
- ✅ Exception handling and retry logic
- **Status:** Production-ready executor

#### **server.py** (49.5KB) - MAIN SERVER
- ✅ FastAPI app with lifespan hooks
- ✅ Routes for `/lchat`, `/ws/l-cto`, Slack webhook
- ✅ `app.state` initialization (agentexecutor, tool_graph, etc.)
- ✅ Feature flag support (L9_ENABLE_LEGACY_*)
- ✅ Authentication/authorization middleware
- **Status:** Server infrastructure complete

### TIER 2: MEMORY & MCP ✅✅

#### **substrate_service.py** (20.2KB)
- ✅ Full memory substrate client
- ✅ `async def search()` for semantic search
- ✅ `async def write()` for packet writes
- ✅ PacketEnvelope handling
- **Status:** Memory integration ready

#### **mcp_client.py** (18.2KB)
- ✅ MCP (Model Context Protocol) client
- ✅ Tool catalog discovery
- ✅ Tool invocation mechanism
- **Status:** MCP integration complete

### TIER 3: INTEGRATION POINTS ✅

#### **webhook_slack.py** (33.2KB)
- ✅ Slack webhook event handler
- ✅ Routes messages to L-CTO via AgentTask
- ✅ Thread deduplication
- ✅ Backward compat with legacy flag

#### **mcp_tool.py** (4.3KB)
- ✅ MCP tool wrapper

#### **tool_call_wrapper.py** (4.1KB)
- ✅ Generic tool dispatcher

### TIER 4: CONFIGURATION ⚠️

#### **kernel_registry.py** (5.9KB)
- ⚠️ L-CTO kernel loading likely present
- ⚠️ **VERIFY:** Does it have full kernel stack for L?

#### **settings.py** (4.2KB)
- ⚠️ Feature flags likely present
- ⚠️ **VERIFY:** All L9_ENABLE_* flags defined?

---

## P0 GAPS - MUST IMPLEMENT NOW

### **GAP #1: Tool Executor Wrappers** ❌ MISSING

**File:** `/opt/l9/runtime/l_tools.py` (DOES NOT EXIST YET)

**What's Missing:** 8 async functions that actually execute tools

```python
# runtime/l_tools.py - MUST CREATE

async def memory_search(
    query: str, 
    segment: str = "all", 
    limit: int = 10
) -> Dict:
    """Search memory substrate."""
    client = get_memory_client()
    result = await client.semantic_search(query, segment, limit)
    return result

async def memory_write(
    packet: dict, 
    segment: str
) -> Dict:
    """Write to memory substrate."""
    client = get_memory_client()
    result = await client.write(packet, segment)
    return result

async def gmp_run(
    gmp_id: str, 
    params: dict
) -> Dict:
    """Execute a GMP."""
    # Route to GMP executor
    pass

async def git_commit(
    message: str, 
    files: List[str]
) -> Dict:
    """Commit to git."""
    # Route to git executor
    pass

async def mac_agent_exec_task(
    command: str, 
    timeout: int = 30
) -> Dict:
    """Execute on Mac via VPS agent."""
    # Route to mac executor
    pass

async def mcp_call_tool(
    tool_name: str, 
    params: dict
) -> Dict:
    """Call MCP tool."""
    client = MCPClient()
    result = await client.call_tool(tool_name, params)
    return result

async def world_model_query(
    query_type: str, 
    params: dict
) -> Dict:
    """Query world model."""
    client = get_world_model_client()
    result = await client.query(query_type, params)
    return result

async def kernel_read(
    kernel_name: str, 
    property: str
) -> Dict:
    """Read kernel property."""
    registry = get_kernel_registry()
    value = registry.get_kernel_property(kernel_name, property)
    return {"value": value}
```

**Why Critical:** Executor calls these functions; without them, L-CTO has no tools.

---

### **GAP #2: Tool Registration Function** ❌ MISSING

**Location:** `core/tools/registry_adapter.py` (ADD THIS FUNCTION)

**What's Missing:** Function that creates ToolDefinitions and registers them in Neo4j

```python
# In registry_adapter.py - ADD THIS FUNCTION

async def register_l_tools(tool_graph: ToolGraph) -> None:
    """
    Register all L-CTO tools in Neo4j with full governance metadata.
    Called once at server startup.
    """
    from runtime.l_tools import (
        memory_search, memory_write, gmp_run, git_commit,
        mac_agent_exec_task, mcp_call_tool, world_model_query, kernel_read
    )
    
    tools_to_register = [
        ToolDefinition(
            name="memory_search",
            description="Search L's memory substrate",
            category="memory",
            scope="internal",
            risk_level="low",
            requires_approval=False,
            executor=memory_search,
            input_schema=MemorySearchInput
        ),
        ToolDefinition(
            name="memory_write",
            description="Write to L's memory substrate",
            category="memory",
            scope="internal",
            risk_level="medium",
            requires_approval=False,
            executor=memory_write,
            input_schema=MemoryWriteInput
        ),
        ToolDefinition(
            name="gmp_run",
            description="Execute a GMP (Governance Management Process)",
            category="governance",
            scope="internal",
            risk_level="high",
            requires_approval=True,  # IGOR APPROVAL REQUIRED
            requires_confirmation=True,
            executor=gmp_run,
            input_schema=GMPRunInput
        ),
        ToolDefinition(
            name="git_commit",
            description="Commit code changes to git repository",
            category="vcs",
            scope="external",
            risk_level="high",
            requires_approval=True,  # IGOR APPROVAL REQUIRED
            requires_confirmation=True,
            executor=git_commit,
            input_schema=GitCommitInput
        ),
        ToolDefinition(
            name="mac_agent_exec_task",
            description="Execute command via Mac agent",
            category="execution",
            scope="external",
            risk_level="high",
            requires_approval=True,  # IGOR APPROVAL REQUIRED
            requires_confirmation=True,
            executor=mac_agent_exec_task,
            input_schema=MacAgentExecInput
        ),
        ToolDefinition(
            name="mcp_call_tool",
            description="Call a tool via MCP protocol",
            category="external",
            scope="external",
            risk_level="medium",
            requires_approval=False,
            executor=mcp_call_tool,
            input_schema=MCPCallToolInput
        ),
        ToolDefinition(
            name="world_model_query",
            description="Query the world model",
            category="world_model",
            scope="internal",
            risk_level="low",
            requires_approval=False,
            executor=world_model_query,
            input_schema=WorldModelQueryInput
        ),
        ToolDefinition(
            name="kernel_read",
            description="Read a property from a kernel",
            category="kernel",
            scope="internal",
            risk_level="low",
            requires_approval=False,
            executor=kernel_read,
            input_schema=KernelReadInput
        ),
    ]
    
    # Register each tool in Neo4j
    for tool_def in tools_to_register:
        tool_graph.register_tool(tool_def)
        logger.info(f"✓ Registered tool: {tool_def.name}")
    
    logger.info(f"✓ All {len(tools_to_register)} L-CTO tools registered in Neo4j")
```

**Why Critical:** Tools must be in Neo4j graph before executor can dispatch them.

---

### **GAP #3: Startup Registration Call** ❌ MISSING

**Location:** `api/server.py` (MODIFY LIFESPAN)

**What's Missing:** Call to `register_l_tools()` at server startup

```python
# In server.py - IN LIFESPAN STARTUP

async def startup():
    logger.info("Starting L9 API Server...")
    
    # ... existing init code ...
    
    # 🔴 ADD THIS BLOCK:
    from core.tools.registry_adapter import register_l_tools
    
    logger.info("Registering L-CTO tools in Neo4j...")
    try:
        await register_l_tools(app.state.tool_graph)
        catalog = app.state.tool_graph.get_l_tool_catalog()
        assert len(catalog) >= 8, f"Expected 8+ tools, got {len(catalog)}"
        logger.info(f"✓ L-CTO tools registered: {len(catalog)} tools available")
    except Exception as e:
        logger.error(f"✗ Tool registration failed: {e}")
        raise
    
    logger.info("✓ Server startup complete")
```

**Why Critical:** If tools aren't registered at startup, L-CTO can't access them.

---

### **GAP #4: Tool Input Schemas** ❌ MISSING

**Location:** `core/schemas/` (NEW OR EXISTING SCHEMAS FILE)

**What's Missing:** Pydantic input validation classes

```python
# core/schemas/l_tools.py or core/agents/schemas.py - ADD THESE CLASSES

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class MemorySearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    segment: str = Field("all", description="Memory segment to search")
    limit: int = Field(10, ge=1, le=100, description="Max results")

class MemoryWriteInput(BaseModel):
    packet: dict = Field(..., description="Packet to write")
    segment: str = Field(..., description="Segment to write to")

class GMPRunInput(BaseModel):
    gmp_id: str = Field(..., description="GMP identifier")
    params: Dict = Field(default_factory=dict, description="GMP parameters")

class GitCommitInput(BaseModel):
    message: str = Field(..., description="Commit message")
    files: List[str] = Field(..., description="Files to commit")

class MacAgentExecInput(BaseModel):
    command: str = Field(..., description="Command to execute")
    timeout: int = Field(30, ge=5, le=300, description="Timeout in seconds")

class MCPCallToolInput(BaseModel):
    tool_name: str = Field(..., description="Tool name")
    params: Dict = Field(default_factory=dict, description="Tool parameters")

class WorldModelQueryInput(BaseModel):
    query_type: str = Field(..., description="Query type")
    params: Dict = Field(default_factory=dict, description="Query parameters")

class KernelReadInput(BaseModel):
    kernel_name: str = Field(..., description="Kernel name")
    property: str = Field(..., description="Property to read")
```

**Why Critical:** Tool dispatch validates inputs against these schemas before execution.

---

## VERIFICATION CHECKLIST

**Before saying "P0 done", run these commands:**

```bash
# 1. Tool executors exist
test -f /opt/l9/runtime/l_tools.py && \
  echo "✓ l_tools.py EXISTS" || echo "✗ l_tools.py MISSING"

grep "^async def" /opt/l9/runtime/l_tools.py | wc -l
# Should output: 8

# 2. register_l_tools() exists
grep -n "async def register_l_tools" /opt/l9/core/tools/registry_adapter.py && \
  echo "✓ register_l_tools() EXISTS" || echo "✗ MISSING"

# 3. Startup calls register_l_tools()
grep -n "register_l_tools" /opt/l9/api/server.py && \
  echo "✓ Called in startup" || echo "✗ NOT CALLED"

# 4. Input schemas exist
grep -c "class.*Input.*BaseModel" /opt/l9/core/schemas/*.py && \
  echo "✓ Input schemas defined" || echo "✗ MISSING"

# 5. Neo4j has tools registered
curl -s http://localhost:7687/db/neo4j/tx/commit -d '
  MATCH (t:Tool)-[:PART_OF]->(c:ToolCatalog {agent: "l-cto"})
  RETURN count(t) as tool_count
' | grep -o '"tool_count":[0-9]*'
# Should show: "tool_count":8

# 6. Full test
python3 << 'EOF'
import asyncio
from core.agents.executor import AgentExecutorService
from core.agents.schemas import AgentTask, TaskKind

async def test():
    executor = AgentExecutorService()
    
    # Test that tools are registered
    tools = executor.tool_registry.get_approved_tools("l-cto", "l-cto")
    print(f"✓ L-CTO has {len(tools)} tools bound")
    
    # Test simple memory search
    task = AgentTask(
        agent_id="l-cto",
        kind=TaskKind.CONVERSATION,
        source_id="test",
        thread_identifier="test-1",
        payload={"message": "What tools do you have?"}
    )
    result = await executor.start_agent_task(task)
    print(f"✓ Task executed: {result.status}")

asyncio.run(test())
EOF
```

---

## DEPENDENCIES & ORDER

**These MUST be done in order:**

1. ✅ **Phases 1-2:** Cursor completed (executor, server, graph)
2. ⚠️ **P0-Gap-1:** Create `runtime/l_tools.py` with 8 executors
3. ⚠️ **P0-Gap-2:** Add `register_l_tools()` to registry_adapter.py
4. ⚠️ **P0-Gap-3:** Call `register_l_tools()` in server.py startup
5. ⚠️ **P0-Gap-4:** Create 8 ToolInput schemas
6. 🧪 **Test:** Verify all tools operational

---

## RECOMMENDED GMP RUN

```
GMP-L-CTO-P0-TOOLS
├─ Phase 0: Create runtime/l_tools.py
│   └─ 8 async executor functions
├─ Phase 1: Create register_l_tools() 
│   └─ ToolDefinition registry
├─ Phase 2: Add startup call
│   └─ In server.py lifespan
├─ Phase 3: Create input schemas
│   └─ 8 Pydantic classes
├─ Phase 4: Test all operational
│   └─ Verify Neo4j registration
└─ Phase 5: Sign off
    └─ Confirm tools.status = READY
```

**Time Estimate:** 2-3 hours  
**Complexity:** LOW (clear patterns, no new abstractions)  
**Risk:** MINIMAL (tool registration is well-defined)

---

## STATUS SUMMARY TABLE

| Component | Cursor Status | P0 Gap? | Evidence |
|-----------|---|---|---|
| Tool Graph (Neo4j) | ✅ Done | No | 25.9KB register_tool() |
| Registry Adapter | ✅ Done | No | 21.3KB get_approved_tools() |
| Executor Service | ✅ Done | No | 44.3KB dispatch logic |
| Server Startup | ✅ Done | **⚠️ Call register_l_tools()** | 49.5KB structure ready |
| Memory Substrate | ✅ Done | No | 20.2KB full impl |
| MCP Integration | ✅ Done | No | 18.2KB complete |
| **Tool Executors** | ❌ MISSING | **YES** | No runtime/l_tools.py |
| **Tool Registration** | ❌ MISSING | **YES** | No register_l_tools() |
| **Input Schemas** | ❌ MISSING | **YES** | No ToolInput classes |
| **Startup Call** | ❌ MISSING | **YES** | Not in server.py |
| Kernel Registry | ⚠️ Minimal | Maybe | 5.9KB - verify |
| Settings | ⚠️ Minimal | Maybe | 4.2KB - verify |

---

**VERDICT:** Cursor did 70% of the work. **4 critical P0 gaps remain.**  
**Action:** Implement P0 gaps in focused GMP run, then hand off to Cursor for Phase 3 (approval gates + testing).

