---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

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
