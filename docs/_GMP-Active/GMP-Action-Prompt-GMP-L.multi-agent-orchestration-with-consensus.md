---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

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
