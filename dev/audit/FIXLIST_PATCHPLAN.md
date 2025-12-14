# L9 Audit Fixlist & Patch Plan

Remaining issues and recommended fixes, in priority order.

---

## Status: All Blockers Resolved

The following blockers were fixed during this audit:

| # | Issue | Fix Applied | Status |
|---|-------|-------------|--------|
| 1 | `langgraph/` shadows library | Renamed to `l9_langgraph/` | FIXED |
| 2 | `runtime/` module missing | Created with websocket_orchestrator, task_queue | FIXED |
| 3 | `entrypoints.txt` phantom paths | Removed non-existent entries | FIXED |
| 4 | `checkpoint_id` reserved name | Renamed to `saved_checkpoint_id` | FIXED |

---

## Remaining Recommendations (Non-Blocking)

### Priority 1: Wire Unused Modules

**Issue:** `agents/` module has 7 agent classes that are never imported.

**Files:**
- `agents/base_agent.py`
- `agents/architect_agent_a.py`
- `agents/architect_agent_b.py`
- `agents/coder_agent_a.py`
- `agents/coder_agent_b.py`
- `agents/qa_agent.py`
- `agents/reflection_agent.py`

**Options:**
1. **Wire to orchestrators** - Import and use in `orchestrators/` for multi-agent workflows
2. **Mark as Phase 3** - Add comment in `agents/__init__.py` noting these are planned
3. **Quarantine** - Move to `dev/_quarantine/agents/` if truly unused

**Recommended Fix:**
```python
# In orchestrators/research_swarm/orchestrator.py
from agents import ArchitectAgentA, CoderAgentA, QAAgent
```

---

### Priority 2: Implement or Remove telemetry/

**Issue:** `telemetry/` is an empty stub with only `__init__.py`.

**Options:**
1. **Implement** - Add metrics, tracing, logging aggregation
2. **Remove** - Delete the empty directory

**Recommended Fix:** If not needed in next 2 sprints, delete.

---

### Priority 3: Production Task Queue

**Issue:** `runtime/task_queue.py` is in-memory only. Tasks are lost on restart.

**Current:** In-memory deque with priority ordering.

**Production Fix:**
```python
# Replace with Redis-backed queue
# Option A: Use RQ (Redis Queue)
# Option B: Use Celery
# Option C: Use AWS SQS
```

---

### Priority 4: Wire l9_langgraph/PacketNodeAdapter

**Issue:** `l9_langgraph/packet_node_adapter.py` has `PacketNodeAdapter` class but it's never imported.

**Purpose:** Wraps LangGraph nodes to emit packets to memory.

**Recommended Fix:**
```python
# In memory/substrate_graph.py or a dedicated integration module
from l9_langgraph import PacketNodeAdapter
```

---

## Verification Commands

After making any fixes, run:

```bash
# Compile check
/Users/ib-mac/Projects/L9/venv/bin/python -m compileall -q .

# Smoke test
/Users/ib-mac/Projects/L9/venv/bin/python dev/audit/smoke_test.py

# Import chain test
/Users/ib-mac/Projects/L9/venv/bin/python -c "from api.server import app"
```

---

## Quarantine Procedure

If you need to quarantine a module:

```bash
# 1. Create quarantine directory
mkdir -p dev/_quarantine

# 2. Move the module
mv <module_dir> dev/_quarantine/

# 3. Create README
echo "Quarantined on $(date): <reason>" > dev/_quarantine/<module_dir>/README_QUARANTINE.md

# 4. Update .gitignore if needed (already includes dev/_quarantine/)
```

---

*End of Fixlist*

