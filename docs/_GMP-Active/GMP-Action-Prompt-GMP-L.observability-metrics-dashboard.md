---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

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
