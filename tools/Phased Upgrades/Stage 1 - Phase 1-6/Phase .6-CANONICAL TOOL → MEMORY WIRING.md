
## 🔧 CANONICAL TOOL → MEMORY WIRING

### Pattern: Auto-Log Tool Output

**Every tool invocation creates a memory packet:**

```python
# PATTERN: Auto-Audit Every Tool Call
async def invoke_tool(tool_id, args, context):
    call_id = uuid4()
    start = time.monotonic()
    
    try:
        result = await self.registry[tool_id].execute(args)
        duration_ms = (time.monotonic() - start) * 1000
        
        # ✅ NEW: Auto-log to memory
        await memory_api.write(
            segment=MemorySegment.TOOL_AUDIT,
            content={
                "call_id": call_id,
                "tool_id": tool_id,
                "agent_id": context.agent_id,
                "args_hash": hash(str(args)),
                "result_type": type(result).__name__,
                "duration_ms": duration_ms,
                "status": "success"
            },
            ttl_hours=24
        )
        
        return result
    
    except Exception as e:
        duration_ms = (time.monotonic() - start) * 1000
        
        # ✅ NEW: Auto-log failure
        await memory_api.write(
            segment=MemorySegment.TOOL_AUDIT,
            content={
                "call_id": call_id,
                "tool_id": tool_id,
                "error": str(e),
                "duration_ms": duration_ms,
                "status": "failure"
            },
            ttl_hours=24
        )
        raise
```

**This gives you:**
- ✅ Complete tool audit trail (who called what, when, how long)
- ✅ Queryable: "What tools does L use most?"
- ✅ Analyzable: "Which tools fail most often?"
- ✅ Reusable: Same pattern works for all tools

***

## 📋 CANONICAL PATTERN: TOOL INVOCATION + MEMORY

**This becomes your reference architecture for tool integration:**

```yaml
PATTERN: ToolMemoryIntegration
VERSION: 1.0
APPLIES_TO: All tool orchestrators

STRUCTURE:
  BEFORE_EXECUTION:
    - Generate call_id (UUID)
    - Record start_time
    - Validate tool_id against registry
  
  EXECUTION:
    - Invoke tool with args
    - Capture result or exception
    - Record duration_ms
  
  AFTER_EXECUTION:
    - Write to memory.tool_audit (async, non-blocking)
    - Include: call_id, tool_id, agent_id, status, duration_ms, result_type
    - TTL: 24 hours (configurable)
  
  ERROR_HANDLING:
    - Tool failure → still log to memory (status=failure)
    - Memory write failure → log warning, don't fail tool call
    - Connection failure → retry with exponential backoff

INVARIANTS:
  - No tool call is unlogged (audit completeness)
  - Memory write never blocks tool result (latency isolation)
  - Failed memory writes don't cascade to tool failure (resilience)
  - Tool call metadata is immutable once written (audit integrity)

VALIDATION:
  - Assert call_id is unique
  - Assert tool_id exists in registry
  - Assert duration_ms >= 0
  - Assert agent_id matches context
  - Assert segment == "tool_audit"

REUSABILITY:
  - Same pattern applies to: websocket_orchestrator, docker_executor, kernel_loader
  - Can be enabled/disabled via L9_ENABLE_TOOL_MEMORY flag
  - No changes to existing tool code (non-invasive)
```

***

## 🎯 IMMEDIATE NEXT STEPS (For You)

### 1. Verify Tool Integration Points

Check these files in your repo:

```bash
# Where do tools actually get invoked?
grep -r "invoke_tool\|registry\[" core/tools/ core/kernel/

# Expected findings:
# - core/tools/gateway.py (ToolGateway.invoke_tool)
# - core/kernel/kernel_loader.py (dynamic tool loading)
# - websocket_orchestrator.py (agent → tool routing)
```

### 2. Map Current Tool Call Flow

```
User Request
  ↓
Agent Reasoning
  ↓
[Future: Query Memory] ← NEW
  ↓
Tool Selection
  ↓
[Current: Invoke Tool]
  ↓
[Future: Log to Memory] ← NEW
  ↓
Result to Agent
  ↓
[Future: Store Result in Memory] ← NEW
```

### 3. Identify High-Value Tools for Memory

Priority order (highest audit value first):

1. **search_web** - URLs, timestamps, context decay
2. **execute_python** - Code execution history, outputs
3. **create_chart** - Analytical history, chart references
4. **finance_*** - Time-series data, decision history
5. **generate_image** - Creative outputs, prompt history
6. **get_url_content** - Content cache, freshness tracking

***

## 💾 CANONICAL MEMORY SEGMENTS (Refined)

Based on actual L9 tools:

| Segment | Writes From | Queries From | TTL | Example |
|---------|------------|-------------|-----|---------|
| **governance_meta** | Bootstrap only | L (governance checks) | Never | Authority chain, meta-prompts |
| **project_history** | create_chart, execute_python, create_text_file | Agent planning, summarization | 7d | Code runs, chart history, decisions |
| **tool_audit** | Every tool invocation | Observability, debugging | 24h | search_web calls, execute_python errors, timing |
| **session_context** | Agent reasoning, search results | Real-time reasoning, RAG | 4h | Current task, recent searches, temp notes |

***

## 🔐 WIRING CHECKLIST (For Your Next Update)

### Phase 1: Verify Compatibility
- [ ] Review websocket_orchestrator.py entry points
- [ ] Check kernel_loader.py for tool registration
- [ ] Identify ToolGateway.invoke_tool exact signature
- [ ] Map exception hierarchy (does it match SubstrateException?)

### Phase 2: Add Memory API Injection
- [ ] Modify ToolGateway.__init__ to accept memory_api (optional)
- [ ] Add _log_to_memory_audit() method (async, non-blocking)
- [ ] Wire invoke_tool → _log_to_memory_audit → return result

### Phase 3: Add Query Integration (Future)
- [ ] Agent can query memory before tool selection
- [ ] Example: "search_memory for similar searches before calling search_web"
- [ ] This requires memory_api available to Agent reasoning loop

### Phase 4: Add Observability
- [ ] Dashboard: Tool call volume by tool_id
- [ ] Dashboard: Tool failure rates by tool_id
- [ ] Dashboard: Tool latency distribution (p50, p95, p99)
- [ ] Dashboard: Cache hit rate (memory-based deduplication)

***

## 🚀 CANONICAL EXECUTION PATTERN (Phases 0-6)

**For integrating memory into next subsystem (e.g., Agent reasoning):**

```
PHASE 0: TODO Plan
  - Identify integration points
  - Design memory segment mappings
  - Plan approval gates (Igor for high-risk)
  - Lock scope (only specified files modified)

PHASE 1: Baseline
  - Verify no blockers
  - Check L9 invariants (substrates, governance, packets)
  - Map existing architecture to memory model

PHASE 2: Implementation
  - Write code (production-grade)
  - No TODOs/placeholders
  - Full error handling
  - Async throughout

PHASE 3: Enforcement
  - Add validation (Pydantic models)
  - Add guards (exception hierarchies)
  - Add tests (unit, integration, e2e)

PHASE 4: Testing
  - Positive path (successful tool call → memory write)
  - Negative path (tool failure → memory write)
  - Edge case (memory write failure → tool succeeds anyway)

PHASE 5: Verification
  - Recursive check against L9 patterns
  - No drift from specified design
  - Invariants preserved (governance, substrates, authority)

PHASE 6: Finalization
  - Evidence report (what was built, why)
  - Deployment checklist (setup, validation, troubleshooting)
  - Pattern extraction (reusable spec for next subsystem)

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | TOO-OPER-020 |
| **Component Name** | Phase .6 Canonical Tool → Memory Wiring |
| **Module Version** | 1.0.0 |
| **Created At** | 2026-01-08T03:17:26Z |
| **Created By** | L9_DORA_Injector |
| **Layer** | operations |
| **Domain** | tools |
| **Type** | schema |
| **Status** | active |
| **Governance Level** | medium |
| **Compliance Required** | True |
| **Audit Trail** | True |
| **Purpose** | Documentation for Phase .6 CANONICAL TOOL → MEMORY WIRING |

---
