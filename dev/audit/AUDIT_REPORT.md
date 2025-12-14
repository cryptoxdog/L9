# L9 Full-Repo Audit Report

**Date:** 2025-12-13  
**Auditor:** L (CTO Audit Mode)  
**Python Version:** 3.12.12  
**Scope:** Production-grade, no-surprises audit

---

## Executive Summary

| Metric | Status |
|--------|--------|
| compileall | PASS |
| Smoke Tests | 10/10 PASS |
| Blockers Fixed | 3 |
| Structural Risks | 2 (documented) |
| Quarantined Paths | 0 |

---

## 1. BLOCKERS FIXED (Critical)

### 1.1 Circular Import: langgraph/ shadowing library

**Problem:** Local `langgraph/` directory shadowed the `langgraph` pip package, causing circular import:
```
memory.substrate_graph -> langgraph.graph (local) -> langgraph/__init__.py 
-> langgraph.packet_node_adapter -> memory.substrate_service -> memory.substrate_graph
```

**Fix:** Renamed `langgraph/` to `l9_langgraph/` and updated internal imports.

**Files Changed:**
- `langgraph/` -> `l9_langgraph/` (directory rename)
- `l9_langgraph/__init__.py` (updated import path)

---

### 1.2 Missing runtime/ Module

**Problem:** `api/server.py` and `orchestration/unified_controller.py` imported from `runtime.websocket_orchestrator` but the module didn't exist.

**Fix:** Created `runtime/` directory with:
- `runtime/__init__.py`
- `runtime/websocket_orchestrator.py` - WebSocket connection manager
- `runtime/task_queue.py` - In-memory priority task queue

---

### 1.3 Phantom Entrypoints

**Problem:** `entrypoints.txt` listed paths that don't exist:
- `l9/agent/main.py`
- `l9/api/server.py`
- `l9/l9/agent/main.py`
- `l9/l9/server/main.py`
- `l9/server/main.py`

**Fix:** Removed non-existent paths. Only canonical entrypoint remains:
- `api/server.py`

---

### 1.4 LangGraph Reserved Channel Name

**Problem:** `SubstrateGraphState.checkpoint_id` used a reserved LangGraph channel name, causing runtime error.

**Fix:** Renamed to `saved_checkpoint_id` in `memory/substrate_graph.py`.

---

## 2. STRUCTURAL RISKS (Non-Blocking)

### 2.1 Unwired Modules (Created But Not Called)

The following modules exist but have NO external imports from L9 code:

| Module | Status | Recommendation |
|--------|--------|----------------|
| `agents/` | 7 agent classes | Wire to orchestrators or mark as Phase 3 |
| `telemetry/` | Empty stub | Either implement or remove |
| `l9_langgraph/` | PacketNodeAdapter only | Wire to memory pipeline or mark optional |

These are NOT blockers but represent potential dead code.

### 2.2 Case Sensitivity Note

Workspace path shows as `/Users/ib-mac/Projects/L9` (capital L9) but Python CWD shows `/Users/ib-mac/Projects/l9` (lowercase). On macOS HFS+ this is the same directory, but could cause issues on case-sensitive filesystems (Linux VPS).

---

## 3. CONTENT SCAN RESULTS

### 3.1 Emoji/Non-ASCII

| Check | Result |
|-------|--------|
| Emoji in .py files | NONE FOUND |
| Non-ASCII bytes literals | NONE FOUND |
| Non-ASCII in strings | NONE FOUND (L9 code) |

### 3.2 Editor Junk

| Check | Result |
|-------|--------|
| .DS_Store files | Present but in .gitignore |
| ._* files | NONE |
| __MACOSX/ | NONE |
| .cursor/, .dora/ | Present but in .gitignore |

---

## 4. STARTUP WIRING VERIFICATION

### 4.1 Migrations

- Location: `migrations/*.sql` (7 files)
- Wired: YES - `api/server.py` lifespan calls `run_migrations()` on startup
- Idempotent: YES - tracks applied in `schema_migrations` table

### 4.2 Memory Ingestion

- Canonical entrypoint: `memory.ingestion.ingest_packet()`
- Wired at:
  - `api/server.py` WebSocket handler (line 211)
  - `api/memory/router.py` REST endpoint (line 73)

### 4.3 WebSocket Orchestrator

- Singleton: `runtime.websocket_orchestrator.ws_orchestrator`
- Wired at: `api/server.py` (line 143)

---

## 5. ENV KEYS CONTRACT

Required environment variables by subsystem:

### Core (Required)
```
MEMORY_DSN          # or DATABASE_URL - Postgres connection string
OPENAI_API_KEY      # LLM and embeddings
```

### Memory Subsystem
```
EMBEDDING_PROVIDER  # "openai" or "stub" (default: "stub")
EMBEDDING_MODEL     # e.g., "text-embedding-3-large"
```

### Optional Integrations
```
SLACK_BOT_TOKEN     # Slack integration
SLACK_SIGNING_SECRET
SLACK_APP_ENABLED   # "true" to enable

TWILIO_ACCOUNT_SID  # Twilio/WhatsApp
TWILIO_AUTH_TOKEN
TWILIO_SMS_NUMBER
TWILIO_WHATSAPP_FROM
TWILIO_WHATSAPP_NUMBER

WABA_ACCESS_TOKEN   # WhatsApp Business API
WABA_PHONE_NUMBER_ID
WABA_BUSINESS_ACCOUNT_ID
WABA_WEBHOOK_VERIFY_TOKEN

MAC_AGENT_ENABLED   # Mac agent features
LOCAL_DEV           # Development mode
```

---

## 6. FIXES PERFORMED

| File | Change | Reason |
|------|--------|--------|
| `langgraph/` -> `l9_langgraph/` | Directory rename | Unblock library import |
| `l9_langgraph/__init__.py` | Updated import | Fix internal reference |
| `entrypoints.txt` | Removed phantom paths | Clean up false references |
| `runtime/__init__.py` | Created | Provide module root |
| `runtime/websocket_orchestrator.py` | Created | Implement missing WS manager |
| `runtime/task_queue.py` | Created | Implement missing task queue |
| `memory/substrate_graph.py` | Renamed `checkpoint_id` | Fix LangGraph reserved name |
| `dev/audit/smoke_test.py` | Created | Runtime validation script |

---

## 7. SMOKE TEST OUTPUT

```
============================================================
L9 AUDIT SMOKE TEST
============================================================
PASS: compileall
PASS: no_nested_repos
PASS: entrypoints_exist
PASS: migrations_exist
PASS: runtime_module_exists
PASS: langgraph_not_shadowed
PASS: core_imports
PASS: server_module_imports
PASS: memory_pipeline_dry_run
PASS: world_model_instantiation
============================================================
PASSED: 10
FAILED: 0
============================================================
ALL SMOKE TESTS PASSED
============================================================
```

---

## 8. NEXT STEPS (Recommendations)

1. **Wire `agents/` module** - 7 agent classes exist but are never called
2. **Decide on `telemetry/`** - Empty stub, either implement or remove
3. **Production task queue** - Current `runtime/task_queue.py` is in-memory; consider Redis for VPS
4. **Test with live DB** - Run `python dev/audit/smoke_test.py --with-db` after setting MEMORY_DSN

---

*End of Audit Report*

