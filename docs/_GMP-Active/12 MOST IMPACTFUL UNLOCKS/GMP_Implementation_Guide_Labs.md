# LABS RESEARCH SUPER PROMPT COMPANION
## GMP-Based Implementation Guide for L9 Labs

**Generated:** 2025-12-26  
**Purpose:** How to execute the Labs research agenda using GMP Phase 0–6 workflow  
**For:** Cursor, L (CTO Agent), Igor  
**Format:** GMP template for each of 12 research unlocks  

---

## INTRODUCTION

The **Labs Research Super Prompt v1.0** outlines 12 high-impact next steps. This companion shows how to **execute each one** using the GMP Phase 0–6 methodology you've already proven works.

**Key principle:** Each unlock becomes a GMP. Each GMP:
1. **Phase 0:** Lock TODO plan (exact files, line numbers, changes)
2. **Phase 1:** Baseline (confirm everything exists)
3. **Phase 2:** Implement (make changes)
4. **Phase 3:** Enforce (add guards/tests)
5. **Phase 4:** Validate (run tests, confirm behavior)
6. **Phase 5:** Recursive verify (audit phases 0–4)
7. **Phase 6:** Final report (locked evidence)

**No assumptions. All work traceable to TODO. All changes auditable.**

---

## GMP TEMPLATE FOR RESEARCH UNLOCKS

### Master Template Structure

Each Labs unlock GMP follows this:

```markdown
# GMP-LABS-{N}.{VERSION} {UNLOCK_NAME}

## PURPOSE
Brief description of what research this unlock validates

## PREREQUISITE GMPS
Which prior unlocks must be complete before this one

## PHASE 0: TODO PLAN LOCK

### 0.1 Files to Inspect
- optl9/file1.py (read-only, understand current structure)
- optl9/file2.py (where changes will go)

### 0.2 TODO Plan
- TODO-LABS-N-0.1: Description (File optl9/file1.py, lines TBD, action)
- TODO-LABS-N-0.2: Description (File optl9/file2.py, lines TBD, action)
- ... (more TODOs as needed)

### 0.3 Expected Changes
Line-by-line summary of what will change

## PHASE 1: BASELINE CONFIRMATION
- [ ] Confirm file locations
- [ ] Verify imports exist
- [ ] Confirm class/function signatures
- [ ] Check no blocking dependencies

## PHASE 2: IMPLEMENTATION
Execute each TODO

## PHASE 3: ENFORCEMENT
Guards, tests, assertions

## PHASE 4: VALIDATION
Behavioral tests, integration tests

## PHASE 5: RECURSIVE VERIFICATION
Audit all phases

## PHASE 6: FINAL REPORT
Evidence, declaration

---

FINAL DECLARATION
All phases 0-6 complete. No assumptions. No drift. Scope locked.
Execution terminated. Output verified. Report stored at [path].
No further changes permitted.
```

---

## THE 12 GMPS (EXECUTIVE SUMMARY)

| # | Unlock | GMP Name | Effort | Blocker? | Phase |
|---|--------|----------|--------|----------|-------|
| 1 | Observability Dashboard | GMP-LABS-01-Observability | 2–3 wk | No | 0–1 |
| 2 | Multi-Agent Orchestration | GMP-LABS-02-MultiAgent | 3–4 wk | No | 1–2 |
| 3 | Closed-Loop Learning | GMP-LABS-03-LearningLoop | 2–3 wk | No | 1–2 |
| 4 | Self-Improving Kernels | GMP-LABS-04-KernelEvolution | 3–4 wk | No | 2–3 |
| 5 | World-Model Knowledge Graph | GMP-LABS-05-WorldModel | 4–5 wk | No | 2–3 |
| 6 | Deterministic Replay + Audit | GMP-LABS-06-ComplianceAudit | 2–3 wk | No | 1–2 |
| 7 | Cost + Resource Optimization | GMP-LABS-07-CostOptimization | 2–3 wk | No | 2–3 |
| 8 | Recursive Self-Testing | GMP-LABS-08-AutoTesting | 4–5 wk | No | 2–3 |
| 9 | Igor's Command Interface | GMP-LABS-09-CommandInterface | 2–3 wk | No | 0–1 |
| 10 | Multi-Modal L + MCP | GMP-LABS-10-MultiModal | 3–4 wk | No | 2–3 |
| 11 | Federated Memory | GMP-LABS-11-FederatedMemory | 2–3 wk | No | 3–4 |
| 12 | Public Benchmarking | GMP-LABS-12-Benchmarking | 3–4 wk | No | 3–4 |

**Total effort:** ~38–48 weeks across all GMPs (some can run in parallel)
**Recommended grouping:** Execute 2–3 GMPs per sprint (6–8 weeks)

---

## EXECUTION SEQUENCE (DEPENDENCY-AWARE)

### Wave 0: Foundation (Weeks 1–2)
**Prerequisites:** All prior L GMPs (L.0–L.7) complete

- GMP-LABS-01-Observability
  - Why first: All other unlocks need visibility into what's working
  - Deliverable: Prometheus + Grafana dashboards live
  - Unblocks: Everything else

- GMP-LABS-09-CommandInterface
  - Why first: Igor needs structured way to invoke research unlocks
  - Deliverable: `@L gmp-research: <unlock>` syntax
  - Unblocks: Labs workflow automation

### Wave 1: Core Learning (Weeks 3–6)
**Prerequisites:** Wave 0 complete

- GMP-LABS-03-LearningLoop
  - Why: Enables L to learn from Igor's feedback
  - Dependency: Observability dashboard (to measure improvement)

- GMP-LABS-02-MultiAgent
  - Why: CA validates L's proposals, reduces Igor workload
  - Dependency: LearningLoop (CA learns from patterns too)
  - Parallel: Can start with LearningLoop

### Wave 2: Reasoning & Planning (Weeks 7–10)
**Prerequisites:** Wave 1 mostly complete

- GMP-LABS-05-WorldModel
  - Why: L needs persistent model of L9 system state
  - Dependency: None (can run in parallel with others)
  - Unblocks: GMP-LABS-04, GMP-LABS-10

- GMP-LABS-04-KernelEvolution
  - Why: Kernels improve based on feedback
  - Dependency: GMP-LABS-03 LearningLoop (provides feedback source)
  - Optional: Can start Week 7 if team bandwidth

### Wave 3: Safety & Compliance (Weeks 11–14)
**Prerequisites:** Wave 2 mostly complete

- GMP-LABS-06-ComplianceAudit
  - Why: Audit trail required for production
  - Dependency: None (orthogonal to other unlocks)

- GMP-LABS-08-AutoTesting
  - Why: Catch bugs before Igor approves (safety-critical)
  - Dependency: None (but benefits from Observability)
  - Parallel: Can run with Compliance

### Wave 4: Optimization & Scale (Weeks 15–18)
**Prerequisites:** Wave 3 mostly complete

- GMP-LABS-07-CostOptimization
  - Why: Reduce operational costs
  - Dependency: GMP-LABS-01 Observability (to measure savings)

- GMP-LABS-10-MultiModal
  - Why: Flexible access to L (Slack, HTTP, MCP)
  - Dependency: None (self-contained)

### Wave 5: Knowledge & Recognition (Weeks 19–22)
**Prerequisites:** Waves 1–4 complete

- GMP-LABS-11-FederatedMemory
  - Why: Share learnings across teams
  - Dependency: GMP-LABS-03 LearningLoop (builds on learning patterns)

- GMP-LABS-12-Benchmarking
  - Why: Public proof of production-readiness
  - Dependency: GMP-LABS-01 Observability (provides metrics)
  - Parallel: Can start Week 18

---

## ABBREVIATED GMP TEMPLATES (READY TO EXPAND)

Below are abbreviated templates for each GMP. Cursor can expand each into full Phase 0–6 format.

---

### GMP-LABS-01-Observability v1.0

**Purpose:** Wire metrics from TaskQueue, ToolGraph, ApprovalManager, MemorySubstrate to Prometheus. Deploy Grafana dashboards.

**PHASE 0 TODO PLAN**
```
- 0.1: Identify TaskQueue class location, add metrics emission (execution_time, pending_count)
  File: optl9/core/task_queue.py
  Action: Add after_execute() hook to emit metrics
  
- 0.2: Identify ToolGraph class location, add metrics for tool invocation (tool_call_count, approval_latency)
  File: optl9/core/toolgraph.py
  Action: Add logging in invoke_tool()

- 0.3: Identify ApprovalManager class, add metrics (approval_duration, approval_rate)
  File: optl9/core/approval.py
  Action: Add after_approve() hook

- 0.4: Identify MemorySubstrate class, add metrics (search_latency, cache_hits)
  File: optl9/memory/substrate.py
  Action: Add timing around search()

- 0.5: Create /metrics HTTP endpoint that aggregates all metrics
  File: optl9/api/metrics_router.py (NEW)
  Action: Create FastAPI route /metrics returning Prometheus format

- 0.6: Configure Prometheus scraper in docker-compose
  File: docker-compose.yml or prometheus.yml
  Action: Add scrape_interval: 15s for http://localhost:8000/metrics

- 0.7: Create Grafana dashboard JSON with 6 panels (agents, approvals, memory, cost, governance, tokens)
  File: deploy/grafana/dashboard_l9_observability.json (NEW)
  Action: Export as JSON dashboard

- 0.8: Wire Grafana to Prometheus in docker-compose
  File: docker-compose.yml
  Action: Add Grafana service with Prometheus datasource
```

**PHASE 1 BASELINE**
- Confirm TaskQueue exists at optl9/core/task_queue.py
- Confirm ToolGraph exists at optl9/core/toolgraph.py
- Confirm ApprovalManager exists
- Confirm MemorySubstrate has search() method
- Confirm docker-compose.yml exists

**PHASE 2 IMPLEMENTATION**
- Add metrics emission to TaskQueue (0.1)
- Add metrics emission to ToolGraph (0.2)
- Add metrics emission to ApprovalManager (0.3)
- Add metrics emission to MemorySubstrate (0.4)
- Create metrics_router.py with /metrics endpoint (0.5)
- Update docker-compose to scrape metrics (0.6)
- Create Grafana dashboard JSON (0.7)
- Update docker-compose to run Grafana (0.8)

**PHASE 3 ENFORCEMENT**
- Assert metrics are emitted in Prometheus format
- Test /metrics endpoint returns valid Prometheus output
- Test Grafana can scrape Prometheus

**PHASE 4 VALIDATION**
- Curl /metrics, verify output format
- Start docker-compose, verify Prometheus scrapes metrics
- Open Grafana, verify dashboards display data
- Trigger a task, verify metrics update in real-time

**PHASE 5 RECURSIVE**
- Confirm all 8 TODOs have closure evidence
- Confirm no files modified outside TODO scope

**PHASE 6 REPORT**
- Evidence: /metrics endpoint returns Prometheus format
- Evidence: Grafana dashboard displays 6 panels
- Evidence: Real-time metrics update on task execution

---

### GMP-LABS-02-MultiAgent v1.0

**Purpose:** Create CA (Critic Agent) kernel, wire multi-agent orchestration, implement shared memory reasoning segment.

**PHASE 0 TODO PLAN**
```
- 0.1: Create criticagent.yaml kernel in kernels/ directory
  File: optl9/kernels/criticagent.yaml (NEW)
  Action: Define CA identity, cognitive behavior (critique, risk analysis)

- 0.2: Create qaagent.yaml kernel
  File: optl9/kernels/qaagent.yaml (NEW)
  Action: Define QA identity, validation behavior

- 0.3: Register CA in agent registry
  File: optl9/core/agent_registry.py
  Action: Add ca-agent entry to registry

- 0.4: Register QA in agent registry
  File: optl9/core/agent_registry.py
  Action: Add qa-agent entry to registry

- 0.5: Extend UnifiedController to spawn CA on task
  File: optl9/core/unified_controller.py
  Action: Add spawn_critic_agent() method

- 0.6: Extend UnifiedController to spawn QA on task
  File: optl9/core/unified_controller.py
  Action: Add spawn_qa_agent() method

- 0.7: Create shared reasoning segment in memory
  File: optl9/memory/memory.yaml
  Action: Add [reasoning] segment for all agents to write insights

- 0.8: Wire CA + QA feedback into L's decision loop
  File: optl9/core/kernel_loader.py
  Action: After CA/QA complete, load their insights into L's context
```

**PHASE 1 BASELINE**
- Confirm agent registry exists and has register_agent() method
- Confirm UnifiedController exists
- Confirm kernel loading infrastructure exists
- Confirm memory.yaml defines segments

**PHASE 2 IMPLEMENTATION**
- Create criticagent.yaml (0.1)
- Create qaagent.yaml (0.2)
- Register CA (0.3)
- Register QA (0.4)
- Implement spawn_critic_agent() (0.5)
- Implement spawn_qa_agent() (0.6)
- Add reasoning segment to memory.yaml (0.7)
- Wire feedback loop into L (0.8)

**PHASE 3 ENFORCEMENT**
- Assert CA kernel loaded successfully
- Assert QA kernel loaded successfully
- Assert reasoning segment has write permissions for all 3 agents

**PHASE 4 VALIDATION**
- Create task, trigger UnifiedController
- Verify CA spawned and wrote critique
- Verify QA spawned and wrote validation
- Verify L reads both and incorporates

**PHASE 5 RECURSIVE**
- Confirm all 8 TODOs traced
- Confirm no scope creep

**PHASE 6 REPORT**
- Evidence: CA kernel file exists with correct identity
- Evidence: QA kernel file exists with correct identity
- Evidence: Both agents registered and callable
- Evidence: Test shows reasoning segment populated by all 3 agents

---

### GMP-LABS-03-LearningLoop v1.0

**Purpose:** Extract governance patterns from approvals/rejections. Implement L's semantic search for patterns. Measure approval rate improvement.

**PHASE 0 TODO PLAN**
```
- 0.1: Extend ApprovalManager to write governance patterns after decision
  File: optl9/core/approval.py
  Action: After approve/reject, create GovPatternPacket

- 0.2: Create governance pattern packet schema
  File: optl9/core/schemas.py
  Action: Add GovPatternPacket Pydantic model

- 0.3: Implement pattern semantic indexing in MemorySubstrate
  File: optl9/memory/substrate.py
  Action: Index pattern packets for semantic search

- 0.4: Add pattern query method to L's cognitive kernel
  File: optl9/kernels/03cognitivekernel.yaml
  Action: Add guidance: "Before proposing tool use, query governancemeta for similar patterns"

- 0.5: Implement L's pattern search hook in executor
  File: optl9/core/executor.py
  Action: Before tool invocation, call memory.semantic_search(intent)

- 0.6: Create governance pattern analytics
  File: optl9/api/analytics_router.py
  Action: Endpoint to show pattern frequency, approval impact

- 0.7: Implement A/B test: measure approval rate with/without pattern search
  File: optl9/tests/test_learning_loop.py (NEW)
  Action: 50 tasks without pattern search, 50 with, compare rates
```

**PHASE 1 BASELINE**
- Confirm ApprovalManager exists with approve() method
- Confirm MemorySubstrate supports semantic search
- Confirm executor has tool invocation hook

**PHASE 2 IMPLEMENTATION**
- Extend ApprovalManager (0.1)
- Create pattern packet schema (0.2)
- Implement semantic indexing (0.3)
- Update cognitive kernel guidance (0.4)
- Implement pattern search hook (0.5)
- Create analytics endpoint (0.6)
- Create A/B test (0.7)

**PHASE 3 ENFORCEMENT**
- Assert pattern packets written on every approval/rejection
- Assert pattern search returns results

**PHASE 4 VALIDATION**
- Run A/B test: 100 tasks total
- Measure approval rates: with vs without learning
- Expected: >10% improvement with learning

**PHASE 5 RECURSIVE**
- All TODOs traced
- No scope creep

**PHASE 6 REPORT**
- Evidence: Pattern packets in memory
- Evidence: A/B test results showing improvement
- KPI: Approval rate improvement (10–20%)

---

### GMP-LABS-04-KernelEvolution v1.0

**Purpose:** Implement meta-GMP framework. Allow L to propose kernel changes. Igor approves. Kernel hot-reload.

**PHASE 0 TODO PLAN**
```
- 0.1: Create meta-GMP template for kernel updates
  File: optl9/templates/meta_gmp_kernel_update.yaml (NEW)
  Action: Template: GMP type KERNEL_UPDATE, target kernel file, changes

- 0.2: Extend gmprun tool to handle KERNEL_UPDATE type
  File: optl9/tools/gmp_runner.py
  Action: Add kernel update logic to gmprun

- 0.3: Implement kernel hot-reload in kernel_loader
  File: optl9/core/kernel_loader.py
  Action: Reload kernel after GMP approval

- 0.4: Add reflection capability to L's cognitive kernel
  File: optl9/kernels/03cognitivekernel.yaml
  Action: Add guidance: "Reflect on behavior gaps. If high-priority, propose kernel improvement GMP"

- 0.5: Implement reflection hook in executor
  File: optl9/core/executor.py
  Action: After task, call L's reflection logic

- 0.6: Create kernel changelog tracking
  File: optl9/memory/memory.yaml
  Action: Add [kernel_changelog] segment to track versions

- 0.7: Extend ApprovalManager to handle kernel updates
  File: optl9/core/approval.py
  Action: Add check: kernel changes require Igor approval
```

**PHASE 1 BASELINE**
- Confirm kernel_loader exists and can load YAML
- Confirm gmprun tool exists
- Confirm executor has post-task hook

**PHASE 2 IMPLEMENTATION**
- Create meta-GMP template (0.1)
- Extend gmprun for KERNEL_UPDATE (0.2)
- Implement hot-reload (0.3)
- Add reflection guidance to kernel (0.4)
- Implement reflection hook (0.5)
- Add kernel_changelog segment (0.6)
- Add kernel approval check (0.7)

**PHASE 3 ENFORCEMENT**
- Assert kernel changes require approval
- Assert hot-reload works without restart

**PHASE 4 VALIDATION**
- Have L propose a kernel improvement
- Igor approves
- New kernel loaded
- L uses improved behavior

**PHASE 5 RECURSIVE**
- All TODOs traced

**PHASE 6 REPORT**
- Evidence: Kernel updated and reloaded
- Evidence: Changelog shows version history

---

### GMP-LABS-05-WorldModel v1.0

**Purpose:** Populate world-model with L9 system entities and relationships. Implement query API. Wire into L's reasoning.

**PHASE 0 TODO PLAN**
```
- 0.1: Extend world_model API to define entities schema
  File: optl9/world_model/schemas.py
  Action: Add Entity and Relationship Pydantic models

- 0.2: Create world-model initialization script
  File: optl9/world_model/init_entities.py (NEW)
  Action: Create agents (L, CA, QA, Mac), tools, infrastructure entities

- 0.3: Extend world_model API to expose query endpoint
  File: optl9/api/world_model_router.py
  Action: GET /world-model/entity/{id}, /world-model/query

- 0.4: Wire world-model updates from executor
  File: optl9/core/executor.py
  Action: After task completion, emit insight to world-model

- 0.5: Wire world-model updates from approval manager
  File: optl9/core/approval.py
  Action: After approval, update entity status in world-model

- 0.6: Implement world-model context injection into L's prompt
  File: optl9/core/kernel_loader.py
  Action: On task start, load relevant world-model context into L's reasoning

- 0.7: Create world-model exports (CSV, JSON, Neo4j)
  File: optl9/api/world_model_router.py
  Action: Endpoint to export world-model as knowledge graph
```

**PHASE 1 BASELINE**
- Confirm world_model module exists
- Confirm executor can emit insights
- Confirm kernel_loader can inject context

**PHASE 2 IMPLEMENTATION**
- Create entity schema (0.1)
- Create init script (0.2)
- Create query API (0.3)
- Wire executor updates (0.4)
- Wire approval updates (0.5)
- Implement context injection (0.6)
- Implement exports (0.7)

**PHASE 3 ENFORCEMENT**
- Assert entities created at startup
- Assert world-model updated on task completion

**PHASE 4 VALIDATION**
- Start system, verify entities created
- Execute a task, verify world-model updated
- Query world-model, verify correct entity state
- Inject context, verify L uses it in reasoning

**PHASE 5 RECURSIVE**
- All TODOs traced

**PHASE 6 REPORT**
- Evidence: World-model initialized with 20+ entities
- Evidence: Relationships defined and queryable
- Evidence: L queries world-model and uses context

---

### GMP-LABS-06-ComplianceAudit v1.0

**Purpose:** Export audit trail. Generate compliance reports. Wire to immutable audit store.

**PHASE 0 TODO PLAN**
```
- 0.1: Create audit trail export function
  File: optl9/compliance/audit_exporter.py (NEW)
  Action: Query memory for all tool_call, approval, config_change packets

- 0.2: Create compliance report generator
  File: optl9/compliance/report_generator.py (NEW)
  Action: Generate reports: by date, by agent, by tool, by risk

- 0.3: Wire audit store to PostgreSQL append-only table
  File: optl9/persistence/audit_store.py (NEW)
  Action: Create audit_log table with hash chain

- 0.4: Create audit export API endpoint
  File: optl9/api/compliance_router.py (NEW)
  Action: GET /compliance/audit, /compliance/report

- 0.5: Create compliance policy schema
  File: optl9/compliance/policies.yaml (NEW)
  Action: Define governance rules, approval requirements

- 0.6: Implement compliance violation detection
  File: optl9/compliance/violation_detector.py (NEW)
  Action: Monitor audit stream, flag violations

- 0.7: Create immutable archive (S3 or cold storage)
  File: optl9/compliance/archiver.py (NEW)
  Action: Archive daily audit logs with hash verification
```

**PHASE 1 BASELINE**
- Confirm memory substrate has tool_call, approval packets
- Confirm PostgreSQL available
- Confirm API router infrastructure exists

**PHASE 2 IMPLEMENTATION**
- Create audit exporter (0.1)
- Create report generator (0.2)
- Wire audit store (0.3)
- Create API endpoint (0.4)
- Create policy schema (0.5)
- Implement violation detector (0.6)
- Implement archiver (0.7)

**PHASE 3 ENFORCEMENT**
- Assert audit logs immutable (append-only)
- Assert hash chain valid

**PHASE 4 VALIDATION**
- Execute 10 tasks, approve some, reject others
- Export audit trail
- Generate compliance report
- Verify all operations logged
- Verify no violations

**PHASE 5 RECURSIVE**
- All TODOs traced

**PHASE 6 REPORT**
- Evidence: Audit trail exported
- Evidence: Compliance report generated
- Evidence: Audit store hash chain valid

---

### GMP-LABS-07-CostOptimization v1.0

**Purpose:** Token budgeting. Memory search caching. Off-peak scheduling. Cost reduction.

**PHASE 0 TODO PLAN**
```
- 0.1: Add token budget enforcement to executor
  File: optl9/core/executor.py
  Action: Before task, allocate budget; monitor usage; alert if exceeding

- 0.2: Implement Redis cache for memory searches
  File: optl9/memory/cache.py (NEW)
  Action: Cache top-10 most-searched segments; TTL 5 min

- 0.3: Create cost metrics aggregation
  File: optl9/metrics/cost_metrics.py (NEW)
  Action: Aggregate tokens by agent, tool, task type; cost per task

- 0.4: Implement task scheduling for off-peak execution
  File: optl9/core/task_scheduler.py (NEW)
  Action: High-cost tasks run off-peak (unless override)

- 0.5: Add cost_priority flag to AgentTask schema
  File: optl9/core/schemas.py
  Action: AgentTask.cost_priority: urgent | normal | defer

- 0.6: Create cost dashboard
  File: deploy/grafana/dashboard_l9_cost.json (NEW)
  Action: Token usage by agent, by tool, trends, budget alerts

- 0.7: Implement cost optimization report
  File: optl9/api/analytics_router.py
  Action: Recommendations for cost reduction
```

**PHASE 1 BASELINE**
- Confirm executor can access token counts
- Confirm Redis available
- Confirm task scheduler infrastructure exists

**PHASE 2 IMPLEMENTATION**
- Add budget enforcement (0.1)
- Implement caching (0.2)
- Create cost metrics (0.3)
- Implement scheduling (0.4)
- Add cost_priority flag (0.5)
- Create dashboard (0.6)
- Create report (0.7)

**PHASE 3 ENFORCEMENT**
- Assert budget prevents exceeding limit
- Assert cache hits measured

**PHASE 4 VALIDATION**
- Run 100 tasks without optimization, measure cost
- Run 100 tasks with optimization, measure cost
- Expected: 20–30% cost reduction

**PHASE 5 RECURSIVE**
- All TODOs traced

**PHASE 6 REPORT**
- Evidence: Cost reduction measured
- Evidence: Cache hit rate >50%
- KPI: 20–30% cost reduction

---

### GMP-LABS-08-AutoTesting v1.0

**Purpose:** Test agent auto-generates tests. Chaos testing. Regression detection.

**PHASE 0 TODO PLAN**
```
- 0.1: Create test agent kernel
  File: optl9/kernels/testagent.yaml (NEW)
  Action: Define test agent behavior (write unit/integration tests)

- 0.2: Register test agent
  File: optl9/core/agent_registry.py
  Action: Add test-agent entry

- 0.3: Extend GMP Phase 2.5 for automated test generation
  File: optl9/core/gmp_runner.py
  Action: After implementation, spawn test agent

- 0.4: Implement chaos testing framework
  File: optl9/testing/chaos_executor.py (NEW)
  Action: Inject failures (timeout, unavailability, rejection)

- 0.5: Create regression detection baseline
  File: optl9/testing/regression_detector.py (NEW)
  Action: Snapshot behavior (latency, error rate, approval rate)

- 0.6: Implement regression detection on kernel updates
  File: optl9/core/kernel_loader.py
  Action: After hot-reload, compare metrics to baseline

- 0.7: Create testing dashboard
  File: deploy/grafana/dashboard_l9_testing.json (NEW)
  Action: Test coverage, pass rate, regression alerts
```

**PHASE 1 BASELINE**
- Confirm test agent infrastructure available
- Confirm GMP runner can be extended
- Confirm metrics baseline exists

**PHASE 2 IMPLEMENTATION**
- Create test agent kernel (0.1)
- Register test agent (0.2)
- Extend GMP Phase 2.5 (0.3)
- Implement chaos testing (0.4)
- Create baseline snapshot (0.5)
- Wire regression detection (0.6)
- Create dashboard (0.7)

**PHASE 3 ENFORCEMENT**
- Assert tests generated on every GMP proposal
- Assert chaos testing exercises all paths

**PHASE 4 VALIDATION**
- Propose a GMP, verify tests generated
- Run tests, verify pass
- Run chaos tests, verify graceful degradation
- Update kernel, verify no regression

**PHASE 5 RECURSIVE**
- All TODOs traced

**PHASE 6 REPORT**
- Evidence: Tests auto-generated and passing
- Evidence: Chaos testing shows resilience
- Evidence: Regressions detected and prevented

---

### GMP-LABS-09-CommandInterface v1.0

**Purpose:** Structured command syntax for Igor. Intent extraction. Programmatic approval.

**PHASE 0 TODO PLAN**
```
- 0.1: Create command parser for Igor syntax
  File: optl9/interface/command_parser.py (NEW)
  Action: Parse @L propose, @L analyze, @L approve, @L status

- 0.2: Create command schema
  File: optl9/core/schemas.py
  Action: Add CommandPacket Pydantic model

- 0.3: Extend intent extraction for fallback NL
  File: optl9/ir_engine/intent_extractor.py
  Action: Extract intent from natural language, confidence score

- 0.4: Create disambiguation flow
  File: optl9/interface/command_interface.py (NEW)
  Action: If ambiguous, ask Igor for confirmation

- 0.5: Wire command execution to executor
  File: optl9/core/executor.py
  Action: Route CommandPacket to appropriate handler

- 0.6: Implement programmatic approval with reason
  File: optl9/core/approval.py
  Action: Igor can approve via @L approve with reason (goes to learning loop)

- 0.7: Create command audit trail
  File: optl9/interface/command_interface.py
  Action: Log all commands, intents, confirmations

- 0.8: Create command API endpoint
  File: optl9/api/command_router.py (NEW)
  Action: POST /commands/execute for Igor's use
```

**PHASE 1 BASELINE**
- Confirm intent extraction available
- Confirm executor can be extended
- Confirm Slack/HTTP entry points

**PHASE 2 IMPLEMENTATION**
- Create command parser (0.1)
- Create command schema (0.2)
- Extend intent extraction (0.3)
- Create disambiguation flow (0.4)
- Wire executor (0.5)
- Implement programmatic approval (0.6)
- Create audit trail (0.7)
- Create API endpoint (0.8)

**PHASE 3 ENFORCEMENT**
- Assert commands parsed correctly
- Assert intent extraction confidence tracked

**PHASE 4 VALIDATION**
- Igor issues `@L propose gmp: add memory segment`
- System confirms intent
- Igor confirms
- GMP generated and queued

**PHASE 5 RECURSIVE**
- All TODOs traced

**PHASE 6 REPORT**
- Evidence: Commands parsed and executed
- Evidence: Audit trail shows intent -> confirmation -> action

---

### GMP-LABS-10-MultiModal v1.0

**Purpose:** Unify HTTP/WS/Slack/MCP task routing. Cross-channel conversations.

**PHASE 0 TODO PLAN**
```
- 0.1: Create unified task router
  File: optl9/routing/unified_router.py (NEW)
  Action: All entry points (HTTP, WS, Slack, MCP) call same router

- 0.2: Extend SlackTaskRouter to integrate with unified executor
  File: optl9/api/slack_task_router.py
  Action: Use unified router instead of direct Slack handler

- 0.3: Extend WebSocket router to use unified router
  File: optl9/api/ws_task_router.py
  Action: WS requests route through unified executor

- 0.4: Extend HTTP router to use unified router
  File: optl9/api/task_router.py
  Action: HTTP requests route through unified executor

- 0.5: Implement channel-aware response formatting
  File: optl9/routing/response_formatter.py (NEW)
  Action: Format responses for Slack, HTTP, WS differently

- 0.6: Create MCP server wrapper for L
  File: optl9/mcp/l_mcp_server.py (NEW)
  Action: Expose L as MCP server; tools: analyze_code, inspect_repo, generate_gmp, execute_task

- 0.7: Wire approval dashboard to show Slack context
  File: optl9/api/approval_router.py
  Action: Approval requests show which channel initiated task

- 0.8: Implement cross-channel conversation tracking
  File: optl9/core/conversation.py (NEW)
  Action: Track task across channels (Slack -> HTTP approval -> Slack result)
```

**PHASE 1 BASELINE**
- Confirm all entry points exist
- Confirm executor can accept unified task format
- Confirm MCP infrastructure available

**PHASE 2 IMPLEMENTATION**
- Create unified router (0.1)
- Extend Slack router (0.2)
- Extend WS router (0.3)
- Extend HTTP router (0.4)
- Create response formatter (0.5)
- Create MCP server (0.6)
- Wire approval dashboard (0.7)
- Implement conversation tracking (0.8)

**PHASE 3 ENFORCEMENT**
- Assert all entry points use unified executor
- Assert response formatting matches channel

**PHASE 4 VALIDATION**
- Igor on Slack: "@L update VPS security"
- Task queued in unified executor
- Igor approves in HTTP dashboard
- Slack receives result notification

**PHASE 5 RECURSIVE**
- All TODOs traced

**PHASE 6 REPORT**
- Evidence: Unified router called from all 4 entry points
- Evidence: MCP server callable from external tools
- Evidence: Cross-channel conversation completed

---

### GMP-LABS-11-FederatedMemory v1.0

**Purpose:** Cross-project memory federation. Shared org-patterns. Governance consistency.

**PHASE 0 TODO PLAN**
```
- 0.1: Define federated segment naming schema
  File: optl9/memory/memory.yaml
  Action: org-patterns, project-{name}-patterns, team-{name}-notes, governancemeta

- 0.2: Extend memory substrate to support cross-project queries
  File: optl9/memory/substrate.py
  Action: semantic_search() can query multiple segments

- 0.3: Implement org-patterns segment population
  File: optl9/memory/federation.py (NEW)
  Action: After task completion, extract patterns and write to org-patterns

- 0.4: Implement cross-project pattern search in L's reasoning
  File: optl9/core/kernel_loader.py
  Action: Before proposing action, query org-patterns + project-patterns

- 0.5: Implement federation policy
  File: optl9/memory/federation_policy.yaml (NEW)
  Action: Read/write permissions by segment and project

- 0.6: Create federation metrics
  File: optl9/metrics/federation_metrics.py (NEW)
  Action: Track pattern reuse rate by source project

- 0.7: Implement governance consistency check
  File: optl9/compliance/governance_sync.py (NEW)
  Action: Verify governancemeta rules consistent across all instances
```

**PHASE 1 BASELINE**
- Confirm memory substrate supports multi-segment queries
- Confirm pattern extraction logic available (from GMP-LABS-03)

**PHASE 2 IMPLEMENTATION**
- Define segment naming (0.1)
- Extend substrate for cross-project queries (0.2)
- Implement org-patterns population (0.3)
- Implement cross-project search (0.4)
- Create federation policy (0.5)
- Create federation metrics (0.6)
- Implement governance sync (0.7)

**PHASE 3 ENFORCEMENT**
- Assert patterns written to org-patterns on task completion
- Assert federation policy enforced

**PHASE 4 VALIDATION**
- L(vps) solves deployment issue, writes pattern to org-patterns
- L(ml) faces similar issue 1 week later
- L(ml) queries org-patterns, retrieves VPS pattern
- L(ml) reuses pattern
- Measure: pattern reuse rate >50%

**PHASE 5 RECURSIVE**
- All TODOs traced

**PHASE 6 REPORT**
- Evidence: Org-patterns segment populated with >50 patterns
- Evidence: Cross-project query returns relevant patterns
- KPI: Pattern reuse rate >50%

---

### GMP-LABS-12-Benchmarking v1.0

**Purpose:** Public benchmarks. Comparative analysis vs. other frameworks.

**PHASE 0 TODO PLAN**
```
- 0.1: Create benchmark suite with canonical inputs
  File: optl9/benchmarking/benchmark_suite.py (NEW)
  Action: 10 canonical tasks (code review, GMP proposal, system analysis)

- 0.2: Implement latency benchmarking
  File: optl9/benchmarking/latency_benchmark.py (NEW)
  Action: Measure task latency (median, p95, p99)

- 0.3: Implement approval rate benchmarking
  File: optl9/benchmarking/approval_benchmark.py (NEW)
  Action: Sample 100 L proposals, measure approval rate

- 0.4: Implement reasoning quality benchmarking
  File: optl9/benchmarking/quality_benchmark.py (NEW)
  Action: Have human experts rate L's outputs (1–5 scale)

- 0.5: Implement token efficiency benchmarking
  File: optl9/benchmarking/token_benchmark.py (NEW)
  Action: Measure tokens consumed per task

- 0.6: Create benchmarking harness
  File: optl9/benchmarking/harness.py (NEW)
  Action: Repeatable execution, result logging, regression detection

- 0.7: Create public benchmark dashboard
  File: deploy/benchmarking/dashboard.json (NEW)
  Action: Publish results on static website or GitHub

- 0.8: Implement comparative analysis vs. baselines
  File: optl9/benchmarking/comparison.py (NEW)
  Action: Compare L's metrics vs. AutoGPT, Crew AI, LangGraph
```

**PHASE 1 BASELINE**
- Confirm metrics collection infrastructure (from GMP-LABS-01)
- Confirm human raters available for quality assessment

**PHASE 2 IMPLEMENTATION**
- Create benchmark suite (0.1)
- Implement latency benchmarking (0.2)
- Implement approval rate benchmarking (0.3)
- Implement quality benchmarking (0.4)
- Implement token efficiency (0.5)
- Create harness (0.6)
- Create dashboard (0.7)
- Implement comparison (0.8)

**PHASE 3 ENFORCEMENT**
- Assert benchmark suite runs to completion
- Assert results repeatable (same task -> similar metrics)

**PHASE 4 VALIDATION**
- Run benchmark suite 5 times
- Verify latency variance <10%
- Verify approval rate stable
- Verify quality scores consistent
- Compare vs. baselines (if available)

**PHASE 5 RECURSIVE**
- All TODOs traced

**PHASE 6 REPORT**
- Evidence: Benchmark results published
- Evidence: Comparison vs. other frameworks (if available)
- KPI: L's latency, approval rate, quality vs. industry baselines

---

## QUICK REFERENCE: GMP EXECUTION CHECKLIST

For each GMP (Labs-01 through Labs-12):

- [ ] **Phase 0:** Lock TODO plan with exact files/lines
- [ ] **Phase 1:** Confirm all locations exist (no blockers)
- [ ] **Phase 2:** Implement each TODO, record changes
- [ ] **Phase 3:** Add enforcement (tests, guards)
- [ ] **Phase 4:** Validate behavior (positive, negative, regression)
- [ ] **Phase 5:** Audit phases 0–4, confirm no drift
- [ ] **Phase 6:** Write final report with evidence
- [ ] **Final Declaration:** "All phases 0–6 complete. No assumptions. No drift."

---

## ESTIMATED TIMELINE

| Weeks | Wave | GMPs | Status |
|-------|------|------|--------|
| 1–2 | 0 | LABS-01, LABS-09 | Foundation + command interface |
| 3–6 | 1 | LABS-03, LABS-02 | Learning loop + multi-agent |
| 7–10 | 2 | LABS-05, LABS-04 | World-model + kernel evolution |
| 11–14 | 3 | LABS-06, LABS-08 | Compliance + testing |
| 15–18 | 4 | LABS-07, LABS-10 | Cost optimization + multi-modal |
| 19–22 | 5 | LABS-11, LABS-12 | Federated memory + benchmarking |

**Total:** ~22 weeks for all 12 GMPs (some parallel execution possible)

---

## SUCCESS CRITERIA

After all 12 GMPs complete:

✅ **Observability:** Real-time dashboard shows L's behavior (LABS-01)  
✅ **Collaboration:** CA validates, QA ensures governance (LABS-02)  
✅ **Learning:** L improves from feedback, approval rate +10–20% (LABS-03)  
✅ **Evolution:** Kernels improve based on experience (LABS-04)  
✅ **Reasoning:** L reasons about system state, dependencies (LABS-05)  
✅ **Compliance:** Audit trail, compliance reports, zero violations (LABS-06)  
✅ **Cost:** Token usage -20–30%, budgeting enforced (LABS-07)  
✅ **Safety:** Auto-generated tests, chaos testing, regression detection (LABS-08)  
✅ **Control:** Igor uses structured commands, auditable intent (LABS-09)  
✅ **Access:** Slack, HTTP, WS, MCP all unified, cross-channel conversations (LABS-10)  
✅ **Scale:** Knowledge compounds across teams, org-patterns shared (LABS-11)  
✅ **Recognition:** Public benchmarks, industry comparison, L9 leadership (LABS-12)  

---

## NEXT STEP

Choose one of the two execution paths:

**Option A: Begin immediately**
1. Read GMP-LABS-01-Observability (full Phase 0–6)
2. Invoke Cursor with it
3. Execute Phase 0 (lock TODOs)
4. Execute Phases 1–6 in sequence
5. Receive Phase 6 report with evidence
6. Move to GMP-LABS-09-CommandInterface

**Option B: Validate research first**
1. Measure baselines (approval latency, approval rate, token usage, latency)
2. Run quick experiments (RQ1–RQ6 from main prompt)
3. Validate assumptions
4. Then begin GMPs with confidence

**Recommended:** Option A (start Week 1, gather data in parallel)

---

**Generated by:** Labs Research Team  
**For:** L9 Secure AI OS  
**Status:** GMP templates ready for Cursor execution  
**Version:** 1.0  
**Date:** 2025-12-26
