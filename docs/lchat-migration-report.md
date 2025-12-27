# LChat Migration Report

## Files Modified

- `api/server.py`
- `api/webhook_slack.py`
- `config/settings.py`
- `docs/lchat-migration-report.md` (this file)

## Phases Implemented

### Phase 0: Feature Flags
Feature flags added (`L9_ENABLE_LEGACY_CHAT`, `L9_ENABLE_LEGACY_SLACK_ROUTER`); legacy behavior gated but unchanged.

### Phase 1: /lchat HTTP Endpoint
`/lchat` HTTP endpoint added using `AgentTask` + `AgentExecutorService` for `agent_id="l-cto"`.

### Phase 2: Slack Helper
Slack helper `handle_slack_with_l_agent()` implemented to route normalized Slack messages into `AgentTask` for `agent_id="l-cto"`.

### Phase 3: /lws WebSocket Endpoint
`/lws` WebSocket endpoint added, mapping JSON frames to `AgentTask` executions for `agent_id="l-cto"` with `source_id="ws"`.

### Phase 4: Slack Flag-Switchable Routing
Slack webhook handler made flag-switchable between legacy routing and L‑AgentTask path via `L9_ENABLE_LEGACY_SLACK_ROUTER`.

### Phase 5: Legacy /chat Control
Legacy `/chat` fully controllable via `L9_ENABLE_LEGACY_CHAT` (no code deletion).

## Current Functional Status

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/lchat` (HTTP) | yes | Always registered, uses AgentExecutorService |
| `/lws` (WebSocket) | yes | Always registered, uses AgentExecutorService |
| `/chat` (legacy HTTP) | flag-gated | Registered when `L9_ENABLE_LEGACY_CHAT=true` |
| Slack routing | flag-gated | Uses AgentTask when `L9_ENABLE_LEGACY_SLACK_ROUTER=false` |

## Flag Configuration (expected for production)

| Flag | Default | Recommended Production Value |
|------|---------|------------------------------|
| `L9_ENABLE_LEGACY_CHAT` | `True` | `False` (to disable legacy direct-OpenAI path) |
| `L9_ENABLE_LEGACY_SLACK_ROUTER` | `True` | `False` (to use kernel-aware agent stack) |

## Architecture Summary

### New Routing Paths

```
HTTP /lchat → AgentTask(l-cto) → AgentExecutorService → AIOSRuntime → LLM
WS   /lws   → AgentTask(l-cto) → AgentExecutorService → AIOSRuntime → LLM
Slack       → handle_slack_with_l_agent() → AgentTask(l-cto) → AgentExecutorService
```

### Legacy Paths (when flags = True)

```
HTTP /chat  → OpenAI direct (no kernels, no AgentTask)
Slack       → route_slack_message() → enqueue_task() (legacy task queue)
```

## Migration Notes

1. **No code deletion**: All legacy paths remain in codebase, only gated by flags.
2. **Kernel-aware**: New paths use `KernelAwareAgentRegistry` and kernel-loaded system prompts.
3. **Audit trail**: All new paths emit packets to memory substrate via AgentExecutorService.
4. **Thread continuity**: Thread identifiers are deterministically derived from source context.

