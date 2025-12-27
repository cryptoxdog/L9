---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

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
