---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

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
