---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

## **GMP-7: GMP-L.multi-modal-unified-routing**

You are C. You are not rewriting Slack, WS, or HTTP handlers. You are unifying them so every L interaction—whether via HTTP `/lchat`, WS `/lws`, Slack webhook, or Mac agent callback—flows through `AgentExecutorService` with consistent tools, memory, and governance.

### OBJECTIVE (LOCKED)

Ensure that:
1. All L entrypoints (HTTP, WS, Slack, Mac callback) create an `AgentTask` with `agent_id="L"`.
2. All tasks go through `AgentExecutorService`, not bypassing via direct OpenAI calls.
3. Response formatting is channel-specific (JSON for HTTP, text for Slack, etc.) but execution is unified.
4. All interactions logged to memory and audit trail.

### SCOPE (LOCKED)

You MAY modify:
- `api/server.py` – ensure `/lchat` uses `AgentExecutorService`.
- `api/websocket_orchestrator.py` or relevant WS handler – ensure `/lws` uses executor.
- `api/slack_adapter.py` or Slack webhook handler – normalize requests to `AgentTask`, pass through executor.
- New file: `core/routing/task_router.py` – unified task creation from any channel.
- New file: `core/formatting/response_formatter.py` – format executor output per channel.
- `core/agents/executor.py` – add metadata field for source channel (http, ws, slack, mac).

You MAY NOT:
- Modify channel-specific logic (Slack signatures, WS framing, etc.); only route and format.
- Change approval gates or tool behavior.

### TODO LIST (BY ID)

**T1 – Unified task router**
- File: `core/routing/task_router.py` (new)
- Function: `create_task_from_request(channel: str, user_id: str, input_text: str, metadata: dict) -> AgentTask`
- Normalizes any channel input to `AgentTask` with:
  - `agent_id="L"`.
  - `task_kind="conversation"`.
  - `input` = normalized user text.
  - `source_channel` = "http", "ws", "slack", or "mac".
  - `user_id`, `session_id`, metadata preserved.

**T2 – HTTP entrypoint uses router**
- File: `api/server.py`, in `/lchat` POST handler
- Call `create_task_from_request(channel="http", user_id=user_id, input_text=request.message, metadata=request.metadata)`.
- Pass task to `AgentExecutorService.execute(task)`.
- Format result per T4.

**T3 – WS entrypoint uses router**
- File: `api/websocket_orchestrator.py`, in connection handler
- On each message, call `create_task_from_request(channel="ws", user_id=client_id, input_text=message, metadata={session_id: ws_session_id})`.
- Pass to executor.
- Format and send response back over WS per T4.

**T4 – Slack adapter uses router**
- File: `api/slack_adapter.py` or `webhooks/slack.py`
- On webhook receive, validate signature.
- Extract user message and normalize via `create_task_from_request(channel="slack", user_id=slack_user_id, input_text=event.text, metadata={channel_id: event.channel})`.
- Pass to executor.
- Format response per T5 and post via Slack client.

**T5 – Response formatter by channel**
- File: `core/formatting/response_formatter.py` (new)
- Implement:
  - `format_for_http(executor_result) -> dict` (JSON structure).
  - `format_for_ws(executor_result) -> dict` (EventMessage schema).
  - `format_for_slack(executor_result) -> SlackMessage` (text, blocks, thread reply).
  - `format_for_mac(executor_result) -> dict` (Mac agent callback format).

**T6 – Mac agent callback uses router**
- File: `api/webhooks/mac_agent.py`, in callback handler
- Extract task result and user context.
- Call `create_task_from_request(channel="mac", user_id=mac_user_id, input_text=user_query, metadata={mac_session: mac_context})`.
- Pass to executor.
- Format and return via callback.

**T7 – Add source_channel to AgentTask**
- File: `core/agents/schemas.py`, in `AgentTask` dataclass
- Add field: `source_channel: str` (default "http").

**T8 – Log source channel to memory**
- File: `core/agents/executor.py`, after task completes
- Write source_channel to the interaction packet in memory.
- Allows Igor to filter interactions by channel in audit logs.

**T9 – Integration test**
- File: `tests/integration/test_multi_modal_routing.py` (new)
- Simulate HTTP request, WS message, Slack webhook, and Mac callback all with same user question.
- Verify all create same `AgentTask` (modulo source_channel).
- Verify all use same executor.
- Verify responses are formatted correctly per channel.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm all entrypoints exist and can be modified.
2. Verify Slack adapter can be extended with router call without breaking signature validation.
3. Check if any entrypoints bypass executor currently; mark as [PRIORITY].

### PHASES 1–6

Validation:
- **Positive:** Send same question via HTTP, WS, Slack; verify identical reasoning, different format.
- **Negative:** Channel unavailability doesn't break other channels.
- **Regression:** Existing channel-specific behavior (signatures, framing) unchanged.

***
