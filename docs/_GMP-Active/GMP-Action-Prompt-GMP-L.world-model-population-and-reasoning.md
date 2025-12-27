---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

## **GMP-6: GMP-L.world-model-population-and-reasoning**

You are C. You are not designing the world model from scratch. You are populating it with L9 operational entities (agents, repos, infrastructure, tools, external systems) and enabling L to query it for reasoning about system state.

### OBJECTIVE (LOCKED)

Ensure that:
1. World model contains entities: agents (L, CA, QA, Mac), repos (L9, configs), infrastructure (Postgres, Redis, Caddy), external systems (GitHub, Slack, MCP servers).
2. Entities have relationships: "L has_tools(memory, gmp, git, …)", "gmprun requires_approval(Igor)", "toolaudit written_to(segment)", etc.
3. Insights track state changes: "L9 repo pushed to GitHub", "approval rule changed", "memory segment schema updated".
4. L can query world model: "What are my current capabilities?", "What was the last change to the approval rules?", "List all active integration points."
5. World model powers L's decision-making and audit reports.

### SCOPE (LOCKED)

You MAY modify:
- `core/worldmodel/runtime.py` or `core/worldmodel/client.py` – extend entity creation/update logic.
- New file: `core/worldmodel/l9_schema.py` – define L9-specific entity types and relationships.
- `core/agents/executor.py` – after significant events (tool execution, approval, memory write), emit insights.
- New file: `core/worldmodel/insight_emitter.py` – convert events to world model insights.
- `api/server.py` – add endpoint for querying world model.
- New file: `tests/integration/test_world_model.py` – validation.

You MAY NOT:
- Modify world model core (only add L9-specific schemas and event producers).
- Change reasoning logic (only provide more context to L).

### TODO LIST (BY ID)

**T1 – L9 entity types schema**
- File: `core/worldmodel/l9_schema.py` (new)
- Define entity types:
  - `Agent` (id, name, role, capabilities, kernel_version, last_active).
  - `Repository` (id, name, path, integration_type, last_push, default_branch).
  - `Infrastructure` (id, type, status, endpoints, health_check).
  - `Tool` (id, name, category, risk_level, requires_approval, last_used).
  - `MemorySegment` (id, name, entity_type, last_updated, size, query_count).
  - `ExternalSystem` (id, name, integration_type, api_endpoint, connection_status).

**T2 – Relationship types**
- File: `core/worldmodel/l9_schema.py`
- Define relationship types:
  - `HAS_TOOL` (Agent → Tool, with properties: enabled, last_used, approval_status).
  - `DEPENDS_ON` (Entity → Infrastructure).
  - `WRITES_TO` (Tool/Agent → MemorySegment).
  - `READS_FROM` (Agent → MemorySegment).
  - `INTEGRATES_WITH` (Agent → ExternalSystem).
  - `REQUIRES_APPROVAL` (Tool → Agent [Igor], with approval_latency).

**T3 – Initialize world model with L9 entities**
- File: `core/worldmodel/runtime.py`, add function:
  - `async def initialize_l9_world_model() -> None`
  - Create entity nodes for all known agents, tools, segments, infrastructure.
  - Create relationships based on current configuration.
  - Should be called at startup.

**T4 – Event-to-insight conversion**
- File: `core/worldmodel/insight_emitter.py` (new)
- Implement:
  - `on_tool_called(tool_name, agent_id, success) -> Insight`
  - `on_approval_changed(task_id, new_status, reason) -> Insight`
  - `on_memory_written(segment_name, content_type) -> Insight`
  - `on_kernel_updated(kernel_name, changes) -> Insight`
  - `on_repo_pushed(repo_name, branch, commits) -> Insight`
- Each insight includes: timestamp, event_type, entities involved, metadata.

**T5 – Hook events into executor**
- File: `core/agents/executor.py`, in `dispatch_tool_call()` and other key points
- After tool call completes, call `insight_emitter.on_tool_called(...)`.
- After approval state change, call `insight_emitter.on_approval_changed(...)`.
- Ensure emissions are non-blocking (fire-and-forget or async).

**T6 – World model query API**
- File: `api/server.py`, add endpoints:
  - `GET /worldmodel/agent/{agent_id}/capabilities` → list tools, segments readable/writable.
  - `GET /worldmodel/infrastructure/status` → health status of Postgres, Redis, Caddy, etc.
  - `GET /worldmodel/approvals/history?limit=10` → recent approvals.
  - `GET /worldmodel/integrations` → list connected external systems.
- Queries use the world model client to fetch and aggregate data.

**T7 – L's world model reasoning**
- File: `core/agents/adaptive_prompting.py`, extend or new function:
  - Before high-risk decisions, L queries world model: "What are my current capabilities? What is the state of external integrations? Have similar decisions been made before?"
  - Prepend world model context to L's system prompt.

**T8 – Integration test**
- File: `tests/integration/test_world_model.py` (new)
- Initialize world model.
- Simulate a tool call and verify insight is created.
- Query world model endpoints and verify data is correct.
- Verify L can use world model context in decisions.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm world model runtime and client exist and support entity/relationship creation.
2. Verify Neo4j or other backing store is running for world model.
3. Check if insight emission infrastructure exists; if not, design minimal async event bus.

### PHASES 1–6

Validation:
- **Positive:** Create entities, emit insights, query endpoints, verify L gets context.
- **Negative:** Graceful handling if world model unavailable (L operates with reduced context).
- **Regression:** Existing agent behavior unchanged; world model is supplementary.

***
