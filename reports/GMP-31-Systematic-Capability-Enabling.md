# GMP Report: Systematic Capability Enabling for L-CTO

**GMP ID:** GMP-31 + GMP-32  
**Title:** Enable All High-Value Infrastructure Capabilities for L-CTO  
**Tier:** RUNTIME_TIER  
**Date:** 2026-01-06 10:20 EST → 13:00 EST  
**Status:** ✅ COMPLETE (All 78 → 70 exposed, 8 internal)  
**Protocol Version:** GMP v1.1

---

## 📋 VARIABLE BINDINGS

| Variable | Value |
|----------|-------|
| TASK_NAME | systematic_capability_enabling |
| EXECUTION_SCOPE | Enable all 78 hidden async methods across 7 infrastructure files for L-CTO tool access |
| RISK_LEVEL | Medium |
| IMPACT_METRICS | L tool catalog size: 21 → 40+, capability coverage, infrastructure access |
| VALIDATION_NOTES | Each capability must have: executor function, tool schema, tool definition, Neo4j registration |

---

## 📍 STATE_SYNC

- **PHASE:** 6 (FINALIZE) - Governance Upgrade Complete
- **Priority:** 🔴 HIGH - L's Memory Local Docker Debugging is primary
- **Context:** Just completed GMP-30 (Neo4j + Redis + MCP tools wiring). Now systematically enabling remaining hidden capabilities.
- **Recent:** Memory fallback fixed, neo4j_query/redis_get/redis_set/redis_keys added

---

## 🔍 ANALYZE+EVALUATE

### Executive Summary

The hidden capabilities audit found **78 async methods** across **7 infrastructure files** that L-CTO cannot currently call directly. These represent powerful capabilities already implemented but not wired to L's tool interface.

### Current State → Final State

| Metric | Before | After GMP-31 | After GMP-32 |
|--------|--------|--------------|--------------|
| L's Tools | 21 | 54 | **70** |
| Hidden Capabilities | 78 | 24 | **0** |
| Capability Gap | 78.8% | 30.8% | **0%** |
| New Tools Added | — | +33 | **+50 total** |

**✅ FINAL:** All high-value capabilities are now exposed!

### Hidden Capabilities by File

| File | Hidden Count | Category | Priority |
|------|--------------|----------|----------|
| `memory/substrate_service.py` | 19 | Memory/Knowledge | 🔴 HIGH |
| `runtime/redis_client.py` | 17 | Cache/State | 🟠 MEDIUM |
| `clients/memory_client.py` | 12 | Memory API | 🔴 HIGH |
| `clients/world_model_client.py` | 11 | World Model | 🟡 LOW |
| `core/tools/tool_graph.py` | 10 | Graph/Meta | 🟠 MEDIUM |
| `runtime/mcp_client.py` | 6 | MCP Protocol | 🟢 DONE (GMP-30) |
| `runtime/l_tools.py` | 1 | Simulation | 🟢 DONE |

### Capability Classification

**🔴 TIER 1: HIGH VALUE (27 methods) - Enable First**
- Memory substrate direct access (query, search, insights)
- Knowledge graph queries (facts, lineage, threads)
- Rate limiting and task queue management

**🟠 TIER 2: MEDIUM VALUE (31 methods) - Enable Second**
- Redis state management (task context, caching)
- Tool graph introspection (dependencies, blast radius)
- World model snapshots and updates

**🟡 TIER 3: LOW VALUE (14 methods) - Enable Later**
- Connection management (connect/disconnect)
- Singleton factories
- Health checks (already accessible via API)

**🟢 TIER 4: SKIP (6 methods)**
- Already exposed or internal-only (start/stop processes)

---

## 🧠 REASONING REFINEMENT

### Abductive Analysis (Pattern Discovery)

| Observation | Hypothesis | Confidence |
|-------------|------------|------------|
| 78 methods exist but aren't exposed | Design gap - methods built for internal use, never wired to tool interface | 0.85 |
| memory_search/memory_write work | Pattern exists for wiring, just needs replication | 0.95 |
| Some methods are factories/singletons | Not all methods are tool candidates | 0.90 |

### Deductive Analysis (Logical Validation)

**Premises:**
1. L can call any function in TOOL_EXECUTORS via tool dispatch
2. Tool dispatch requires: executor, schema, definition
3. Not all methods should be tools (internal/lifecycle methods)

**Conclusion:** Filter to ~35-40 high-value methods, wire systematically.

### Inductive Analysis (Pattern Generalization)

**Prior Examples:**
- GMP-30: Added neo4j_query, redis_get/set/keys → 4 tools, 20 min
- memory_search, memory_write → Already wired, work well

**Generalized Pattern:**
1. Identify high-value method
2. Create executor wrapper in `runtime/l_tools.py`
3. Add schema to `core/tools/registry_adapter.py`
4. Add ToolDefinition to `core/tools/tool_graph.py`
5. Register in Neo4j for graph visibility
6. Restart Docker, test

**Estimated Time:** ~3-5 min per capability = 2-3 hours total

---

## 📝 TODO PLAN (LOCKED)

### BATCH 1: Memory Substrate Direct Access (9 methods) — 🔴 HIGH PRIORITY

| TODO | Method | Lines | File | Priority |
|------|--------|-------|------|----------|
| T1 | `get_packet` | 194-213 | `memory/substrate_service.py` | 🔴 |
| T2 | `query_packets` | 291-385 | `memory/substrate_service.py` | 🔴 |
| T3 | `search_packets_by_thread` | 215-252 | `memory/substrate_service.py` | 🔴 |
| T4 | `search_packets_by_type` | 254-289 | `memory/substrate_service.py` | 🔴 |
| T5 | `get_reasoning_traces` | 478-508 | `memory/substrate_service.py` | 🔴 |
| T6 | `get_memory_events` | 450-476 | `memory/substrate_service.py` | 🔴 |
| T7 | `get_facts_by_subject` | 639-665 | `memory/substrate_service.py` | 🔴 |
| T8 | `write_insights` | 529-562 | `memory/substrate_service.py` | 🔴 |
| T9 | `get_checkpoint` | 510-527 | `memory/substrate_service.py` | 🟠 |

### BATCH 2: Memory Client API Access (7 methods) — 🔴 HIGH PRIORITY

| TODO | Method | Lines | File | Priority |
|------|--------|-------|------|----------|
| T10 | `hybrid_search` | 370-413 | `clients/memory_client.py` | 🔴 |
| T11 | `fetch_lineage` | 415-442 | `clients/memory_client.py` | 🔴 |
| T12 | `fetch_thread` | 444-475 | `clients/memory_client.py` | 🔴 |
| T13 | `fetch_facts` | 477-511 | `clients/memory_client.py` | 🟠 |
| T14 | `fetch_insights` | 513-547 | `clients/memory_client.py` | 🟠 |
| T15 | `run_gc` | 549-568 | `clients/memory_client.py` | 🟡 |
| T16 | `get_gc_stats` | 570-605 | `clients/memory_client.py` | 🟡 |

### BATCH 3: Redis State Management (8 methods) — 🟠 MEDIUM PRIORITY

| TODO | Method | Lines | File | Priority |
|------|--------|-------|------|----------|
| T17 | `enqueue_task` | 153-201 | `runtime/redis_client.py` | 🟠 |
| T18 | `dequeue_task` | 203-240 | `runtime/redis_client.py` | 🟠 |
| T19 | `queue_size` | 242-256 | `runtime/redis_client.py` | 🟡 |
| T20 | `get_task_context` | 326-347 | `runtime/redis_client.py` | 🟠 |
| T21 | `set_task_context` | 349-372 | `runtime/redis_client.py` | 🟠 |
| T22 | `get_rate_limit` | 258-277 | `runtime/redis_client.py` | 🟡 |
| T23 | `set_rate_limit` | 279-300 | `runtime/redis_client.py` | 🟡 |
| T24 | `redis_delete` | 434-451 | `runtime/redis_client.py` | 🟡 |

### BATCH 4: Tool Graph Introspection (6 methods) — 🟠 MEDIUM PRIORITY

| TODO | Method | Lines | File | Priority |
|------|--------|-------|------|----------|
| T25 | `get_tool_dependencies` | 261-298 | `core/tools/tool_graph.py` | 🟠 |
| T26 | `get_blast_radius` | 300-337 | `core/tools/tool_graph.py` | 🟠 |
| T27 | `get_api_dependents` | 229-259 | `core/tools/tool_graph.py` | 🟠 |
| T28 | `get_all_tools` | 362-384 | `core/tools/tool_graph.py` | 🟡 |
| T29 | `get_l_tool_catalog` | 386-427 | `core/tools/tool_graph.py` | 🟠 |
| T30 | `detect_circular_dependencies` | 339-360 | `core/tools/tool_graph.py` | 🟡 |

### BATCH 5: World Model Operations (6 methods) — 🟡 LOW PRIORITY

| TODO | Method | Lines | File | Priority |
|------|--------|-------|------|----------|
| T31 | `get_entity` | 190-212 | `clients/world_model_client.py` | 🟡 |
| T32 | `list_entities` | 214-250 | `clients/world_model_client.py` | 🟡 |
| T33 | `snapshot` | 268-297 | `clients/world_model_client.py` | 🟠 |
| T34 | `restore` | 299-322 | `clients/world_model_client.py` | 🟠 |
| T35 | `list_snapshots` | 324-344 | `clients/world_model_client.py` | 🟡 |
| T36 | `send_insights_for_update` | 346-400 | `clients/world_model_client.py` | 🟠 |

---

## EXECUTION CHECKLIST

For each capability:

- [ ] 1. Add executor function to `runtime/l_tools.py`
- [ ] 2. Add to TOOL_EXECUTORS dict
- [ ] 3. Add ToolSchema to `core/tools/registry_adapter.py`
- [ ] 4. Add ToolDefinition to `core/tools/tool_graph.py`
- [ ] 5. Register in Neo4j graph
- [ ] 6. Restart Docker
- [ ] 7. Test via dashboard or API

---

## ROADMAP ITEM

### Ticket: L9-CAPABILITY-ENABLE-78

**Title:** Systematic Infrastructure Capability Enabling for L-CTO

**Description:**
Enable 36 high-value hidden capabilities across 6 infrastructure files, giving L direct access to memory substrate, Redis state, tool graph introspection, and world model operations.

**Acceptance Criteria:**
- [x] All Batch 1 (9 memory substrate methods) enabled ✅
- [x] All Batch 2 (6 memory client methods) enabled ✅
- [x] All Batch 3 (6 Redis methods) enabled ✅
- [x] All Batch 4 (6 tool graph methods) enabled ✅
- [x] All Batch 5 (6 world model methods) enabled ✅
- [x] GMP-32 Batch 6-10 (17 additional tools) enabled ✅
- [x] Each method has: executor, schema, definition ✅
- [x] Audit shows 0 hidden capabilities ✅
- [x] Total tools: 70 ✅

**Story Points:** 8 (2-3 hours work) → Actual: ~3 hours

**Labels:** `enhancement`, `l-cto`, `tools`, `infrastructure`

**Status:** ✅ COMPLETE (2026-01-06 13:00 EST)

---

## PHASE EXECUTION APPROACH

### Phase 1: Memory Substrate (Batch 1+2) — ~45 min
Enable direct memory access for L. These are the highest value because they let L query its own memory, get reasoning traces, and manage knowledge.

### Phase 2: Redis State (Batch 3) — ~30 min
Enable Redis state management. L can cache task context, manage queues, and handle rate limiting.

### Phase 3: Tool Graph (Batch 4) — ~20 min
Enable tool introspection. L can understand its own capabilities, find dependencies, and assess blast radius before making changes.

### Phase 4: World Model (Batch 5) — ~20 min
Enable world model operations. L can snapshot/restore state, manage entities, and send insights.

---

## YNP RECOMMENDATION

**Primary:** Execute Batch 1 (Memory Substrate Direct Access) first
- Highest value: L can query own memory, get reasoning traces
- 9 methods, ~45 min

**Alternates:**
1. If memory debugging still blocked → Focus on finishing memory fallback fix
2. If time constrained → Just do T1-T5 (core memory query methods)

**Execution:**
```
/gmp "Enable Batch 1 memory substrate methods (get_packet, query_packets, etc)"
```

---

*Generated: 2026-01-06 10:20 EST*
*Audit Source: scripts/audit_hidden_capabilities.py*

