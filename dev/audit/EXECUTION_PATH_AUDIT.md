# L9 Execution Path Audit

**Date:** 2025-12-13  
**Scope:** All externally reachable execution paths (HTTP, WebSocket, Slack, Timers)

---

## 1. Entry Surface Enumeration

### 1.1 api/server.py (Primary FastAPI App)

| Surface | Path | Function | Memory Ingestion | Orchestrator | Status |
|---------|------|----------|------------------|--------------|--------|
| GET | `/` | `root()` | NO (read-only) | NO | OK - Health check |
| GET | `/os/health` | `os_health()` | NO (read-only) | NO | OK - Health check |
| GET | `/os/status` | `os_status()` | NO (read-only) | NO | OK - Health check |
| GET | `/agent/health` | `agent_health()` | NO (read-only) | NO | OK - Health check |
| GET | `/agent/status` | `agent_status()` | NO (read-only) | NO | OK - Health check |
| POST | `/agent/task` | `submit_task()` | YES (fixed) | NO | FIXED |
| POST | `/memory/packet` | `create_packet()` | YES | via DAG | OK |
| POST | `/memory/semantic/search` | `semantic_search()` | NO (read-only) | NO | OK |
| GET | `/memory/stats` | `get_stats()` | NO (read-only) | NO | OK |
| POST | `/memory/test` | `memory_test()` | NO (read-only) | NO | OK |
| WS | `/ws/agent` | `agent_ws_endpoint()` | YES | via ws_orchestrator | OK |

### 1.2 api/server_memory.py (Alt App with Integrations)

| Surface | Path | Function | Memory Ingestion | Orchestrator | Status |
|---------|------|----------|------------------|--------------|--------|
| GET | `/` | `root()` | NO (read-only) | NO | OK |
| GET | `/health` | `health()` | NO (read-only) | NO | OK |
| POST | `/chat` | `chat()` | YES (fixed) | NO | FIXED |

### 1.3 api/webhook_slack.py

| Surface | Path | Function | Memory Ingestion | Orchestrator | Status |
|---------|------|----------|------------------|--------------|--------|
| POST | `/slack/commands` | `slack_commands()` | YES (via enqueue) | NO | FIXED |
| POST | `/slack/events` | `slack_events()` | YES (via enqueue) | NO | FIXED |

### 1.4 api/webhook_mac_agent.py

| Surface | Path | Function | Memory Ingestion | Orchestrator | Status |
|---------|------|----------|------------------|--------------|--------|
| GET | `/mac/tasks/next` | `get_next_mac_task()` | NO (read-only) | NO | OK |
| POST | `/mac/tasks/{id}/result` | `submit_task_result()` | YES (fixed) | NO | FIXED |
| GET | `/mac/tasks` | `list_mac_tasks()` | NO (read-only) | NO | OK |

### 1.5 api/webhook_twilio.py

| Surface | Path | Function | Memory Ingestion | Orchestrator | Status |
|---------|------|----------|------------------|--------------|--------|
| POST | `/twilio/webhook` | `twilio_webhook()` | YES (via `/chat`) | NO | FIXED |

### 1.6 api/webhook_waba.py

| Surface | Path | Function | Memory Ingestion | Orchestrator | Status |
|---------|------|----------|------------------|--------------|--------|
| GET | `/waba/webhook` | `verify_waba_webhook()` | NO (verification) | NO | OK |
| POST | `/waba/webhook` | `waba_webhook()` | YES (via `/chat`) | NO | FIXED |

### 1.7 api/world_model_api.py

| Surface | Path | Function | Memory Ingestion | Orchestrator | Status |
|---------|------|----------|------------------|--------------|--------|
| GET | `/world-model/health` | `world_model_health()` | NO (read-only) | NO | OK |
| GET | `/world-model/entities/{id}` | `get_entity()` | NO (read-only) | NO | OK |
| GET | `/world-model/entities` | `list_entities()` | NO (read-only) | NO | OK |
| GET | `/world-model/state-version` | `get_state_version()` | NO (read-only) | NO | OK |
| POST | `/world-model/snapshot` | `create_snapshot()` | YES (WM service) | YES | OK |
| POST | `/world-model/restore` | `restore_from_snapshot()` | YES (WM service) | YES | OK |
| GET | `/world-model/snapshots` | `list_snapshots()` | NO (read-only) | NO | OK |
| POST | `/world-model/insights` | `submit_insights()` | YES (WM service) | YES | OK |
| GET | `/world-model/updates` | `list_updates()` | NO (read-only) | NO | OK |

### 1.8 email_agent/router.py

| Surface | Path | Function | Memory Ingestion | Orchestrator | Status |
|---------|------|----------|------------------|--------------|--------|
| POST | `/email/query` | `query_emails()` | YES (pre+post) | NO | FIXED |
| POST | `/email/get` | `get_email()` | YES (pre+post) | NO | FIXED |
| POST | `/email/draft` | `draft_email()` | YES (pre+post) | NO | FIXED |
| POST | `/email/send` | `send_email()` | YES (pre+post) | NO | FIXED |
| POST | `/email/reply` | `reply_email()` | YES (pre+post) | NO | FIXED |
| POST | `/email/forward` | `forward_email()` | YES (pre+post) | NO | FIXED |

### 1.9 Background Tasks / Startup Events

| Surface | Location | Function | Memory Ingestion | Status |
|---------|----------|----------|------------------|--------|
| startup | `api/server.py` | `lifespan()` | YES (init_service) | OK |
| startup | `api/server.py` | `on_startup()` | NO (hook only) | OK |
| shutdown | `api/server.py` | `on_shutdown()` | NO (cleanup) | OK |
| timer | `world_model/runtime.py` | `run_forever()` | YES | OK |

---

## 2. Violation Summary

### 2.1 Violations Status (State Changes Without Memory)

| # | Path | Problem | Status |
|---|------|---------|--------|
| 1 | `/agent/task` | Accepts tasks but doesn't process or ingest | **FIXED** |
| 2 | `/chat` | LLM calls bypass memory entirely | **FIXED** |
| 3 | `/slack/commands` | Enqueues tasks to file, no memory | **FIXED** |
| 4 | `/slack/events` | Same as above | **FIXED** |
| 5 | `/mac/tasks/{id}/result` | Stores results without memory ingest | **FIXED** |
| 6 | `/twilio/webhook` | Routes through `/chat`, no memory | **FIXED** (via `/chat`) |
| 7 | `/waba/webhook` | Routes through `/chat`, no memory | **FIXED** (via `/chat`) |
| 8 | `/email/*` | All Gmail operations bypass memory | **FIXED** |

### 2.2 Acceptable Read-Only Paths

These paths are read-only and do not require memory ingestion:
- All `/health` and `/status` endpoints
- All `GET` endpoints that only read data
- Verification endpoints (WABA challenge, etc.)

---

## 3. Call Chain Analysis

### 3.1 Compliant Path: WebSocket Agent
```
@app.websocket("/ws/agent")
    └── receive_json()
        └── ingest_packet(PacketEnvelopeIn)  ✅
            └── SubstrateDAG.run()
                ├── intake_node
                ├── reasoning_node
                ├── memory_write_node  ✅ (DB write)
                ├── semantic_embed_node
                ├── extract_insights_node
                ├── store_insights_node
                ├── world_model_trigger_node
                └── checkpoint_node
        └── ws_orchestrator.handle_incoming()  ✅
            └── orchestrators/ws_bridge.handle_ws_event()
```

### 3.2 Compliant Path: Memory Packet API
```
POST /memory/packet
    └── create_packet()
        └── ingest_packet(packet_in)  ✅
            └── SubstrateDAG.run()  ✅
```

### 3.3 Violating Path: Chat Endpoint
```
POST /chat
    └── chat()
        └── OpenAI.chat.completions.create()
        └── return reply
        ⚠️ NO MEMORY INGESTION
```

### 3.4 Violating Path: Slack Commands
```
POST /slack/commands
    └── slack_commands()
        └── route_slack_message()  (LLM call, returns task dict)
        └── enqueue_task()  (writes to ~/.l9/mac_tasks/*.json)
        ⚠️ NO MEMORY INGESTION
```

### 3.5 Violating Path: Mac Task Result
```
POST /mac/tasks/{id}/result
    └── submit_task_result()
        └── complete_task()  (updates in-memory task)
        └── slack_post()  (sends to Slack)
        ⚠️ NO MEMORY INGESTION
```

---

## 4. Applied Fixes

### 4.1 FIXED - HIGH Priority

| # | File | Fix Applied | Status |
|---|------|-------------|--------|
| 1 | `api/agent_routes.py` | Added `ingest_packet()` to `/agent/task` | DONE |
| 2 | `api/server_memory.py` | Added `ingest_packet()` to `/chat` (async) | DONE |
| 3 | `services/mac_tasks.py` | Added `ingest_packet()` to `enqueue_task()` | DONE |
| 4 | `services/mac_tasks.py` | Added `ingest_packet()` to `enqueue_mac_task()` | DONE |
| 5 | `api/webhook_mac_agent.py` | Added `ingest_packet()` to task result submission | DONE |

### 4.2 Auto-Fixed via Dependencies

| # | File | Path | Fixed By |
|---|------|------|----------|
| 6 | `api/webhook_slack.py` | `/slack/commands` | `enqueue_task()` now ingests |
| 7 | `api/webhook_slack.py` | `/slack/events` | `enqueue_task()` / `enqueue_mac_task()` now ingest |
| 8 | `api/webhook_twilio.py` | `/twilio/webhook` | `/chat` now ingests |
| 9 | `api/webhook_waba.py` | `/waba/webhook` | `/chat` now ingests |

### 4.3 FIXED - Email Routes (v3.0.0)

| # | File | Fix Applied |
|---|------|-------------|
| 10 | `email_agent/router.py` | All handlers now ingest pre+post events with trace_id |
| 11 | `dev/audit/smoke_email.py` | Created smoke test for email ingestion |

Features:
- All 6 email handlers (query, get, draft, send, reply, forward) now ingest to memory
- Pre-action event ingested before Gmail API call
- Post-action event ingested with success/error status
- Every response includes `trace_id` for tracing
- Ingestion failure causes HTTP 500 (fail loud policy)
- Sensitive content (email body) NOT ingested, only metadata

---

## 5. Guaranteed Invariants (After Fixes)

Once fixes are applied, the following invariants will hold:

1. **No external task executes without memory ingestion**
   - Every POST that triggers an action writes a packet
   
2. **No LLM call occurs without audit trail**
   - All `/chat` calls ingest query + response
   
3. **All Slack interactions are recorded**
   - Commands, events, and results ingested
   
4. **All Mac agent results are persisted**
   - Task results flow through memory DAG
   
5. **Read-only endpoints are explicitly allowed**
   - Health checks and GET queries do not require ingestion

---

## 6. Enforcement Guards (Recommended)

Add runtime guards to detect violations:

```python
# In memory/ingestion.py
import logging

_INGESTION_REQUIRED_PATHS = {
    "/chat", "/agent/task", "/slack/commands", "/slack/events",
    "/mac/tasks/{task_id}/result", "/email/send", "/email/reply",
    "/email/forward", "/email/draft"
}

def enforce_ingestion_guard(request_path: str, packet_type: str):
    """Log warning if a path that should ingest doesn't call this."""
    logger = logging.getLogger("l9.ingestion.guard")
    logger.debug(f"Ingestion called for {request_path}: {packet_type}")

# Call at start of ingest_packet():
# enforce_ingestion_guard(request.url.path, packet_in.packet_type)
```

---

*End of Execution Path Audit*

