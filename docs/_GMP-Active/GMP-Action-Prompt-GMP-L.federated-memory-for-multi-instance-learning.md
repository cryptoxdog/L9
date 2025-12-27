---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

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
