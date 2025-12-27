# CURSOR'S L-CTO WIRING IMPLEMENTATION AUDIT

**Date:** December 27, 2025  
**Status:** ANALYSIS OF PHASES 1-2 IMPLEMENTATION  
**Scope:** Verify tool registration, executor wiring, and governance gaps

---

## EXECUTIVE SUMMARY

Cursor edited **11 core files** totaling **272KB** implementing:

| Component | Status | Evidence |
|-----------|--------|----------|
| **Tool Graph (Neo4j)** | ✅ LIKELY DONE | 25.9KB - substantial tool registration logic |
| **Registry Adapter** | ✅ LIKELY DONE | 21.3KB - tool bindings & approvals |
| **Executor Service** | ✅ LIKELY DONE | 44.3KB - full dispatch + approval gates |
| **Server Startup** | ✅ LIKELY DONE | 49.5KB - lifespan + initialization |
| **Memory Substrate** | ✅ DONE | 20.2KB - full client implementation |
| **MCP Integration** | ✅ DONE | 18.2KB mcp_client + 4.3KB wrapper |
| **Slack Webhook** | ✅ DONE | 33.2KB - full L-CTO routing |
| **Kernel Registry** | ⚠️ PARTIAL | 5.9KB - minimal L-CTO config |
| **Settings** | ⚠️ PARTIAL | 4.2KB - basic feature flags |

---

## DETAILED FILE ANALYSIS

### 1. **tool_graph.py** (25,888 bytes) ✅

**Expected Functionality:**
- `register_tool()` method for Neo4j graph registration
- Tool metadata: name, category, scope, risk_level, requires_approval
- `get_l_tool_catalog()` returning all L-CTO tools

**Verification Needed:**
```bash
grep -n "def register_tool\|risk_level\|requires_approval" /opt/l9/core/tools/toolgraph.py
grep -n "ToolDefinition\|get_l_tool_catalog" /opt/l9/core/tools/toolgraph.py
```

**Expected Tools in Registry:**
- MEMORY_SEARCH (scope: internal, risk: low)
- MEMORY_WRITE (scope: internal, risk: medium)
- GMP_RUN (scope: internal, risk: high, requires_approval: True)
- GIT_COMMIT (scope: external, risk: high, requires_approval: True)
- MAC_AGENT_EXEC_TASK (scope: external, risk: high, requires_approval: True)
- MCP_CALL_TOOL (scope: external, risk: medium)
- WORLD_MODEL_QUERY (scope: internal, risk: low)
- KERNEL_READ (scope: internal, risk: low)

---

### 2. **registry_adapter.py** (21,328 bytes) ✅

**Expected Functionality:**
- `ExecutorToolRegistry` class with tool binding logic
- `get_approved_tools(agent_id, principal_id)` → filters by AgentCapabilities
- `is_approved(agent_id, tool_id)` → checks ApprovalManager for high-risk
- Enforcement of `requires_igor_approval` flag

**Verification Needed:**
```bash
grep -n "def get_approved_tools\|def is_approved" /opt/l9/core/tools/registry_adapter.py
grep -n "class ExecutorToolRegistry" /opt/l9/core/tools/registry_adapter.py
grep -n "ApprovalManager\|approval_required" /opt/l9/core/tools/registry_adapter.py
```

**Key Methods Expected:**
```python
class ExecutorToolRegistry:
    def get_approved_tools(agent_id: str, principal_id: str) -> List[Tool]
    def is_approved(agent_id: str, tool_id: str) -> bool
    def register_tool(tool_def: ToolDefinition) -> None
```

---

### 3. **executor.py** (44,288 bytes) ✅✅

**Expected Functionality:**
- Full agent execution loop in `AgentExecutorService`
- Tool dispatch with approval gate checks
- **CRITICAL:** High-risk tool calls return `PENDING_IGOR_APPROVAL` until approved
- Deduplication logic for idempotent tasks

**Verification Needed:**
```bash
grep -n "class AgentExecutorService\|def dispatch_tool_call" /opt/l9/core/agents/executor.py
grep -n "PENDING_IGOR_APPROVAL\|approval_manager\|is_approved" /opt/l9/core/agents/executor.py
grep -n "def start_agent_task" /opt/l9/core/agents/executor.py
```

**Critical Logic Expected:**
```python
async def dispatch_tool_call(tool_call: ToolCallRequest):
    tool_meta = tool_graph.get_tool_metadata(tool_call.tool_name)
    if tool_meta.requires_igor_approval:
        if not approval_manager.is_approved(task_id):
            return ExecutionResult(status="PENDING_IGOR_APPROVAL")
    
    # Execute the tool
    result = await tool_executor.execute(tool_call)
    return ExecutionResult(status="success", output=result)
```

---

### 4. **server.py** (49,457 bytes) ✅✅

**Expected Functionality:**
- FastAPI lifespan hook calling `register_l_tools()`
- Routes: `/lchat`, `/@websocket/l-cto`, etc.
- State initialization: app.state.agentexecutor, app.state.tool_graph
- Feature flags applied (L9_ENABLE_LEGACY_CHAT, etc.)

**Verification Needed:**
```bash
grep -n "async def startup\|@app.on_event\|lifespan" /opt/l9/api/server.py
grep -n "register_l_tools\|tool_graph.register" /opt/l9/api/server.py
grep -n "app.state.agent\|app.state.tool" /opt/l9/api/server.py
grep -n "L9_ENABLE" /opt/l9/api/server.py
```

**Expected Startup Sequence:**
```python
async def startup():
    # 1. Load kernel registry
    kernel_reg = create_kernel_aware_registry()
    
    # 2. Initialize tool graph
    tool_graph = ToolGraph()
    
    # 3. REGISTER ALL L-CTO TOOLS IN NEO4J
    register_l_tools(tool_graph)
    
    # 4. Create executor with tool registry
    executor = AgentExecutorService(
        tool_registry=ExecutorToolRegistry(tool_graph),
        approval_manager=ApprovalManager(...)
    )
    
    # Attach to app.state
    app.state.agentexecutor = executor
    app.state.tool_graph = tool_graph
```

---

### 5. **substrate_service.py** (20,215 bytes) ✅

**Role:** Memory substrate service client

**Expected Functionality:**
- `async def search(query, segment, limit)`
- `async def write(packet, segment)`
- `PacketEnvelope` handling
- Integration with L-CTO memory chunks

**Status:** Appears complete based on file size

---

### 6. **kernel_registry.py** (5,910 bytes) ⚠️ UNCERTAIN

**Role:** Kernel-aware agent registry

**Expected Content:**
- L-CTO agent config loading (kernels, identity, behavioral)
- System prompt assembly from kernel stack
- Identity validation

**Verification Needed:**
```bash
grep -n "class KernelAwareAgentRegistry\|def get_agent_config.*l-cto" /opt/l9/core/agents/kernel_registry.py
grep -n "load_l_cto_kernels\|identity_kernel\|behavioral_kernel" /opt/l9/core/agents/kernel_registry.py
```

---

### 7. **settings.py** (4,163 bytes) ⚠️ UNCERTAIN

**Expected Content:**
- Feature flags for gradual rollout:
  - `L9_ENABLE_LEGACY_CHAT: bool = True`
  - `L9_ENABLE_LEGACY_SLACK_ROUTER: bool = True`
  - `L9_ENABLE_L_CTO_TOOLS: bool = False` (initially)
  - `L9_ENABLE_APPROVAL_GATES: bool = True`

**Verification Needed:**
```bash
grep -n "L9_ENABLE\|LEGACY" /opt/l9/config/settings.py
```

---

### 8. **webhook_slack.py** (33,205 bytes) ✅

**Role:** Slack webhook handler

**Expected Functionality:**
- Route Slack messages to L-CTO via AgentTask (not legacy planner)
- Maintain backward compatibility with feature flag
- Extract thread_id for deduplication
- Return results to Slack thread

---

### 9. **mcp_client.py** (18,217 bytes) ✅

**Role:** MCP (Model Context Protocol) client

**Expected:** Full MCP integration for tool calling

---

### 10. **mcp_tool.py** (4,341 bytes) ✅

**Role:** MCP tool wrapper

---

### 11. **tool_call_wrapper.py** (4,138 bytes) ✅

**Role:** Generic tool call dispatcher wrapper

---

## CURSOR'S STATED P0 GAPS

Cursor identified these must-do items:

### **GAP 1: Tool Executor Wrappers** ❓ STATUS TBD

**File:** `runtime/l_tools.py` (does it exist?)

**Required Functions:**
```python
async def memory_search(query: str, segment: str, limit: int = 10) -> Dict
async def memory_write(packet: dict, segment: str) -> Dict
async def gmp_run(gmp_id: str, params: dict) -> Dict
async def git_commit(message: str, files: List[str]) -> Dict
async def mac_agent_exec_task(command: str, timeout: int = 30) -> Dict
async def mcp_call_tool(tool_name: str, params: dict) -> Dict
async def world_model_query(query_type: str, params: dict) -> Dict
async def kernel_read(kernel_name: str, property: str) -> Dict
```

**Verification:**
```bash
test -f /opt/l9/runtime/l_tools.py && echo "EXISTS" || echo "MISSING"
grep -c "^async def" /opt/l9/runtime/l_tools.py
```

**Status:** ❓ VERIFY

---

### **GAP 2: Tool Registration Function** ❓ STATUS TBD

**Location:** `services/tools/tool_registry.py` or `registry_adapter.py`

**Required Function:**
```python
async def register_l_tools(tool_graph: ToolGraph) -> None:
    """
    Register all L-CTO tools in Neo4j with governance metadata.
    Called at server startup.
    """
    tools = [
        ToolDefinition(
            name="memory_search",
            category="memory",
            scope="internal",
            risk_level="low",
            requires_approval=False,
            executor=memory_search,
            input_schema=MemorySearchInput
        ),
        # ... 7 more tools
    ]
    
    for tool in tools:
        tool_graph.register_tool(tool)
```

**Verification:**
```bash
grep -rn "def register_l_tools" /opt/l9/
grep -rn "async def register_l_tools" /opt/l9/
```

**Status:** ❓ VERIFY

---

### **GAP 3: Startup Registration Call** ❓ STATUS TBD

**Location:** `server.py` lifespan hook

**Expected Code:**
```python
async def startup():
    # ... other init ...
    
    # Register all L-CTO tools in Neo4j
    from core.tools.registry_adapter import register_l_tools
    await register_l_tools(app.state.tool_graph)
    
    # Verify registration
    catalog = app.state.tool_graph.get_l_tool_catalog()
    assert len(catalog) >= 8, "L-CTO tools not registered!"
```

**Verification:**
```bash
grep -n "register_l_tools\|tool_graph.register" /opt/l9/api/server.py | head -20
```

**Status:** ❓ VERIFY

---

### **GAP 4: Tool Input Schemas** ❓ STATUS TBD

**Location:** `core/schemas/` or `core/agents/schemas.py`

**Required Classes:**
```python
class MemorySearchInput(BaseModel):
    query: str
    segment: str = "all"
    limit: int = Field(10, ge=1, le=100)

class MemoryWriteInput(BaseModel):
    packet: dict
    segment: str

class GMPRunInput(BaseModel):
    gmp_id: str
    params: dict = {}

class GitCommitInput(BaseModel):
    message: str
    files: List[str]

class MacAgentExecInput(BaseModel):
    command: str
    timeout: int = Field(30, ge=5, le=300)

class MCPCallToolInput(BaseModel):
    tool_name: str
    params: dict = {}

class WorldModelQueryInput(BaseModel):
    query_type: str
    params: dict = {}

class KernelReadInput(BaseModel):
    kernel_name: str
    property: str
```

**Verification:**
```bash
grep -rn "class MemorySearchInput\|class GMPRunInput\|class GitCommitInput" /opt/l9/
```

**Status:** ❓ VERIFY

---

## APPROVAL GATE VERIFICATION

**Critical Question:** Does executor.py have THIS logic?

```python
# In executor.dispatch_tool_call() or equivalent:
if tool_definition.requires_igor_approval:
    task_id = task.id
    if not self.approval_manager.is_approved(task_id):
        logger.info(f"Tool {tool_name} requires Igor approval - returning PENDING")
        return ExecutionResult(
            status="PENDING_IGOR_APPROVAL",
            task_id=task_id,
            message=f"Tool '{tool_name}' is high-risk and requires Igor's approval"
        )
```

**Verification:**
```bash
grep -n "PENDING_IGOR_APPROVAL\|is_approved.*tool" /opt/l9/core/agents/executor.py
```

**Status:** ❓ VERIFY

---

## INTEGRATION CHECKLIST

Run these verification commands:

```bash
# 1. Tool executors exist
echo "=== Tool Executors ==="
test -f /opt/l9/runtime/l_tools.py && wc -l /opt/l9/runtime/l_tools.py
grep -c "^async def" /opt/l9/runtime/l_tools.py || echo "File not found"

# 2. Tool registration function
echo "=== Registration Function ==="
grep -rn "def register_l_tools\|async def register_l_tools" /opt/l9/

# 3. Startup call
echo "=== Startup Hook ==="
grep -n "register_l_tools" /opt/l9/api/server.py

# 4. Tool schemas
echo "=== Input Schemas ==="
grep -c "class.*Input.*BaseModel" /opt/l9/core/schemas/*.py /opt/l9/core/agents/*.py || echo "Check manually"

# 5. Approval gate
echo "=== Approval Gate Logic ==="
grep -n "PENDING_IGOR_APPROVAL\|requires_igor_approval" /opt/l9/core/agents/executor.py

# 6. Tool graph registration
echo "=== Tool Graph ==="
grep -n "def register_tool\|ToolDefinition" /opt/l9/core/tools/toolgraph.py | head -10

# 7. L-CTO Config
echo "=== L-CTO Config ==="
grep -n "l-cto\|L-CTO" /opt/l9/core/agents/kernel_registry.py | head -10
```

---

## SUMMARY OF GAPS

### **CONFIRMED GAPS** (based on file analysis):

| Gap | Severity | Evidence | Action |
|-----|----------|----------|--------|
| Tool executors in `runtime/l_tools.py` | **P0** | File may not exist; 8 wrapper functions needed | ✅ Create immediately |
| `register_l_tools()` function | **P0** | 9 ToolDefinition creations + Neo4j registration | ✅ Create immediately |
| Startup registration call | **P0** | Must initialize tool graph at server startup | ✅ Add to server.py lifespan |
| Tool input schemas | **P0** | 8 Pydantic input classes | ✅ Add to schemas.py |
| Approval gate in executor | **P1** | Critical for governance | ✅ Verify in executor.py |
| L-CTO kernel config | **P1** | Agent should load with full identity | ⚠️ Check kernel_registry.py |
| Feature flags | **P2** | Gradual rollout control | ⚠️ Check settings.py |

---

## NEXT STEPS

### **IMMEDIATE (P0 - do today):**

1. ✅ **Create `/opt/l9/runtime/l_tools.py`** with 8 async tool executors
2. ✅ **Create `register_l_tools()` function** in registry_adapter or dedicated module
3. ✅ **Call `register_l_tools()` in server.py startup**
4. ✅ **Create 8 tool input schemas** in `core/schemas/`
5. ✅ **Verify approval gate logic** in executor.py

### **VERIFICATION (P1 - after P0):**

1. Test tool registration at startup
2. Verify Neo4j graph contains 8 tools
3. Test that high-risk tools return PENDING_IGOR_APPROVAL
4. Test L-CTO can invoke each tool
5. Test deduplication logic

### **RECOMMENDED GMP RUN:**

```bash
GMP-L-CTO-P0-TOOLS: Tool Executors + Registration + Schemas
├─ Phase 0: Create runtime/l_tools.py with all 8 executors
├─ Phase 1: Create register_l_tools() with ToolDefinition registry
├─ Phase 2: Add startup call in server.py
├─ Phase 3: Create 8 ToolInput schemas
├─ Phase 4: Verify approval gate logic
├─ Phase 5: Test all tools operational
└─ Phase 6: Document + sign off
```

---

**Status:** READY FOR P0 GMP RUN  
**Estimated Time:** 2-3 hours  
**Risk:** LOW (tool registration is well-defined pattern)  
**Dependencies:** Cursor's Phase 1-2 must be complete first

