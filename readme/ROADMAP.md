# L9 Development Roadmap

## Completed ✅

### Stage 1: Basic Wiring & Interfaces
- [x] Memory Substrate schema and repository
- [x] Semantic search with pgvector
- [x] World Model engine and state
- [x] WebSocket agent protocol
- [x] PacketEnvelope schema

### Stage 2: Memory + World Model Integration
- [x] Slack ingest → thread context retrieval
- [x] Slack ingest → semantic memory hits
- [x] Insights → World Model orchestrator propagation
- [x] `MemorySubstrateService.trigger_world_model_update()`

### Stage 3: Autonomous Execution
- [x] Mac Agent shell executor (with LocalAPI whitelist)
- [x] Mac Agent browser executor (Playwright automation)
- [x] Mac Agent Python executor (Docker sandbox with subprocess fallback)

---

### Stage 4: LLM-Powered Artifact Generation
- [x] `generate_artifact_with_llm()` function for plans, code, docs
- [x] `draft_work_node` now generates real artifacts via GPT-4
- [x] Context-aware generation (governance rules, project history)
- [x] Auto-detect when code/docs artifacts are needed

---

### Stage 2.5: Memory API & Client SDK (2025-01-27)
- [x] Fixed memory router path: `/memory` → `/api/v1/memory` (matches client SDK expectations)
- [x] Added 8 missing API route handlers in `api/memory/router.py`:
  - `GET /api/v1/memory/packet/{id}` - Get packet by ID
  - `GET /api/v1/memory/thread/{id}` - Get thread packets
  - `GET /api/v1/memory/lineage/{id}` - Get packet lineage
  - `POST /api/v1/memory/hybrid/search` - Hybrid search (semantic + filters)
  - `GET /api/v1/memory/facts` - Query knowledge facts
  - `GET /api/v1/memory/insights` - Query insights
  - `POST /api/v1/memory/gc/run` - Run garbage collection
  - `GET /api/v1/memory/gc/stats` - Get GC statistics
- [x] All 9 MemoryClient SDK methods now have corresponding API endpoints
- [x] Integration tests: 12/12 passing (all new endpoints verified)
- [x] Client SDK tests: Added comprehensive test for all 9 methods
- [x] Created gap analysis documentation (`docs/API_GAP_ANALYSIS.md`)
- [x] Created orchestrator wiring status documentation (`docs/ORCHESTRATOR_WIRING_STATUS.md`)

---

## In Progress 🔄

### Stage 2.7: PacketEnvelope v2.0 Schema Migration
> **Sunset Deadline: 2026-04-05**

**Status:** Schema v2.0.0 is canonical, SchemaRegistry auto-upcasts at runtime. 72 files still import from deprecated modules.

- [x] **Phase 1: Schema Consolidation (Complete)**
  - [x] Created `core/schemas/packet_envelope_v2.py` (v2.0.0 canonical)
  - [x] Added `SchemaRegistry` with chained upcasting (v1.0.0 → v2.0.0)
  - [x] Immutability enforcement (`frozen=True`)
  - [x] Content hash integrity (`compute_content_hash()`, `verify_integrity()`)
  - [x] DAG lineage tracking (`PacketLineage`)
  - [x] Deprecation warnings on import of old modules

- [x] **Phase 2: CI Gate (Complete)**
  - [x] Created `ci/check_schema_deprecation.py`
  - [x] Phase-based enforcement (warnings → errors → block)
  - [x] Excluded tests/docs/archive from gate

- [ ] **Phase 3: Import Migration (~25 active files)**
  - [ ] Migrate `core/agents/executor.py`
  - [ ] Migrate `core/governance/*.py` (3 files)
  - [ ] Migrate `core/compliance/audit_log.py`
  - [ ] Migrate `memory/*.py` (5 files)
  - [ ] Migrate `orchestration/*.py` (3 files)
  - [ ] Migrate `api/*.py` (4 files)
  - [ ] Migrate `services/*.py` (2 files)
  - [ ] Run full test suite

- [ ] **Phase 4: Upgrade Engine Activation**
  - [ ] Activate phases 2-5 via `/api/v1/upgrades/packet-envelope/activate/all`
  - [ ] Add lifespan auto-activation (optional, for persistence across restarts)
  - [ ] Verify Jaeger + Prometheus integration

**Sunset Timeline:**
| Date | Phase | Effect |
|------|-------|--------|
| 2026-01-05 | Phase 1 | Warnings only (current) |
| 2026-02-20 | Phase 2 | Errors in new files |
| 2026-03-22 | Phase 3 | Errors for all |
| 2026-04-05 | Phase 4 | Complete block |

**Files:**
- Canonical schema: `core/schemas/packet_envelope_v2.py`
- Registry: `core/schemas/schema_registry.py`
- CI gate: `ci/check_schema_deprecation.py`
- Upgrade engine: `l9/upgrades/packet_envelope/`

---

### Stage 3.5: Proactive World Model Updates
- [x] `MemorySubstrateService.query_packets()` for world model polling
- [x] `MemorySubstratePacketSource` implementation
- [x] `create_runtime_with_substrate()` factory function
- [ ] Integration with API server startup
- [ ] Background task for `runtime.run_forever()`

---

### Stage 2.6: Orchestrator API Wiring (HIGH PRIORITY) 🚨
- [ ] **Phase 1: ActionTool Orchestrator**
  - [ ] Add optional import check for `ActionToolOrchestrator` in `api/server.py`
  - [ ] Instantiate `ActionToolOrchestrator` in `lifespan()` startup
  - [ ] Store in `app.state.action_tool_orchestrator`
  - [ ] Mount `api/tools/router.py` at `/tools` prefix
  - [ ] Test `/tools/test` and `/tools/execute` endpoints

- [ ] **Phase 2: Reasoning Orchestrator**
  - [ ] Add optional import check for `ReasoningOrchestrator` in `api/server.py`
  - [ ] Instantiate `ReasoningOrchestrator` in `lifespan()` startup
  - [ ] Store in `app.state.reasoning_orchestrator`
  - [ ] Mount `api/routes/reasoning.py` at `/reasoning` prefix
  - [ ] Test `/reasoning/execute` endpoint

- [ ] **Phase 3: ResearchSwarm Orchestrator**
  - [ ] Add optional import check for `ResearchSwarmOrchestrator` in `api/server.py`
  - [ ] Complete stub implementation in `orchestrators/research_swarm/orchestrator.py`
  - [ ] Instantiate `ResearchSwarmOrchestrator` in `lifespan()` startup
  - [ ] Store in `app.state.research_swarm_orchestrator`
  - [ ] Mount `api/routes/research.py` at `/research/swarm` prefix (or consolidate with existing `/research`)
  - [ ] Test `/research/swarm/execute` endpoint

**Dependencies:**
- Stage 2.6 blocks: None (can start immediately)
- Stage 2.6 enables: Tool execution API, reasoning orchestration API, research swarm API

**Notes:**
- All three orchestrators exist as code but are **not wired** (not instantiated, not mounted)
- See `docs/API_GAP_ANALYSIS.md` and `docs/ORCHESTRATOR_WIRING_STATUS.md` for details
- ActionTool and Reasoning are fully implemented; ResearchSwarm is stub

---

## Planned 📋

### Stage 7: L-CTO Agent Integration (HIGHEST PRIORITY) 🚨
- [ ] **Phase 1: Memory Migration**
  - [x] Archive deprecated Supabase clients (`l-cto/l_memory/memory_client.py`, `kg_client.py`)
  - [ ] Remove Supabase dependencies from `l-cto/memory/` routers
  - [ ] Migrate `MemoryRouterV4` to use `MemorySubstrateService` instead of Supabase
  - [ ] Replace custom L1/MAC/META table routing with `PacketEnvelope` + `agent_id` filtering
  - [ ] Delete deprecated `l-cto/l_memory/` directory (already archived)

- [ ] **Phase 2: Agent Architecture Refactor**
  - [ ] **CRITICAL**: Refactor `LMission` + `LEngine` into separate, granular layers
  - [ ] Extract reasoning engine as shared component (not L-CTO-specific)
  - [ ] Extract governance checks as shared component (not L-CTO-specific)
  - [ ] Make L-CTO use `agents/l_cto.py` (BaseAgent) + shared reasoning/governance layers
  - [ ] Ensure all agents can plug into shared reasoning engines (architectural requirement)

- [ ] **Phase 3: Multi-Agent Memory Infrastructure**
  - [ ] Verify `PacketEnvelope.metadata.agent` supports multi-agent filtering
  - [ ] Add agent_id constants: `l-cto`, `l9`, `cursor`, `emma`
  - [ ] Ensure memory queries filter by `agent_id` for isolation
  - [ ] Test cross-agent memory access patterns (shared vs private)

- [ ] **Phase 4: L-CTO Integration Points**
  - [ ] Wire `agents/l_cto.py` into `AgentExecutorService` (task routing)
  - [ ] Add FastAPI route `/api/agents/l-cto/directive` (direct HTTP access)
  - [ ] Register L-CTO in `AgentRegistry` with `agent_id="l-cto"`
  - [ ] Test both integration points (executor + HTTP route)

- [ ] **Phase 5: Slack Integration for L-CTO**
  - [ ] Wire L-CTO into Slack webhook routing (similar to existing Slack → L9 flow)
  - [ ] Ensure L-CTO can receive DMs and channel messages
  - [ ] Add placeholder for Emma Slack integration (future)

- [ ] **Phase 6: Naming Standardization**
  - [ ] Run rename script: `python scripts/rename_l_to_l_cto.py` (dry-run completed)
  - [ ] Rename all code references: "l" → "l-cto" (agent_id, class names, imports)
  - [ ] Keep "L" as display name in user-facing messages only
  - [ ] Update all YAML configs, kernel files, docs to use "l-cto" in code
  - [ ] Consider renaming `l-cto/` directory to `l_cto/` for Python import compatibility

**Dependencies:**
- Stage 7 blocks: None (can start immediately)
- Stage 7 enables: Multi-agent orchestration, Emma agent integration, advanced agent coordination

**Notes:**
- L-CTO integration is **HIGHEST PRIORITY**
- Architecture principle: Granular, pluggable agents with shared reasoning engines (NOT monolithic LMission/LEngine)
- Memory principle: Shared infrastructure with `agent_id` filtering (NOT per-agent databases)
- Emma agent: Spec outside repo, add placeholders where prudent
- Supabase: Fully deprecated - use `MemorySubstrateService` + `PacketEnvelope` only

---

### Stage 4: LLM-Powered Artifact Generation
- [ ] `long_plan_graph.py` → LLM code generation in planning nodes
- [ ] `long_plan_graph.py` → LLM documentation generation
- [ ] Artifact storage and versioning
- [ ] Plan → Executable workflow conversion

### Stage 5: Research Swarm
- [ ] `orchestrators/research_swarm/orchestrator.py` → Implement orchestration logic (currently stub)
- [ ] `orchestrators/research_swarm/convergence.py` → Implement convergence/specialized logic
- [ ] Wire ResearchSwarmOrchestrator into API (see Stage 2.6 Phase 3)

### Stage 6: Persistence & Reliability
- [ ] World Model snapshots persisted to storage
- [ ] World Model restore from snapshot
- [ ] Checkpoint-based recovery
- [ ] Event sourcing for state reconstruction

---

---

### Stage 2.8: MCP Memory Scope Enforcement (2026-01-06) ✅

**Status:** In Progress (5/8 tasks done, local Docker test + VPS deploy pending)

| Question | Answer |
|----------|--------|
| Is `L9_TENANT_ID=l-cto` hardcoded? | No, it defaults to `l-cto` but reads from env |
| Is `l9-shared` used? | Yes, both L and C share it for MCP memory |
| Does scope restrict Cursor? | ❌ **NOT YET** — spec exists, code doesn't enforce it |
| Can L hide memories from Cursor? | ❌ **NOT YET** — would need `scope='l-private'` filtering |

**Design:**
- L and Cursor share `user_id = l9-shared` (intentional - L is Cursor's superior)
- L can see ALL memories Cursor creates
- L can add knowledge that Cursor benefits from (shared learning)
- L can write `l-private` scope memories that Cursor CANNOT see

**Scope Values:**
| Scope | L Access | Cursor Access |
|-------|----------|---------------|
| `user` | ✅ READ/WRITE | ✅ READ/WRITE |
| `project` | ✅ READ/WRITE | ✅ READ/WRITE |
| `global` | ✅ READ/WRITE | ✅ READ/WRITE |
| `l-private` | ✅ READ/WRITE | ❌ BLOCKED |

- [x] Add `l-private` to allowed scope values in MCP tool schema
- [x] Enforce scope filtering in `search_memory_handler()` based on caller
- [x] Enforce scope filtering in `get_context_injection()` based on caller
- [x] Enforce scope filtering in `get_proactive_suggestions()` based on caller
- [x] Block Cursor from writing `l-private` scope
- [ ] Test on local Docker (must pass before VPS deploy)
- [ ] Deploy to VPS
- [ ] Add tests for scope isolation

---

---

### Stage 2.9: Systematic Capability Enabling (GMP-31) 🔄

**Status:** In Progress (Planning Complete, Execution Pending)
**Story Points:** 8 (2-3 hours work)
**Priority:** P1 (after L's memory debugging complete)

**Goal:** Enable 36 high-value hidden capabilities across 6 infrastructure files, giving L direct access to memory substrate, Redis state, tool graph introspection, and world model operations.

**Capability Audit Results:**
| Metric | Value |
|--------|-------|
| L's Current Tools | 21 |
| Hidden Capabilities | 78 |
| High-Value (to enable) | 36 |
| Files Affected | 6 |

**Batches:**

| Batch | Category | Methods | Priority | Est. Time |
|-------|----------|---------|----------|-----------|
| 1 | Memory Substrate Direct | 9 | 🔴 HIGH | 45 min |
| 2 | Memory Client API | 7 | 🔴 HIGH | 25 min |
| 3 | Redis State Management | 8 | 🟠 MEDIUM | 30 min |
| 4 | Tool Graph Introspection | 6 | 🟠 MEDIUM | 20 min |
| 5 | World Model Operations | 6 | 🟡 LOW | 20 min |

**Key Methods per Batch:**

- **Batch 1 (Memory Substrate):** `get_packet`, `query_packets`, `get_reasoning_traces`, `get_facts_by_subject`, `write_insights`
- **Batch 2 (Memory Client):** `hybrid_search`, `fetch_lineage`, `fetch_thread`, `fetch_facts`
- **Batch 3 (Redis):** `enqueue_task`, `dequeue_task`, `get_task_context`, `set_task_context`
- **Batch 4 (Tool Graph):** `get_tool_dependencies`, `get_blast_radius`, `get_l_tool_catalog`
- **Batch 5 (World Model):** `snapshot`, `restore`, `send_insights_for_update`

**Files to Modify:**

| File | Add Executors | Add Schemas | Add Definitions |
|------|---------------|-------------|-----------------|
| `runtime/l_tools.py` | 36 functions | - | - |
| `core/tools/registry_adapter.py` | - | 36 schemas | 36 definitions |
| `core/tools/tool_graph.py` | - | - | 36 L_INTERNAL_TOOLS |

**Acceptance Criteria:**
- [ ] All Batch 1-5 methods enabled (36 total)
- [ ] Each method has: executor, schema, definition, Neo4j node
- [ ] All tests pass
- [ ] L can call each new tool from dashboard

**Report:** `reports/GMP-31-Systematic-Capability-Enabling.md`
**Audit Script:** `scripts/audit_hidden_capabilities.py`

---

## Future (Deferred) 🔮

### Self-Evolution Capabilities
> ⚠️ **DEFERRED** - Requires careful security review and governance framework.

The following capabilities are intentionally deferred until proper safety mechanisms are in place:

- **Code self-modification**: Evolution engine reading/writing its own source code
- **Autonomous refactoring**: L9 proposing and applying changes to itself
- **Capability expansion**: L9 adding new tools/executors without human approval

**Prerequisites before implementation:**
1. Comprehensive governance framework
2. Human-in-the-loop approval workflow
3. Rollback mechanisms with full audit trail
4. Sandboxed testing environment for self-modifications
5. Rate limiting on self-modification operations
6. External monitoring and kill switch

**Related stubs (not to be implemented without approval):**
- `orchestrators/evolution/apply_engine.py` → `_read_file()`, `_write_file()`
- Any code that would allow L9 to modify files in its own repository

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.3.0 | 2026-01-05 | Added Stage 2.7 (PacketEnvelope v2.0 Schema Migration) with sunset timeline |
| 0.2.0 | 2025-01-27 | Added Stage 2.5 (Memory API & Client SDK completion), Stage 2.6 (Orchestrator API Wiring), gap analysis docs |
| 0.1.0 | 2025-12-26 | Initial roadmap created |

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | REA-OPER-010 |
| **Component Name** | Roadmap |
| **Module Version** | 1.0.0 |
| **Created At** | 2026-01-08T03:17:26Z |
| **Created By** | L9_DORA_Injector |
| **Layer** | operations |
| **Domain** | readme |
| **Type** | schema |
| **Status** | active |
| **Governance Level** | medium |
| **Compliance Required** | True |
| **Audit Trail** | True |
| **Purpose** | Documentation for ROADMAP |

---
