ROLE
You are CURSOR-GOD-MODE C operating under a locked CGMP to refactor the L9 API so that all interactions with the L‑CTO agent (L) are routed through the kernel-aware AgentTask / AgentExecutorService stack. You must follow this prompt exactly, treat all instructions as authoritative, and refuse to act outside the defined scope.

MISSION OBJECTIVE
Replace the current legacy simple HTTP chat path that calls OpenAI directly with a new `POST /lchat` HTTP endpoint that:
- Constructs a `core.agents.schemas.AgentTask` targeting the L‑CTO agent via `KernelAwareAgentRegistry`
- Executes it via `core.agents.executor.AgentExecutorService`
- Returns a stable, minimal JSON response for callers

All changes must be rolled out in controlled phases with feature flags to preserve existing behavior until explicitly disabled.

OPERATING MODE
- Operate only on the files and paths explicitly listed in this prompt.
- Use deterministic, explicit edits anchored to existing code structures (no large rewrites).
- Do not introduce new abstractions unless explicitly requested in a phase.
- Do not modify any behavior unrelated to L‑CTO chat routing.
- Preserve existing logging, error handling, and security checks unless a change is explicitly required.
- Keep all new public interfaces minimal, documented, and stable.

SCOPE – FILES YOU MAY EDIT
- `opt/l9/api/server.py` (a.k.a. `apiserver.py`)[web:27][web:29]
- `opt/l9/api/servermemory.py`[web:27]
- `opt/l9/api/webhook_slack.py` (or the actual Slack webhook file path already in the repo)[web:27]
- `opt/l9/core/agents/schemas.py`[web:27]
- `opt/l9/core/agents/executor.py`[web:27]
- `opt/l9/core/agents/agentinstance.py`[web:27]
- `opt/l9/core/agents/runtime.py`[web:27]
- `opt/l9/core/agents/kernelregistry.py`[web:27]
- L9 settings/config file used by `server.py` (e.g. `opt/l9/config/settings.py` or equivalent)[web:27]

DO NOT TOUCH any other files in this prompt.

---

PHASE -1 – PLANNING (NO CODE CHANGES)
1. Open and review:
   - `opt/l9/api/server.py` – FastAPI app, existing `POST /chat` route, `wsagent` endpoint, lifespan wiring.[web:27][web:29]
   - `opt/l9/api/servermemory.py` – legacy memory-only chat API.[web:27]
   - `opt/l9/api/webhook_slack.py` – Slack webhook handling, legacy routing path.[web:27]
   - `opt/l9/core/agents/schemas.py` – `AgentTask`, `TaskKind`, `AgentConfig`, `ExecutorState`, `AIOSResult`, `ToolCallRequest`, `ToolCallResult`.[web:27]
   - `opt/l9/core/agents/executor.py` – `AgentExecutorService.start_agent_task` (or equivalent), validation, execution loop.[web:27]
   - `opt/l9/core/agents/agentinstance.py` – how context, history, and tools are assembled.[web:27]
   - `opt/l9/core/agents/runtime.py` – `AIOSRuntime`, `execute_reasoning`.[web:27]
   - `opt/l9/core/agents/kernelregistry.py` – `KernelAwareAgentRegistry`, L‑CTO agent IDs (`l9-standard-v1`, alias `l-cto`).[web:27]
2. Confirm in `server.py` where:
   - `AgentExecutorService`, `AIOSRuntime`, `KernelAwareAgentRegistry`, and `ExecutorToolRegistry` are created and attached to `app.state` (e.g., `app.state.agent_executor`).[web:27]
3. DO NOT change any code in this phase.

---

PHASE 0 – FEATURE FLAGS, NO BEHAVIOR CHANGE
Objective: introduce toggles so you can switch between legacy and new paths without breaking existing integrations.

1. In the configuration layer used by `server.py` (e.g. `opt/l9/config/settings.py`):
   - Add boolean flags with these exact names and defaults:
     - `L9_ENABLE_LEGACY_CHAT: bool = True`
     - `L9_ENABLE_LEGACY_SLACK_ROUTER: bool = True`[web:27]
   - Expose them via the same `settings` object already used by `server.py`.

2. In `opt/l9/api/server.py`:
   - Locate the existing `@app.post("/chat")` route that calls OpenAI directly and writes a packet to memory.[web:27]
   - Wrap its definition in a conditional on `settings.L9_ENABLE_LEGACY_CHAT` so that:
     - When `True`: the route is registered and behaves exactly as today.
     - When `False`: the route is not registered at all.
   - DO NOT change the internals of the legacy handler in this phase.

3. In `opt/l9/api/webhook_slack.py`:
   - Locate the main Slack webhook handler entrypoint (e.g. `@app.post("/slack/webhook")` or equivalent).[web:27]
   - Introduce a conditional that checks `settings.L9_ENABLE_LEGACY_SLACK_ROUTER`:
     - When `True`: keep existing Slack routing behavior intact.
     - When `False`: for now, still call the same legacy behavior (Phase 2 will add the new path).

4. In `opt/l9/api/servermemory.py`:
   - Do not change behavior in this phase.
   - Only ensure any imports of `settings` still work after adding the new flags.

Definition of done for Phase 0:
- Both flags exist, default to `True`, and wrapping logic compiles.
- Behavior for `/chat` and Slack remains unchanged when flags are `True`.

---

PHASE 1 – ADD `POST /lchat` USING `AgentTask` + `AgentExecutorService`
Objective: introduce a new HTTP endpoint for L that uses the executor stack, without altering existing callers.

1. In `opt/l9/api/server.py`, near existing API models:
   - Define two Pydantic models (use existing import style: `BaseModel`, `Field`, `Optional`, `Any`):
     ```
     class LChatRequest(BaseModel):
         message: str
         thread_id: Optional[str] = None
         metadata: dict[str, Any] = Field(default_factory=dict)

     class LChatResponse(BaseModel):
         reply: str
         task_id: str
         status: str
     ```
   - Match naming and import conventions already used in `server.py`.[web:27]

2. Still in `server.py`, add a new route:
   - `@app.post("/lchat", response_model=LChatResponse)`
   - The handler MUST:
     - Reuse the same auth mechanism as other protected endpoints in `server.py` (e.g. existing API key or auth dependency).[web:27]
     - Access `app.state.agent_executor` and NOT re-initialize any executors/registries.

3. Inside the `lchat` handler:
   - Resolve the target agent ID:
     - Use `"l-cto"` as the `agent_id` (this alias already exists in `KernelAwareAgentRegistry`).[web:27]
   - Construct an `AgentTask` from `core.agents.schemas` with:
     - `agent_id="l-cto"`
     - `kind=TaskKind.CONVERSATION`
     - `source_id="http"`
     - `thread_identifier=request.thread_id or "<http-default>"` (choose a deterministic fallback string, and keep it constant).
     - `payload` containing at least:
       - `"message": request.message`
       - `"channel": "http"`
       - `"metadata": request.metadata`
     - Use default timeout/iterations from the model; DO NOT invent new fields.[web:27]
   - Call:
     - `result_or_dup = await app.state.agent_executor.start_agent_task(task)`
       - Use the actual method name from `AgentExecutorService` (e.g. `start_agent_task`), not a new one.[web:27]
   - Handle duplicate vs fresh execution:
     - If the executor returns a duplicate-style result, respond with:
       - `status="duplicate"`
       - `reply="Duplicate task"`
       - `task_id` from the duplicate info.
     - If it returns an `ExecutionResult` (or equivalent), extract:
       - `task_id` from the task or result.
       - `status` from result status.
       - `reply` from the final assistant message content using the existing field in the result type (do NOT invent a new structure).[web:27]

4. Ensure `lchat` NEVER calls OpenAI directly:
   - No direct `openai` / `AsyncOpenAI` imports or usage in this route.
   - All LLM calls must flow through `AgentExecutorService` → `AgentInstance` → `AIOSRuntime`.[web:27]

5. DO NOT disable `/chat` yet. At the end of Phase 1:
   - `/chat` is still behind `L9_ENABLE_LEGACY_CHAT`.
   - `/lchat` is fully functional and uses the executor stack.

---

PHASE 2 – PREPARE SLACK TO USE L VIA `AgentTask` (NO SWITCH YET)
Objective: add a code path that can route Slack messages into `AgentTask` for L, but keep the legacy Slack routing active.

1. In `opt/l9/api/webhook_slack.py`:
   - Identify the normalization flow using `SlackRequestValidator` and `SlackRequestNormalizer`.[web:27]
   - Implement a helper function, e.g. `async def handle_slack_with_l_agent(app, normalized_message) -> tuple[str, str]:`
     - It SHOULD:
       - Accept normalized Slack message info: `text`, `thread_uuid`, `team_id`, `channel_id`, `user_id`.
       - Construct an `AgentTask` similar to `lchat`:
         - `agent_id="l-cto"`
         - `kind=TaskKind.CONVERSATION`
         - `source_id="slack"`
         - `thread_identifier` = Slack thread UUID.
         - `payload` including:
           - `"message": text`
           - `"channel": "slack"`
           - `"slack": {"team_id": ..., "channel_id": ..., "user_id": ...}`
       - Call `await app.state.agent_executor.start_agent_task(task)`.
       - Return `(reply_text, status)` formatted for Slack.

2. DO NOT yet switch the main Slack webhook handler to use this helper.
   - Legacy behavior remains in place.
   - The helper must compile and be testable in isolation.

Definition of done for Prompt 1:
- Flags exist and wrap legacy chat + Slack.
- `/lchat` exists and uses `AgentExecutorService` correctly.
- Slack helper exists and builds `AgentTask` for `"l-cto"` but is not yet wired into the main handler.

DO NOT PROCEED to WebSocket or Slack switching in this prompt.
Stop after Phase 2 is complete and all tests pass.
