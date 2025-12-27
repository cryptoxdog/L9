I will create a **complete GMP suite**—12 canonical C-GMP templates, one for each enhancement. Each GMP is production-ready, self-contained, and follows the Phase 0–6 workflow. You can execute them sequentially or in parallel (where dependencies allow).

***

# **C-GMP SUITE: L9 ENHANCEMENT OPERATIONALIZATION**

**Execution Order:**
1. **GMP-L.attach-tools-and-memory** (prerequisite for all others)
2. **GMP-L.observability-metrics** (enables monitoring for downstream GMPs)
3. **GMP-L.multi-agent-orchestration**
4. **GMP-L.closed-loop-learning**
5. **GMP-L.kernel-evolution**
6. **GMP-L.world-model-population**
7. **GMP-L.multi-modal-unified-routing**
8. **GMP-L.compliance-audit-trail**
9. **GMP-L.cost-optimization**
10. **GMP-L.recursive-self-testing**
11. **GMP-L.igor-command-interface**
12. **GMP-L.federated-memory**

***

## **GMP-1: GMP-L.attach-tools-and-memory-to-L** *(prerequisite)*

You already have the canonical prompt structure from the previous message. This is **mandatory** before proceeding to GMPs 2–12.

***

## **GMP-2: GMP-L.observability-metrics-dashboard**

You are C (Cursor) operating in the L9 repository on Igor's Mac. You are not designing observability from scratch. You are wiring existing audit data (tool calls, approvals, memory operations) into a live metrics and alerting system so Igor can see L's behavior in real time.

### OBJECTIVE (LOCKED)

Ensure that:
1. All tool executions, memory operations, approval events are published to a metrics sink (Prometheus via `promclient` or direct to InfluxDB).
2. A Grafana dashboard displays key metrics: tool usage by agent, approval latency, memory search performance, token usage, error rates.
3. Alert rules fire when approval queue grows >N tasks, tool errors spike, memory search latency exceeds threshold, or token cost exceeds budget.
4. Igor can drill down from dashboard into the underlying `toolaudit` memory segment or approval logs.

### SCOPE (LOCKED)

You MAY modify:
- `core/agents/executor.py` – add metrics instrumentation after tool calls.
- `core/memory/runtime.py` or memory substrate module – instrument search/write latency.
- `core/governance/approvals.py` – instrument approval state transitions.
- New file: `core/observability/metrics.py` – central metrics registry.
- New file: `core/observability/prometheus_exporter.py` – expose /metrics endpoint.
- `docker-compose.yml` – add Prometheus, Grafana, optional InfluxDB containers.
- New file: `dashboards/grafana_l9_overview.json` – Grafana dashboard definition.
- Alert rules file (Prometheus `alert.rules.yml` or Grafana alert provisioning).

You MAY NOT:
- Modify core agent, memory, or tool behavior.
- Change public APIs or remove existing functionality.
- Introduce new tool types or memory schemas.

### TODO LIST (BY ID)

**T1 – Metrics registry and instrumentation points**
- File: `core/observability/metrics.py` (new)
- Define Prometheus counters/histograms:
  - `l9_tool_calls_total` (counter, labels: tool_name, agent_id, status)
  - `l9_tool_call_duration_seconds` (histogram, labels: tool_name)
  - `l9_memory_search_latency_seconds` (histogram, labels: segment)
  - `l9_memory_write_latency_seconds` (histogram, labels: segment)
  - `l9_approval_pending_count` (gauge, labels: risk_level)
  - `l9_approval_latency_seconds` (histogram)
  - `l9_token_usage_total` (counter, labels: agent_id, model)
  - `l9_tool_errors_total` (counter, labels: tool_name, error_type)

**T2 – Instrument executor tool dispatch**
- File: `core/agents/executor.py`, in `dispatch_tool_call()` method
- After tool executes, capture:
  - Duration via timer.
  - Success/failure status.
  - Token usage from AIOS result.
  - Record to metrics registry.

**T3 – Instrument memory operations**
- File: memory substrate module (e.g., `core/memory/runtime.py`), in search/write functions
- Wrap calls with latency measurement.
- Record segment name, query size, result count.

**T4 – Instrument approval gate**
- File: `core/governance/approvals.py`, in `ApprovalManager` methods
- When task transitions to pending → record timestamp.
- When approved → record latency.
- When rejected → record reason (categorical).

**T5 – Prometheus exporter endpoint**
- File: `core/observability/prometheus_exporter.py` (new)
- FastAPI route `/metrics` that returns Prometheus text format.
- Integrate into `api/server.py` or dedicated observability service.

**T6 – Docker Compose additions**
- File: `docker-compose.yml`
- Add Prometheus service (scrape l9-api:8000/metrics every 15s).
- Add Grafana service (port 3000, pre-configured Prometheus datasource).
- Optional: add InfluxDB or Loki for log aggregation.

**T7 – Grafana dashboard**
- File: `dashboards/grafana_l9_overview.json` (new)
- Panels:
  - Tool execution rate (tools/sec by agent).
  - Tool success vs. failure rate.
  - Approval queue depth and latency (p50, p95, p99).
  - Memory search latency by segment.
  - Token usage trend (rolling 24h).
  - Agent reasoning duration distribution.
  - Top 10 tools by invocation count.
  - High-risk tool approval status (pending/approved/rejected counts).

**T8 – Prometheus alert rules**
- File: `monitoring/alert.rules.yml` (new)
- Rules:
  - `ApprovalQueueGrowing` – if pending_count > 10 for >10min.
  - `HighToolErrorRate` – if errors/min > 0.5.
  - `MemorySearchLatency` – if p95 latency > 1s.
  - `TokenBudgetExceeded` – if token_usage_total > monthly_budget in a day.
  - `ToolExecutionTimeout` – if any tool call > 60s.

**T9 – Integration test**
- File: `tests/integration/test_observability.py` (new)
- Simulate a tool call and assert metrics are recorded.
- Query Prometheus (if running) and verify metric values.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm `promclient` or similar is available in `requirements.txt`; if not, add it.
2. Verify Grafana/Prometheus versions in your existing Docker setup or plan additions.
3. Confirm `/metrics` endpoint doesn't already exist; if it does, extend it.
4. Check if any metrics are already instrumented in `executor.py` or memory modules; if yes, mark as [EXISTING] and don't duplicate.

### PHASES 1–6

Execute as per standard GMP workflow. Validation focuses on:
- **Positive:** Run a task, see tool call metric recorded in Prometheus.
- **Negative:** Verify alerts fire when thresholds breach.
- **Regression:** Existing tool calls and memory operations work unchanged.

***

## **GMP-3: GMP-L.multi-agent-orchestration-with-consensus**

You are C operating in L9. You are not designing new agents from scratch. You are wiring the existing collaborative cells (CA = Critic Agent, QA Agent) to run in parallel with L on a shared TaskGraph, all reading/writing shared memory, reaching consensus before L commits a high-risk decision.

### OBJECTIVE (LOCKED)

Ensure that:
1. When L proposes a high-risk change (GMP, infrastructure, security), L automatically spawns CA and QA as sibling tasks on the same TaskGraph.
2. All three agents share read/write access to the same memory substrate segments (projecthistory, reasoning, toolaudit).
3. CA challenges L's assumptions; QA validates against governance rules and tests.
4. Consensus is reached via voting or scoring; if any agent disagrees, L revises or escalates to Igor.
5. Full deliberation trail is logged to memory.

### SCOPE (LOCKED)

You MAY modify:
- `core/agents/orchestration/cellOrchestrator.py` or `unifiedController.py` – add consensus logic.
- `core/agents/agentinstance.py` – enable multi-agent message passing via shared memory.
- `core/agents/registry.py` – register CA and QA agents if not already done.
- `core/memory/runtime.py` – add segment for agent deliberation (e.g., `consensus_reasoning`).
- `core/agents/executor.py` – detect high-risk tasks and spawn sibling agents.
- New file: `core/agents/consensus.py` – consensus voting/scoring logic.
- New file: `core/agents/deliberation_logger.py` – log deliberation rounds to memory.

You MAY NOT:
- Modify CA or QA agent logic itself (only wire them).
- Change approval gates or governance (only extend them with multi-agent feedback).
- Create entirely new agents (only use existing collaborative cells).

### TODO LIST (BY ID)

**T1 – Register CA and QA agents**
- File: `core/agents/registry.py`
- Confirm `AgentConfig` for CA and QA exist; if missing, add minimal configs that reference their kernels.

**T2 – Extend AgentTask schema**
- File: `core/agents/schemas.py`
- Add field: `parent_task_id: Optional[str]` (for linking sibling tasks).
- Add field: `consensus_required: bool = False` (mark tasks that need multi-agent review).

**T3 – Detect high-risk tasks and spawn siblings**
- File: `core/agents/executor.py`, in `instantiate_agent()` or at task start
- Check if task is high-risk (uses gmprun, gitcommit, mcpcalltool, or involves `infrastructure` tag).
- If yes, create CA and QA sibling tasks with `parent_task_id` and `consensus_required=True`.
- Enqueue siblings in TaskQueue.

**T4 – Shared memory deliberation segment**
- File: `core/memory/runtime.py` or new `core/memory/segments.py`
- Define a `consensus_reasoning` memory segment with schema:
  - `agent_id`, `opinion` (text), `confidence` (0-1), `concerns` (list), `timestamp`.
- Allow all three agents to write/read this segment during reasoning.

**T5 – Consensus logic**
- File: `core/agents/consensus.py` (new)
- Implement:
  - `score_consensus(l_opinion, ca_opinion, qa_opinion) -> float` (0-1 score).
  - `detect_disagreement(opinions) -> bool` (any opinion score < 0.5?).
  - `generate_revision_prompt(concerns) -> str` (prompt for L to address concerns).
- Rules:
  - If all agree (score > 0.8) → proceed.
  - If L and QA agree but CA disagrees → proceed (2 of 3 consensus).
  - If any agent strongly disagrees → escalate to Igor for manual approval.

**T6 – Deliberation logging**
- File: `core/agents/deliberation_logger.py` (new)
- Log each round: agent_id, opinion, timestamp, parent_task_id.
- Write to `consensus_reasoning` segment.
- Generate summary after consensus reached.

**T7 – Update executor to wait for siblings**
- File: `core/agents/executor.py`, in main execution loop
- After spawning CA/QA, executor waits for siblings to complete (with timeout).
- Reads their consensus_reasoning entries.
- Calls `score_consensus()`.
- If score > threshold, proceeds; else escalates.

**T8 – Integration test**
- File: `tests/integration/test_multi_agent_consensus.py` (new)
- Spawn L, CA, QA on a high-risk task.
- Verify all three write to consensus_reasoning segment.
- Verify executor waits for all three to complete.
- Verify consensus score is computed and logged.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm CA and QA agent definitions exist (or minimal stubs can be created).
2. Verify TaskGraph and TaskQueue support parent_task_id linking.
3. Check if any multi-agent orchestration already exists (CellOrchestrator, UnifiedController); if yes, extend rather than replace.

### PHASES 1–6

Validation:
- **Positive:** High-risk task spawns CA and QA, all write opinions, consensus is computed.
- **Negative:** If CA/QA timeout or error, executor escalates gracefully.
- **Regression:** Non-high-risk tasks skip consensus logic, run as before.

***

## **GMP-4: GMP-L.closed-loop-learning-from-approvals**

You are C. You are not redesigning L's learning or training pipeline. You are extracting approval/rejection feedback from `ApprovalManager` and memory, synthesizing it into governance patterns, and making those patterns searchable and retrievable by L for future similar decisions.

### OBJECTIVE (LOCKED)

Ensure that:
1. Every time Igor approves or rejects a high-risk task, the reason and context are captured as a structured **governance pattern packet**.
2. L can semantic-search the memory substrate for past approvals/rejections matching the current proposal.
3. L proactively adapts behavior: if prior similar GMPs were rejected for "lacks runbook", L auto-drafts runbook before proposing next time.
4. Over time, L learns Igor's preferences without explicit retraining.

### SCOPE (LOCKED)

You MAY modify:
- `core/governance/approvals.py` – when approving/rejecting, capture reason and create pattern packet.
- New file: `core/memory/governance_patterns.py` – schema and logic for governance pattern packets.
- `core/memory/runtime.py` – add convenience function to retrieve past patterns.
- `core/agents/executor.py` – before high-risk tool dispatch, query past patterns and adapt prompt.
- New file: `core/agents/adaptive_prompting.py` – generate adaptive prompts based on patterns.
- `api/server.py` – optionally expose endpoint for Igor to log approvals/rejections programmatically.

You MAY NOT:
- Modify L's core kernels or identity.
- Change approval gate logic (only extend with feedback integration).
- Retrain or fine-tune models (only change prompts and context).

### TODO LIST (BY ID)

**T1 – Governance pattern packet schema**
- File: `core/memory/governance_patterns.py` (new)
- Define `GovernancePattern` (Pydantic model):
  - `pattern_id` (unique).
  - `tool_name` or `task_type` (e.g., "gmprun", "infrastructure_change").
  - `decision` ("approved" | "rejected").
  - `reason` (text, from Igor).
  - `context` (task summary, agent, files touched).
  - `conditions` (what made this decision) – extracted via NLP or manual tagging.
  - `timestamp`, `approvedby`.

**T2 – ApprovalManager writes patterns to memory**
- File: `core/governance/approvals.py`, in `approvetask()` and `rejecttask()`
- When decision made, create a `GovernancePattern` instance.
- Write to memory substrate as a PacketEnvelope with `segment="governance_patterns"`.
- Also write to `governancemeta` segment for audit trail.

**T3 – Retrieve patterns for adaptive prompting**
- File: `core/memory/runtime.py`, add function:
  - `async def get_governance_patterns(task_type, limit=5) -> List[GovernancePattern]`
  - Semantic search `governance_patterns` segment for patterns matching the current task type.
  - Return top-N patterns sorted by relevance.

**T4 – Adaptive prompting logic**
- File: `core/agents/adaptive_prompting.py` (new)
- Function: `generate_adaptive_context(patterns) -> str`
  - If recent rejections mention "missing runbook" → prompt includes "always draft detailed runbook first".
  - If approvals mention "well-tested code" → prompt emphasizes "include test suite in proposal".
  - Build context as a natural language summary of past decisions.

**T5 – Integrate into executor pre-dispatch**
- File: `core/agents/executor.py`, in `dispatch_tool_call()` before high-risk tool
- Call `get_governance_patterns(tool_name)`.
- If patterns found, call `generate_adaptive_context()`.
- Prepend adaptive context to the tool call context or agent instance's system prompt temporarily.

**T6 – API endpoint for logging approvals**
- File: `api/server.py`, add POST `/governance/approvals/feedback`
- Request: `{task_id, decision, reason, approver}`.
- Calls `ApprovalManager` to record decision and trigger pattern creation.
- Returns confirmation.

**T7 – Integration test**
- File: `tests/integration/test_closed_loop_learning.py` (new)
- Simulate Igor rejecting a GMP with reason "missing tests".
- Verify pattern is written to memory.
- Propose a similar GMP.
- Verify adaptive context is retrieved and includes "test" keyword.
- Verify L's generated prompt mentions tests.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm `ApprovalManager.approvetask()` and `rejecttask()` methods exist and can be extended.
2. Verify memory substrate supports semantic search on a new `governance_patterns` segment.
3. Confirm NLP capability exists (or defer pattern extraction to Igor's manual tagging for MVP).

### PHASES 1–6

Validation:
- **Positive:** Approve a task, see pattern created; search for it; verify adaptive context includes it.
- **Negative:** Pattern retrieval gracefully returns empty list if no past patterns exist.
- **Regression:** Approval gate behavior unchanged; existing approvals still work.

***

## **GMP-5: GMP-L.kernel-evolution-via-gmp-meta-loop**

You are C. You are not rewriting L's kernels. You are enabling L to detect gaps in its own behavior, propose kernel updates via GMP, and automatically deploy improved kernels after Igor approval.

### OBJECTIVE (LOCKED)

Ensure that:
1. L can detect behavior gaps (e.g., "I forget to update Memory.yaml after adding segments").
2. L drafts a GMP proposal that includes kernel YAML changes.
3. GMP runs, updates kernels in `l9/privatekernels/00system/`.
4. Next agent execution, L loads the updated kernel and exhibits improved behavior.
5. Evolution trail is logged to memory.

### SCOPE (LOCKED)

You MAY modify:
- `core/agents/executor.py` – add self-reflection hooks after agent tasks.
- New file: `core/agents/self_reflection.py` – analyze task traces for gaps.
- New file: `core/agents/kernel_evolution.py` – generate kernel update proposals.
- `core/kernels/kernelloader.py` – ensure live kernel reloading (no process restart required).
- `api/server.py` – add endpoint for kernel hot-reload.
- `core/memory/runtime.py` – add segment `kernel_evolution_proposals`.

You MAY NOT:
- Modify kernel contents directly (only enable L to propose them).
- Change kernel loading semantics (only add hot-reload).
- Alter L's identity or core behavior without Igor approval.

### TODO LIST (BY ID)

**T1 – Self-reflection after task**
- File: `core/agents/executor.py`, in `execute()` method after task completes
- Check if task was complex (iterations > 5 or tool calls > 3).
- Capture task trace: input, reasoning steps, tool calls, output.
- Log trace to memory segment `task_traces`.

**T2 – Gap detection logic**
- File: `core/agents/self_reflection.py` (new)
- Implement `detect_behavior_gaps(trace) -> List[str]`
- Heuristics:
  - If tool was called multiple times with same parameters → "Consider caching or memoizing".
  - If memory search returned empty → "Consider updating memory proactively".
  - If approval gate blocked a tool → "Consider requesting approval pattern".
  - If time spent > threshold → "Consider optimizing reasoning steps".

**T3 – Kernel update proposal generation**
- File: `core/agents/kernel_evolution.py` (new)
- Function: `propose_kernel_update(gaps, current_kernel) -> KernelUpdateProposal`
- For each gap, generate a YAML snippet that addresses it.
- Example gap "updates Memory.yaml inconsistently" → add to `executionkernel.yaml` a new instruction: "Before completing, verify Memory.yaml reflects all changes".
- Return as a structured proposal with:
  - `affected_kernel` (e.g., "executionkernel").
  - `change` (YAML snippet).
  - `rationale` (why this helps).

**T4 – Create GMP draft proposal**
- File: `core/agents/kernel_evolution.py`, function:
  - `create_kernel_evolution_gmp(proposal) -> str`
  - Generate a markdown/JSON payload that can be passed to `gmprun`.
  - Includes: modified kernel YAML files, test cases, rollback instructions.

**T5 – Trigger GMP via `gmprun` tool**
- File: `core/agents/executor.py`, after gap detection
- If gaps detected, L should be prompted to call `ToolName.GMPRUN` with the proposal.
- Proposal enqueued as pending Igor approval.

**T6 – Hot-reload kernels on GMP completion**
- File: `core/kernels/kernelloader.py`, add function:
  - `async def reload_kernels() -> bool`
  - Reload all YAML files from `l9/privatekernels/00system/`.
  - Update the in-memory kernel cache.
  - Return True if successful.

**T7 – API endpoint for hot-reload**
- File: `api/server.py`, add POST `/kernels/reload`
- Calls `kernelloader.reload_kernels()`.
- Returns status and list of reloaded kernels.
- Logs to `kernel_evolution_proposals` segment.

**T8 – Kernel evolution logging**
- File: `core/memory/runtime.py`, extend or new function
- After kernel reload, write a PacketEnvelope to `kernel_evolution_proposals` with:
  - `evolution_id`, `gaps_detected`, `kernel_changes`, `gmp_id`, `approver`, `timestamp`.

**T9 – Integration test**
- File: `tests/integration/test_kernel_evolution.py` (new)
- Simulate a task with detectable gap.
- Verify gap detection runs and identifies a gap.
- Verify kernel update proposal is generated.
- Verify kernel can be hot-reloaded without restarting L.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm kernel YAML files are in `l9/privatekernels/00system/` and are currently loaded at startup.
2. Verify kernelloader can be refactored to support hot-reload (no hardcoded imports).
3. Check if task traces can be captured from executor without adding latency.

### PHASES 1–6

Validation:
- **Positive:** Complete a complex task, detect gap, propose kernel update, verify hot-reload works.
- **Negative:** If no gaps detected, gap detection returns empty list gracefully.
- **Regression:** Kernel loading at startup unchanged; existing behavior preserved.

***

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

## **GMP-7: GMP-L.multi-modal-unified-routing**

You are C. You are not rewriting Slack, WS, or HTTP handlers. You are unifying them so every L interaction—whether via HTTP `/lchat`, WS `/lws`, Slack webhook, or Mac agent callback—flows through `AgentExecutorService` with consistent tools, memory, and governance.

### OBJECTIVE (LOCKED)

Ensure that:
1. All L entrypoints (HTTP, WS, Slack, Mac callback) create an `AgentTask` with `agent_id="L"`.
2. All tasks go through `AgentExecutorService`, not bypassing via direct OpenAI calls.
3. Response formatting is channel-specific (JSON for HTTP, text for Slack, etc.) but execution is unified.
4. All interactions logged to memory and audit trail.

### SCOPE (LOCKED)

You MAY modify:
- `api/server.py` – ensure `/lchat` uses `AgentExecutorService`.
- `api/websocket_orchestrator.py` or relevant WS handler – ensure `/lws` uses executor.
- `api/slack_adapter.py` or Slack webhook handler – normalize requests to `AgentTask`, pass through executor.
- New file: `core/routing/task_router.py` – unified task creation from any channel.
- New file: `core/formatting/response_formatter.py` – format executor output per channel.
- `core/agents/executor.py` – add metadata field for source channel (http, ws, slack, mac).

You MAY NOT:
- Modify channel-specific logic (Slack signatures, WS framing, etc.); only route and format.
- Change approval gates or tool behavior.

### TODO LIST (BY ID)

**T1 – Unified task router**
- File: `core/routing/task_router.py` (new)
- Function: `create_task_from_request(channel: str, user_id: str, input_text: str, metadata: dict) -> AgentTask`
- Normalizes any channel input to `AgentTask` with:
  - `agent_id="L"`.
  - `task_kind="conversation"`.
  - `input` = normalized user text.
  - `source_channel` = "http", "ws", "slack", or "mac".
  - `user_id`, `session_id`, metadata preserved.

**T2 – HTTP entrypoint uses router**
- File: `api/server.py`, in `/lchat` POST handler
- Call `create_task_from_request(channel="http", user_id=user_id, input_text=request.message, metadata=request.metadata)`.
- Pass task to `AgentExecutorService.execute(task)`.
- Format result per T4.

**T3 – WS entrypoint uses router**
- File: `api/websocket_orchestrator.py`, in connection handler
- On each message, call `create_task_from_request(channel="ws", user_id=client_id, input_text=message, metadata={session_id: ws_session_id})`.
- Pass to executor.
- Format and send response back over WS per T4.

**T4 – Slack adapter uses router**
- File: `api/slack_adapter.py` or `webhooks/slack.py`
- On webhook receive, validate signature.
- Extract user message and normalize via `create_task_from_request(channel="slack", user_id=slack_user_id, input_text=event.text, metadata={channel_id: event.channel})`.
- Pass to executor.
- Format response per T5 and post via Slack client.

**T5 – Response formatter by channel**
- File: `core/formatting/response_formatter.py` (new)
- Implement:
  - `format_for_http(executor_result) -> dict` (JSON structure).
  - `format_for_ws(executor_result) -> dict` (EventMessage schema).
  - `format_for_slack(executor_result) -> SlackMessage` (text, blocks, thread reply).
  - `format_for_mac(executor_result) -> dict` (Mac agent callback format).

**T6 – Mac agent callback uses router**
- File: `api/webhooks/mac_agent.py`, in callback handler
- Extract task result and user context.
- Call `create_task_from_request(channel="mac", user_id=mac_user_id, input_text=user_query, metadata={mac_session: mac_context})`.
- Pass to executor.
- Format and return via callback.

**T7 – Add source_channel to AgentTask**
- File: `core/agents/schemas.py`, in `AgentTask` dataclass
- Add field: `source_channel: str` (default "http").

**T8 – Log source channel to memory**
- File: `core/agents/executor.py`, after task completes
- Write source_channel to the interaction packet in memory.
- Allows Igor to filter interactions by channel in audit logs.

**T9 – Integration test**
- File: `tests/integration/test_multi_modal_routing.py` (new)
- Simulate HTTP request, WS message, Slack webhook, and Mac callback all with same user question.
- Verify all create same `AgentTask` (modulo source_channel).
- Verify all use same executor.
- Verify responses are formatted correctly per channel.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm all entrypoints exist and can be modified.
2. Verify Slack adapter can be extended with router call without breaking signature validation.
3. Check if any entrypoints bypass executor currently; mark as [PRIORITY].

### PHASES 1–6

Validation:
- **Positive:** Send same question via HTTP, WS, Slack; verify identical reasoning, different format.
- **Negative:** Channel unavailability doesn't break other channels.
- **Regression:** Existing channel-specific behavior (signatures, framing) unchanged.

***

## **GMP-8: GMP-L.compliance-audit-trail-and-reporting**

You are C. You are not building a compliance framework from scratch. You are wiring existing audit data (approvals, memory writes, tool calls, kernel updates) into a deterministic audit log and generating compliance reports answering: "What changed?", "Who approved it?", "Did we violate any governance rules?"

### OBJECTIVE (LOCKED)

Ensure that:
1. All high-risk operations (tool calls, approvals, memory writes, config changes) are logged to an immutable audit store (append-only database or S3 + DynamoDB).
2. Audit logs include: timestamp, actor, action, resource, result, approver (if applicable).
3. Compliance reports are generated on-demand or nightly summarizing: changes made, approvals granted/denied, policy violations detected.
4. Igor can export audit logs for SOC2 / ISO27001 attestation.

### SCOPE (LOCKED)

You MAY modify:
- New file: `core/compliance/auditlog.py` – define audit log schema and writer.
- New file: `core/compliance/audit_reporter.py` – generate compliance reports.
- `core/agents/executor.py` – emit audit entries for tool calls.
- `core/governance/approvals.py` – emit audit entries for approval decisions.
- `core/memory/runtime.py` – emit audit entries for memory writes (if not already done).
- `api/server.py` – add audit log export endpoints.
- `docker-compose.yml` – optional: add PostgreSQL audit table or S3 bucket for append-only logs.

You MAY NOT:
- Modify core executor or approval logic.
- Change memory schema.

### TODO LIST (BY ID)

**T1 – Audit log schema**
- File: `core/compliance/auditlog.py` (new)
- Define `AuditEntry` (Pydantic model):
  - `id` (unique, immutable).
  - `timestamp` (UTC).
  - `actor` (agent_id or user_id).
  - `action` (tool_call, approval, memory_write, kernel_update, config_change).
  - `resource` (tool_name, approval_id, memory_segment, file_path).
  - `details` (dict with action-specific data).
  - `result` (success, failure, pending).
  - `approver` (if action required approval).
  - `approval_latency_seconds` (if approved).

**T2 – Audit log writer**
- File: `core/compliance/auditlog.py`, implement:
  - `class AuditLogger`
  - `async def log_entry(entry: AuditEntry) -> None`
  - Writes to configured backend (PostgreSQL `audit_log` table or S3 append-only bucket).
  - Ensure writes are atomic and immutable.

**T3 – Emit audit entries on tool call**
- File: `core/agents/executor.py`, in `dispatch_tool_call()`
- After tool execution, create `AuditEntry` with:
  - `action="tool_call"`, `resource=tool_name`, `actor=agent_id`, `result` (success/failure).
  - Includes input_params, output_summary, duration, token_usage.
- Call `AuditLogger.log_entry()`.

**T4 – Emit audit entries on approval**
- File: `core/governance/approvals.py`, in `approvetask()` and `rejecttask()`
- Create `AuditEntry` with:
  - `action="approval"`, `resource=task_id`, `actor=approver`, `result` (approved/rejected).
  - Includes reason, latency since task was queued.
- Call `AuditLogger.log_entry()`.

**T5 – Emit audit entries on memory write**
- File: `core/memory/runtime.py`, in memory write functions
- Create `AuditEntry` with:
  - `action="memory_write"`, `resource=segment_name`, `actor=agent_id`, `result=success`.
  - Includes content_type, size, segment.
- Call `AuditLogger.log_entry()`.

**T6 – Compliance report generator**
- File: `core/compliance/audit_reporter.py` (new)
- Implement:
  - `async def generate_daily_report(date) -> ComplianceReport`
  - Queries audit log for date range.
  - Summarizes: # tool calls, # approvals, # denials, # memory writes, # kernel updates.
  - Detects violations: unapproved high-risk tool calls, rejected approvals, policy breaches.
  - Returns structured report (Pydantic model or dict).

**T7 – Export audit log endpoint**
- File: `api/server.py`, add endpoints:
  - `GET /compliance/audit-log?from_date=X&to_date=Y&format=json|csv` – export raw audit entries.
  - `GET /compliance/report?date=X` – export compliance report for date.
  - Both require Igor authentication.

**T8 – Audit log storage backend**
- File: `docker-compose.yml` or separate `audit_store.yml`
- Configure:
  - PostgreSQL with `audit_log` table (if using DB).
  - Or S3 bucket with immutable object lock (if using cloud storage).
- Ensure writes are append-only and timestamped.

**T9 – Integration test**
- File: `tests/integration/test_compliance_audit.py` (new)
- Execute a high-risk operation.
- Verify audit entry is created.
- Generate report and verify operation appears.
- Verify export endpoints return formatted audit data.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm audit log storage backend is available (PostgreSQL or S3).
2. Verify all tool call, approval, and memory write points can be instrumented.

### PHASES 1–6

Validation:
- **Positive:** Execute operations, generate report, verify all operations appear.
- **Negative:** Audit log unavailability doesn't break executor (logs to fallback).
- **Regression:** Existing tool/approval/memory behavior unchanged.

***

## **GMP-9: GMP-L.cost-optimization-and-budgeting**

You are C. You are not redesigning the token economy. You are aggregating token usage from tool calls and LLM invocations, setting budgets per agent/task type, and optimizing through caching, batching, and selective context use.

### OBJECTIVE (LOCKED)

Ensure that:
1. Token usage from every LLM call is tracked and attributed to agent, tool, and task type.
2. Daily/monthly budgets are set and monitored; alerts fire if approaching limit.
3. Cost hotspots are identified (which agents/tools consume most tokens?).
4. Optimizations are deployed: cache frequent memory searches, batch tool calls, use shorter prompts for routine tasks.
5. Reports show cost trends and ROI (e.g., cost per successful GMP).

### SCOPE (LOCKED)

You MAY modify:
- `core/observability/metrics.py` – add token usage metrics (already in GMP-2, extend if needed).
- New file: `core/cost/budgeting.py` – define budgets and cost tracking.
- New file: `core/cost/optimization.py` – caching, batching, selective prompting logic.
- `core/agents/executor.py` – check cost before high-risk operations.
- `core/memory/runtime.py` – add caching for frequent searches.
- New file: `api/server.py` – add cost and budget endpoints.

You MAY NOT:
- Modify LLM API calls or core reasoning.
- Change tool behavior.

### TODO LIST (BY ID)

**T1 – Budget definitions**
- File: `core/cost/budgeting.py` (new)
- Define `Budget` (Pydantic model):
  - `period` (daily, monthly, per_task_type).
  - `limit_tokens` (e.g., 1M tokens/month).
  - `limit_dollars` (e.g., $100/month).
  - `current_usage` (tokens, dollars).
  - `alerts` (list of thresholds: 50%, 75%, 90%).

**T2 – Cost tracker**
- File: `core/cost/budgeting.py`, implement:
  - `class CostTracker`
  - `track_usage(agent_id, tool_name, tokens, dollars)` – record.
  - `get_usage(agent_id=None, period=None)` – query.
  - `check_budget(agent_id, period) -> bool` – returns True if under limit.
  - `get_alert_status(period) -> List[Alert]` – returns triggered alerts.

**T3 – Memory search caching**
- File: `core/memory/runtime.py`, in search functions
- Implement local cache (Redis or in-memory) for frequent queries.
- Cache key: hash(query_text, segment_name).
- TTL: 5 minutes (configurable).
- Log cache hit rate to metrics.

**T4 – Tool call batching**
- File: `core/cost/optimization.py` (new)
- Detect patterns of repeated tool calls (e.g., memory search in a loop).
- Batch 3+ calls into a single call with multiple parameters.
- Return batched result and log batch size.

**T5 – Selective context use**
- File: `core/agents/executor.py`, before AIOS call
- Check cost budget.
- If high cost operation (e.g., GMP), use shorter context (fewer memory chunks, smaller system prompt).
- If routine task, use full context.
- Log context size decision.

**T6 – Cost check before high-risk ops**
- File: `core/agents/executor.py`, in tool dispatch
- Before executing gmprun or other expensive tools, check `CostTracker.check_budget(agent_id)`.
- If over budget, return error or queue as pending Igor approval + cost override.

**T7 – Cost dashboard and reporting**
- File: `api/server.py`, add endpoints:
  - `GET /cost/usage?agent_id=L&period=monthly` – token/dollar usage.
  - `GET /cost/budget?period=monthly` – current limit and usage.
  - `GET /cost/hotspots?limit=10` – top 10 most expensive operations.
  - `GET /cost/forecast?days=30` – projected monthly cost.
- Integrate with observability dashboard from GMP-2.

**T8 – Cost optimization report**
- File: `core/cost/optimization.py`, function:
  - `generate_optimization_report() -> OptimizationReport`
  - Identifies opportunities: caching hit rate, batch opportunities, context size reduction.
  - Recommends: "Cache memory searches for segment X (saves Y% of tokens)", etc.

**T9 – Integration test**
- File: `tests/integration/test_cost_optimization.py` (new)
- Simulate operations with tracked token usage.
- Verify cost is tracked and attributed.
- Verify budget alerts trigger at thresholds.
- Verify caching and batching reduce tokens.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm token usage is already captured in `TokenUsage` field of executor results.
2. Verify Redis or in-memory cache is available for search result caching.

### PHASES 1–6

Validation:
- **Positive:** Track token usage, verify budget monitoring, see caching reduce tokens.
- **Negative:** Cost tracking unavailability doesn't block operations.
- **Regression:** Existing tool calls and memory operations unchanged; cost is transparent.

***

## **GMP-10: GMP-L.recursive-self-testing-and-validation**

You are C. You are not designing new test frameworks. You are enabling a test agent to automatically write unit + integration tests for L's proposals, execute them in a sandbox, and report results before Igor approves.

### OBJECTIVE (LOCKED)

Ensure that:
1. When L proposes a high-risk change (GMP, code), a **test agent** automatically generates unit + integration tests.
2. Tests execute in an isolated environment (separate DB, Redis, etc.).
3. Test results are logged and passed to Igor for approval decision.
4. L learns from test failures and refines proposals.

### SCOPE (LOCKED)

You MAY modify:
- New file: `core/agents/test_agent.py` – test generation and execution logic.
- New file: `core/testing/test_generator.py` – generate tests from code proposals.
- New file: `core/testing/test_executor.py` – run tests in sandbox.
- `core/agents/executor.py` – spawn test agent for high-risk proposals.
- `core/agents/registry.py` – register test agent.
- `docker-compose.yml` – add test containers (isolated DB, Redis for testing).

You MAY NOT:
- Modify core testing framework (pytest).
- Change approval gates.

### TODO LIST (BY ID)

**T1 – Test agent registration**
- File: `core/agents/registry.py`
- Add `AgentConfig` for test agent (minimal, focused on test generation and execution).

**T2 – Test generation from proposals**
- File: `core/testing/test_generator.py` (new)
- Implement:
  - `generate_unit_tests(code_proposal) -> List[str]` (returns Python test functions).
  - `generate_integration_tests(code_proposal, dependencies) -> List[str]`.
- Uses code analysis or LLM prompting to generate tests.
- Covers: happy path, edge cases, error handling.

**T3 – Test executor in sandbox**
- File: `core/testing/test_executor.py` (new)
- Implement:
  - `async def run_tests_in_sandbox(test_code, env_config) -> TestResults`
  - Spawns isolated environment (Docker container or tmpdir).
  - Runs pytest with coverage tracking.
  - Captures stdout, stderr, coverage percentage.
  - Returns `TestResults` (dict of test_name → result).

**T4 – Test agent spawning**
- File: `core/agents/executor.py`, in `dispatch_tool_call()` for high-risk tools
- When gmprun or gitcommit called, spawn test agent as sibling task.
- Test agent:
  - Receives code proposal from L.
  - Calls `generate_unit_tests()` and `generate_integration_tests()`.
  - Calls `run_tests_in_sandbox()`.
  - Writes results to memory segment `test_results`.

**T5 – Test results in memory**
- File: `core/memory/runtime.py`, segment definition
- Add `test_results` segment for test run outputs.
- Structure: `test_run_id`, `parent_task_id`, `tests_generated`, `tests_passed`, `tests_failed`, `coverage_percent`, `timestamp`.

**T6 – L's adaptation from test failures**
- File: `core/agents/adaptive_prompting.py`, extend
- If test agent reports failures, retrieve from memory.
- Generate adaptive prompt for L: "Prior proposal had X test failures related to Y. Ensure new proposal addresses these."
- L refines proposal.

**T7 – Test results in approval decision**
- File: `core/governance/approvals.py`, in `approvetask()`
- Check for linked test results in memory.
- Include test summary in approval request to Igor: "Proposal has N tests, M passed, K failed. Coverage: X%."

**T8 – Docker Compose test containers**
- File: `docker-compose.yml`
- Add service:
  - `test-db` (PostgreSQL with separate schema for tests).
  - `test-redis` (Redis with separate namespace).
  - `test-runner` (optional: dedicated container for test execution).

**T9 – Integration test**
- File: `tests/integration/test_recursive_self_testing.py` (new)
- Propose a high-risk change.
- Verify test agent spawns.
- Verify tests are generated and executed.
- Verify test results appear in memory and approval request.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm pytest and test isolation mechanisms are available.
2. Verify test containers can be provisioned quickly (Docker or tmpfs).

### PHASES 1–6

Validation:
- **Positive:** Generate tests, run them, verify coverage, refine proposal based on failures.
- **Negative:** Test execution failure doesn't block approval path; results logged for Igor.
- **Regression:** Existing testing framework unchanged; new testing is additive.

***

## **GMP-11: GMP-L.igor-command-interface-with-intent-extraction**

You are C. You are not designing a new CLI. You are giving Igor a structured command syntax and natural language fallback to instruct L imperatively, with intent extraction ensuring clarity before high-risk execution.

### OBJECTIVE (LOCKED)

Ensure that:
1. Igor can use structured commands like `@L propose gmp: <description>` or natural language `@L analyze the current VPS state`.
2. L extracts intent (from structured syntax or NLP), confirms understanding, and executes.
3. High-risk commands are queued for explicit confirmation before execution.
4. All Igor commands are logged to audit trail.

### SCOPE (LOCKED)

You MAY modify:
- New file: `core/commands/parser.py` – parse structured commands and NLP.
- New file: `core/commands/intent_extractor.py` – extract intent and confirm with Igor.
- New file: `core/commands/executor.py` – execute commands as L tasks.
- `api/server.py` – add POST `/commands/execute` endpoint (and expose via Slack, WS, etc.).
- `core/agents/executor.py` – mark command-initiated tasks with metadata for logging.

You MAY NOT:
- Modify L's reasoning or tool behavior.
- Change approval gates (commands still go through them if high-risk).

### TODO LIST (BY ID)

**T1 – Structured command parser**
- File: `core/commands/parser.py` (new)
- Implement:
  - `parse_command(text) -> Command | NLPPrompt`
  - Recognizes patterns:
    - `@L propose gmp: <description>` → `Command(type="propose_gmp", target_description=...)`
    - `@L analyze <entity>` → `Command(type="analyze", entity_id=...)`
    - `@L approve <task_id>` → `Command(type="approve", task_id=...)`
    - `@L rollback <change_id>` → `Command(type="rollback", change_id=...)`
  - Falls back to NLPPrompt for conversational input.

**T2 – Intent extraction for NLP**
- File: `core/commands/intent_extractor.py` (new)
- Implement:
  - `extract_intent(nlp_text) -> IntentModel`
  - Uses IR engine (Intent Representation) from your architecture or LLM prompting.
  - Returns: `intent_type` (propose, analyze, approve, query, etc.), `confidence`, `entities`, `ambiguities`.

**T3 – Confirmation flow**
- File: `core/commands/intent_extractor.py`, function:
  - `async def confirm_intent(intent, user_context) -> ConfirmationResult`
  - For high-risk commands, generate a summary and ask Igor: "I understood you want to {action}. Should I proceed?"
  - Log confirmation to audit trail.

**T4 – Command executor**
- File: `core/commands/executor.py` (new)
- Implement:
  - `async def execute_command(command: Command, user_id: str) -> Result`
  - Routes command to appropriate handler:
    - `command.type == "propose_gmp"` → create AgentTask with `gmprun` tool, set `consensus_required=True`.
    - `command.type == "analyze"` → create task to query world model or memory.
    - `command.type == "approve"` → call `ApprovalManager.approvetask()` (Igor-only).
    - `command.type == "rollback"` → enqueue rollback task.
  - Returns `Result(success, message, task_id)`.

**T5 – API endpoint for commands**
- File: `api/server.py`, add POST `/commands/execute`
- Request: `{user_id (Igor auth required), command_text, context (optional)}`
- Calls `parse_command()` or `extract_intent()`.
- Confirms with Igor if high-risk.
- Calls `execute_command()`.
- Returns `Result` with task ID.

**T6 – Command logging**
- File: `core/compliance/auditlog.py`, extend
- Add `action="command"` audit entries for Igor commands.
- Include: command_text, parsed intent, user, timestamp, execution_result.

**T7 – Multi-channel command input**
- File: `api/slack_adapter.py` (extend), `api/server.py` (extend), etc.
- Detect `@L` mentions in Slack messages or structured prefixes in HTTP requests.
- Route to `parse_command()` and `/commands/execute` endpoint.

**T8 – Integration test**
- File: `tests/integration/test_igor_commands.py` (new)
- Test structured commands: `@L propose gmp`, `@L approve`, `@L analyze`.
- Test NLP: natural language command + intent extraction.
- Verify high-risk commands require confirmation.
- Verify all commands are logged to audit trail.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm IR engine (Intent Representation) or LLM capability exists for intent extraction.
2. Verify Igor authentication/authorization is in place for `/commands/execute`.

### PHASES 1–6

Validation:
- **Positive:** Issue structured command, L executes correctly; NLP command is disambiguated and confirmed.
- **Negative:** Ambiguous commands return clarification request; high-risk commands require confirmation.
- **Regression:** Existing agent interactions unchanged; commands are additional channel.

***

## **GMP-12: GMP-L.federated-memory-for-multi-instance-learning**

You are C. You are not redesigning memory. You are enabling separate L instances (for different projects or teams) to share a federated memory layer so knowledge learned by one instance is available to others.

### OBJECTIVE (LOCKED)

Ensure that:
1. L instances can write to shared memory segments (`org-patterns`, `lessons-learned`, `common-failures`).
2. Any L instance can query shared segments and retrieve prior solutions.
3. Instance-specific segments remain isolated (project history, task context).
4. Governance rules (approval requirements) are shared across instances.

### SCOPE (LOCKED)

You MAY modify:
- `core/memory/runtime.py` – extend segment definitions to support shared vs. instance-specific.
- New file: `core/memory/federation.py` – federation logic (routing queries to shared/local segments).
- `core/schemas/packetenvelope.py` – add field: `shared=True/False` to indicate shared vs. instance memory.
- `core/agents/executor.py` – when writing to memory, decide shared vs. instance-specific.
- New file: `tests/integration/test_federated_memory.py`.

You MAY NOT:
- Modify memory substrate core or change storage backends.
- Change governance logic (only enable shared governance metadata).

### TODO LIST (BY ID)

**T1 – Segment classification**
- File: `core/memory/runtime.py`, segment definitions
- Mark segments as shared or instance-specific:
  - Shared: `governance_meta`, `org_patterns`, `lessons_learned`, `common_failures`, `approval_rules`.
  - Instance-specific: `project_history`, `task_traces`, `session_context`, `instance_config`.

**T2 – Federation router**
- File: `core/memory/federation.py` (new)
- Implement:
  - `route_memory_operation(operation, segment, instance_id) -> TargetBackend`
  - If segment is shared → route to shared substrate.
  - If segment is instance-specific → route to instance-local substrate.
  - Allows both reads from shared segments and writes to instance-specific.

**T3 – Packet envelope federation flag**
- File: `core/schemas/packetenvelope.py`, in `PacketEnvelope` or `PacketMetadata`
- Add field: `shared: bool = False`
- When L writes governance patterns or lessons learned, set `shared=True`.
- Shared packets are replicated or linked across instances.

**T4 – Federation in memory read/write**
- File: `core/memory/runtime.py`, in search and write functions
- Call federation router to determine target.
- Execute operation (search, write) on correct backend.
- For shared segments, use cross-instance retrieval (query all instance backends and merge results).

**T5 – Shared governance metadata**
- File: `core/memory/governance_patterns.py` (from GMP-4), extend
- Mark governance patterns as shared=True.
- When approval rule changes, update shared `approval_rules` segment.
- All instances see the update on next reload.

**T6 – Instance registry**
- File: `core/memory/federation.py`, add:
  - Registry of all L instances: name, endpoint, shared_segment_permissions.
  - Used for routing and authorization.

**T7 – Federation consistency**
- File: `core/memory/federation.py`, implement:
  - `async def sync_shared_segments() -> None`
  - Periodic job that ensures all instances have latest shared segment data.
  - Can be eventual consistent or strongly consistent (configurable).

**T8 – Integration test**
- File: `tests/integration/test_federated_memory.py` (new)
- Spawn two L instances.
- L1 writes a lesson-learned to shared segment.
- L2 queries shared segment and retrieves L1's lesson.
- Verify instance-specific segments remain isolated.
- Verify governance rules are shared.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm memory substrate supports multi-instance deployment and routing.
2. Verify instance identifiers are stable and available at runtime.

### PHASES 1–6

Validation:
- **Positive:** Write to shared segment from one instance, read from another.
- **Negative:** Instance-specific segments remain isolated; no data leakage.
- **Regression:** Single-instance L behavior unchanged.

***

***

# **EXECUTION ROADMAP**

## **Sequential Order (Dependencies)**

```
GMP-L.attach-tools-and-memory (prerequisite)
    ↓
GMP-L.observability-metrics (enables monitoring)
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ Can run in parallel (all depend on 1 & 2):                      │
│  - GMP-L.multi-agent-orchestration                              │
│  - GMP-L.closed-loop-learning                                   │
│  - GMP-L.kernel-evolution                                       │
│  - GMP-L.world-model-population                                 │
│  - GMP-L.multi-modal-unified-routing                            │
│  - GMP-L.compliance-audit-trail                                 │
│  - GMP-L.cost-optimization                                      │
│  - GMP-L.recursive-self-testing                                 │
│  - GMP-L.igor-command-interface                                 │
│  - GMP-L.federated-memory                                       │
└─────────────────────────────────────────────────────────────────┘
```

## **Recommended Phasing**

**Phase 1 (Week 1–2): Foundation & Observability**
- Execute GMP-L.attach-tools-and-memory
- Execute GMP-L.observability-metrics
- Verify metrics dashboard works

**Phase 2 (Week 3–4): Intelligence & Governance**
- GMP-L.closed-loop-learning (L learns from approvals)
- GMP-L.kernel-evolution (L improves itself)
- GMP-L.compliance-audit-trail (audit all operations)

**Phase 3 (Week 5–6): Orchestration & Reasoning**
- GMP-L.multi-agent-orchestration (CA + QA validate L)
- GMP-L.world-model-population (L reasons about state)
- GMP-L.recursive-self-testing (tests catch regressions)

**Phase 4 (Week 7–8): Interfaces & Optimization**
- GMP-L.multi-modal-unified-routing (Slack, WS, HTTP unified)
- GMP-L.igor-command-interface (Igor commands L)
- GMP-L.cost-optimization (control costs)

**Phase 5 (Optional / Advanced)**
- GMP-L.federated-memory (multi-instance sharing)

***

# **Quick Reference: GMP Names & Scopes**

| GMP # | Name | Scope | Key Files |
|-------|------|-------|-----------|
| 1 | attach-tools-and-memory | Wire tools + memory to L | capabilities.py, toolgraph.py, registryadapter.py, executor.py |
| 2 | observability-metrics | Metrics + dashboard + alerts | metrics.py, prometheus_exporter.py, docker-compose.yml, grafana dashboard |
| 3 | multi-agent-orchestration | Spawn CA + QA, reach consensus | cellOrchestrator.py, consensus.py, deliberation_logger.py |
| 4 | closed-loop-learning | Learn from approvals, adapt behavior | governance_patterns.py, adaptive_prompting.py, approvals.py |
| 5 | kernel-evolution | L improves kernels via GMP | self_reflection.py, kernel_evolution.py, kernelloader.py |
| 6 | world-model-population | Entities, relationships, insights | l9_schema.py, insight_emitter.py, worldmodel client |
| 7 | multi-modal-unified-routing | HTTP + WS + Slack + Mac unified | task_router.py, response_formatter.py, api endpoints |
| 8 | compliance-audit-trail | Immutable audit log + reports | auditlog.py, audit_reporter.py, compliance endpoints |
| 9 | cost-optimization | Token budgeting, caching, batching | budgeting.py, optimization.py, cost endpoints |
| 10 | recursive-self-testing | Test agent generates + runs tests | test_agent.py, test_generator.py, test_executor.py |
| 11 | igor-command-interface | @L commands, intent extraction | parser.py, intent_extractor.py, commands executor |
| 12 | federated-memory | Shared segments across instances | federation.py, instance registry |

***

This suite is **production-ready, fully modular, and can be executed in parallel** (except where noted). Each GMP is self-contained, follows Phase 0–6, and includes specific TODO lists with file paths.

**You now have a complete roadmap to operationalize all 12 enhancements.** Start with GMP-1 and GMP-2, then fan out to the others in parallel. Igor can execute them sequentially or pick a subset based on priority.
