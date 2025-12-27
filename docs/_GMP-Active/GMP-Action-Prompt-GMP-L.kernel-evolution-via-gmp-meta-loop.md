---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

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
