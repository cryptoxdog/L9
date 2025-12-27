ROLE
You are CURSOR-GOD-MODE C operating under a locked CGMP to finish routing all L‑CTO interactions through the kernel-aware AgentTask / AgentExecutorService stack, and to introduce a WebSocket entrypoint for L consistent with the existing L9 WS orchestration architecture. You must follow this prompt exactly, and refuse to act outside the defined scope.

MISSION OBJECTIVE
1. Introduce a dedicated WebSocket entrypoint `/lws` for L that:
   - Accepts JSON frames from clients.
   - Maps each frame into an `AgentTask` for `"l-cto"` and executes it via `AgentExecutorService`.
   - Returns replies over the same WebSocket.
2. Wire Slack into the new L‑AgentTask path using a feature flag.
3. Keep all legacy behavior feature-gated and non-destructive, and write a migration report.

OPERATING MODE
- Assume Prompt 1 has already been applied (feature flags + `/lchat` + Slack helper exist).
- Operate only on the files listed below.
- No new abstractions beyond what is explicitly described.
- Preserve existing behavior when flags are `True`.

SCOPE – FILES YOU MAY EDIT
- `opt/l9/api/server.py`[web:27][web:29]
- `opt/l9/api/webhook_slack.py`[web:27]
- `opt/l9/docs/lchat-migration-report.md` (new file)[web:27]

You MAY read but not structurally change:
- `opt/l9/core/orchestrators/websocket_orchestrator.py`[web:27]
- `opt/l9/core/orchestrators/wsbridge.py`[web:27]
- `opt/l9/core/orchestrators/wstaskrouter.py`[web:27]
- `opt/l9/core/schemas/wseventstream.py`[web:27]

---

PHASE 3 – ADD DEDICATED `lws` WEBSOCKET ENTRYPOINT
Objective: introduce a WebSocket endpoint for L clients that uses `AgentTask` + `AgentExecutorService` directly, without disturbing existing `wsagent`.

1. In `opt/l9/api/server.py`:
   - Locate the existing `@app.websocket("/wsagent")` endpoint and review its behavior.[web:27]
   - Immediately near it, add a new endpoint:
     ```
     @app.websocket("/lws")
     async def l_ws(websocket: WebSocket):
         ...
     ```
     Use the same import style and dependencies as `wsagent`.[web:27]

2. Implement `l_ws` with the following protocol:
   - On connect:
     - `await websocket.accept()`
   - Then loop:
     - `data = await websocket.receive_json()`
     - Expect frames with at least:
       - `message: str`
       - Optional `thread_id: str`
       - Optional `metadata: dict`
     - Build an `AgentTask` for `"l-cto"` exactly as in `/lchat`, but:
       - `source_id="ws"`
       - `thread_identifier` from `thread_id` field if present, else a deterministic WS default string.
       - `payload` must include `"channel": "ws"` plus any metadata.
     - Call `await app.state.agent_executor.start_agent_task(task)`.
     - Extract:
       - `task_id`
       - `status`
       - `reply` (assistant text) from the executor result.
     - Send back a JSON frame:
       ```
       {
         "task_id": "...",
         "status": "...",
         "reply": "..."
       }
       ```
   - Error handling:
     - If task creation or execution fails, send a JSON frame with `status="error"` and a short `reply` message, then continue or close as appropriate.
   - DO NOT route `lws` frames through `wsbridge` or `wstaskrouter` in this phase.
   - DO NOT alter `wsagent`.

Definition of done for Phase 3:
- `/lws` exists, compiles, and uses `AgentExecutorService` for `"l-cto"` with `source_id="ws"`.

---

PHASE 4 – SWITCH SLACK TO L VIA `AgentTask` WITH FLAG
Objective: allow Slack to use the L‑AgentTask path while keeping legacy routing available via `L9_ENABLE_LEGACY_SLACK_ROUTER`.

1. In `opt/l9/api/webhook_slack.py`:
   - Locate the main Slack webhook handler.[web:27]
   - Modify it so that:
     - If `settings.L9_ENABLE_LEGACY_SLACK_ROUTER is True`:
       - Use the existing legacy routing path unchanged.
     - If `False`:
       - Use the Phase 2 helper you created (e.g. `handle_slack_with_l_agent`) to:
         - Build an `AgentTask` for `"l-cto"`.
         - Execute it via `app.state.agent_executor`.
         - Produce the reply used in the Slack HTTP response.
   - Ensure:
     - All Slack message types previously handled still get a response.
     - No direct OpenAI calls are made in this new path; all go through executor stack.

Definition of done for Phase 4:
- Slack path can be toggled between legacy and L‑AgentTask by changing `L9_ENABLE_LEGACY_SLACK_ROUTER`.

---

PHASE 5 – LEGACY CHAT FLAG USE (NO DELETION)
Objective: demonstrate that legacy chat can be disabled purely via config; do NOT delete the code.

1. Ensure `opt/l9/api/server.py`:
   - Registers `/chat` only when `settings.L9_ENABLE_LEGACY_CHAT` is `True`.
   - Always registers `/lchat`.
2. Do NOT change values of flags in code; they are controlled via deployment config, not hard-coded.

---

FINAL REPORT – `opt/l9/docs/lchat-migration-report.md`
Create this new markdown file with the following content structure:

