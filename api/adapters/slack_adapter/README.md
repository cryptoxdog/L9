# Slack Adapter Documentation

## Overview

L9 has **three Slack integration implementations** that coexist for backward compatibility and gradual migration:

1. **Slack Webhook Adapter (v2.6)** - Newest, module-based adapter (`api/adapters/slack_adapter/`)
2. **Slack Routes (v2.0+)** - FastAPI routes with validation (`api/routes/slack.py`)
3. **Legacy Webhook Handler** - Original implementation (`api/webhook_slack.py`)

## Current Status

### What's Enabled

All three implementations are **conditionally registered** in `api/server.py`:

- **Slack Webhook Adapter (v2.6)**: Registered if `api/adapters/slack_adapter` imports successfully
- **Slack Routes (v2.0+)**: Registered if `_has_slack` is True (requires `api/slack_adapter.py`)
- **Legacy Webhook**: Registered if `_has_slack` is True (always registered, but behavior gated by `L9_ENABLE_LEGACY_SLACK_ROUTER`)

### Feature Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `SLACK_APP_ENABLED` | `false` | Master toggle for all Slack functionality |
| `L9_ENABLE_LEGACY_SLACK_ROUTER` | `true` | When `false`, routes through AgentTask + L-CTO agent instead of legacy handlers |

## Architecture

### 1. Slack Webhook Adapter (v2.6) - Recommended

**Location**: `api/adapters/slack_adapter/`

**Routes**:
- `POST /slack/events` - Slack Events API webhook
- `GET /slack/health` - Health check

**Features**:
- HMAC-SHA256 signature validation
- Idempotent request handling (dedupe cache)
- Packet emission to memory substrate
- AIOS runtime integration
- Module-spec v2.6 compliant

**Wiring**: See `WIRING_LOG.md` in this directory.

**Configuration**:
```python
# Environment variables (from config.py)
SLACK_SIGNING_SECRET  # Required
SLACK_BOT_TOKEN       # Required
SLACK_APP_ENABLED     # Optional, feature toggle
SLACK_WEBHOOK_LOG_LEVEL  # Optional
```

### 2. Slack Routes (v2.0+)

**Location**: `api/routes/slack.py`

**Routes**:
- `POST /slack/events` - Events API handler
- `POST /slack/commands` - Slash command handler

**Features**:
- Uses `SlackRequestValidator` and `SlackRequestNormalizer` from `api/slack_adapter.py`
- Routes to memory ingestion layer (`memory/slack_ingest.py`)
- Dependency injection via FastAPI `Depends`

**Initialization**: 
- Validator and client initialized in `server.py` lifespan
- Stored in `app.state.slack_validator` and `app.state.slack_client`

### 3. Legacy Webhook Handler

**Location**: `api/webhook_slack.py`

**Routes**:
- `POST /slack/events` - Legacy event handler

**Behavior**:
- When `L9_ENABLE_LEGACY_SLACK_ROUTER=true`: Uses legacy routing (planner/queue)
- When `L9_ENABLE_LEGACY_SLACK_ROUTER=false`: Routes through `handle_slack_with_l_agent()` → AgentTask → L-CTO agent

**Key Function**: `handle_slack_with_l_agent()` (lines 25-100)
- Constructs `AgentTask` for `agent_id="l-cto"`
- Executes via `AgentExecutorService.start_agent_task()`
- Returns formatted reply for Slack

## Event Flow

### Current Flow (Legacy Router Enabled)

```
Slack Event → /slack/events (webhook_slack.py)
  → Legacy routing (if L9_ENABLE_LEGACY_SLACK_ROUTER=true)
  → OR handle_slack_with_l_agent() → AgentTask → L-CTO (if flag=false)
```

### Target Flow (v2.6 Adapter)

```
Slack Event → /slack/events (slack_webhook_adapter)
  → SlackWebhookAdapter.process()
  → Memory substrate packet emission
  → AIOS runtime integration
```

## OAuth Scopes

Required scopes for the Slack app (see `l-cto/slack.scope.md`):

**Bot Token Scopes**:
- `app_mentions:read` - View @L-CTO mentions
- `assistant:write` - Act as App Agent
- `channels:history` - View public channel messages
- `channels:join` - Join public channels
- `chat:write` - Send messages
- `files:write` - Upload/edit/delete files
- `im:history` - View DM messages
- `im:read` - View DM info
- `im:write` - Start DMs
- `incoming-webhook` - Post to channels
- `links:read` - View URLs
- `mpim:history` - Group DM history
- `reactions:read` - View reactions

## Event Subscriptions

To enable "no @L needed" in DMs:

1. **Slack App → Event Subscriptions**:
   - Enable Events: **ON**
   - Request URL: `https://your-domain.com/slack/events`

2. **Subscribe to bot events**:
   - `app_mention` (already enabled) - For channel mentions
   - `message.im` - **Add this** for DM messages without @L
   - `message.channels` - Optional, for channel-wide listening
   - `message.groups` - Optional, for private channels

3. **OAuth & Permissions**:
   - Ensure `im:history` scope is present
   - Reinstall app to workspace if scopes changed

## Environment Variables

### Required
```bash
SLACK_SIGNING_SECRET=xoxb-...  # From Slack App → Basic Information → Signing Secret
SLACK_BOT_TOKEN=xoxb-...       # From Slack App → OAuth & Permissions → Bot User OAuth Token
```

### Optional
```bash
SLACK_APP_ENABLED=true          # Master toggle
L9_ENABLE_LEGACY_SLACK_ROUTER=false  # Use AgentTask routing (recommended)
```

## Testing

### Unit Tests
```bash
pytest api/adapters/slack_adapter/tests/test_slack_webhook.py
```

### Integration Tests
```bash
pytest api/adapters/slack_adapter/tests/test_slack_webhook_integration.py
```

## Migration Path

### Phase 1: Current State ✅
- All three implementations coexist
- Legacy router enabled by default (`L9_ENABLE_LEGACY_SLACK_ROUTER=true`)

### Phase 2: Enable AgentTask Routing
- Set `L9_ENABLE_LEGACY_SLACK_ROUTER=false`
- DMs and messages containing "l9" route through L-CTO agent
- See `igor/slack enabling.md` for detailed GMP prompt

### Phase 3: Migrate to v2.6 Adapter (Future)
- Deprecate legacy webhook handler
- Standardize on `api/adapters/slack_adapter/`
- Remove duplicate routes

## Troubleshooting

### Slack adapter not initializing
- Check: `SLACK_SIGNING_SECRET` and `SLACK_BOT_TOKEN` are set
- Check: `SLACK_APP_ENABLED=true` (if using startup validation)
- Check logs for: "Slack adapter not initialized: ..."

### Events not received
- Verify Request URL in Slack App settings matches your server
- Check that `url_verification` challenge is handled correctly
- Ensure event subscriptions are enabled in Slack App dashboard

### Messages not routing to L-CTO
- Check: `L9_ENABLE_LEGACY_SLACK_ROUTER=false` (to use AgentTask path)
- Verify: `app.state.agent_executor` is initialized in `server.py`
- Check logs for: "handle_slack_with_l_agent: agent_executor not available"

## Related Files

- `api/adapters/slack_adapter/WIRING_LOG.md` - Technical wiring details
- `l-cto/slack.scope.md` - OAuth scopes reference
- `igor/slack enabling.md` - GMP prompt for enabling DM routing
- `api/webhook_slack.py` - Legacy implementation
- `api/routes/slack.py` - v2.0+ routes
- `api/slack_adapter.py` - Validation/normalization utilities

## v2.6 Adapter vs AgentTask Routing

### Key Differences

| Feature | AgentTask Routing (`handle_slack_with_l_agent`) | v2.6 Adapter |
|---------|------------------------------------------------|--------------|
| **Architecture** | Direct function call → AgentExecutorService | Structured orchestration pipeline |
| **Memory Integration** | ❌ No packet emission | ✅ Automatic inbound/outbound/error packet emission |
| **Idempotency** | ❌ No deduplication | ✅ Dedupe cache with TTL (24h default) |
| **Thread UUID** | Manual generation | ✅ Deterministic UUIDv5 from request |
| **Error Handling** | Basic try/catch | ✅ Structured error packets to memory |
| **Validation** | Minimal | ✅ Multi-step validation pipeline |
| **Observability** | Basic logging | ✅ Packet-based audit trail |
| **AIOS Integration** | Direct agent execution | ✅ Can route to AIOS runtime OR agent executor |
| **Module Compliance** | ❌ Custom implementation | ✅ Module-Spec v2.6 compliant |
| **Side Effects** | Mixed with logic | ✅ Separated (`_execute_side_effects`) |
| **Testing** | Manual integration | ✅ Unit + integration test suite |

### Why v2.6 is Better

#### 1. **Memory Substrate Integration**
- **AgentTask**: No automatic packet emission. Events may not be fully auditable.
- **v2.6**: Every request/response/error automatically written to memory substrate as packets:
  - `slack_webhook.in` - Inbound request packet
  - `slack_webhook.out` - Outbound response packet  
  - `slack_webhook.error` - Error packet (if failure)
- **Benefit**: Full audit trail, searchable history, thread reconstruction

#### 2. **Idempotency & Deduplication**
- **AgentTask**: Same message processed multiple times if Slack retries
- **v2.6**: Dedupe cache prevents duplicate processing (24h TTL)
- **Benefit**: Prevents duplicate agent responses, reduces API costs

#### 3. **Deterministic Threading**
- **AgentTask**: Thread UUID passed in (may be inconsistent)
- **v2.6**: UUIDv5 generated deterministically from request (same request = same UUID)
- **Benefit**: Consistent thread grouping across retries, better conversation continuity

#### 4. **Structured Orchestration**
- **AgentTask**: Single function with mixed concerns
- **v2.6**: Clear pipeline:
  ```
  1. Generate context (thread UUID)
  2. Validate request
  3. Check idempotency
  4. Write inbound packet
  5. Execute business logic
  6. Write outbound packet
  7. Execute side effects (Slack API calls)
  8. Cache response
  ```
- **Benefit**: Easier to test, debug, and extend

#### 5. **Error Recovery**
- **AgentTask**: Errors logged but not persisted
- **v2.6**: Error packets written to memory with full context
- **Benefit**: Error analysis, retry logic, failure pattern detection

#### 6. **Module-Spec Compliance**
- **AgentTask**: Custom implementation, not standardized
- **v2.6**: Follows Module-Spec v2.6 patterns (same as email, twilio, calendar adapters)
- **Benefit**: Consistent patterns across all integrations, easier maintenance

#### 7. **Flexible Execution**
- **AgentTask**: Hardcoded to `AgentExecutorService.start_agent_task()`
- **v2.6**: Can route to:
  - AIOS runtime (`aios_runtime_client.execute_reasoning()`)
  - Agent executor (via AgentTask)
  - Custom logic
- **Benefit**: Supports multiple execution models, future-proof

### When to Use Each

**Use AgentTask Routing** when:
- ✅ Quick prototype or temporary solution
- ✅ Simple use case with no memory/audit requirements
- ✅ Direct agent execution is sufficient

**Use v2.6 Adapter** when:
- ✅ Production deployment (recommended)
- ✅ Need full audit trail and observability
- ✅ Need idempotency (Slack retries)
- ✅ Want consistent patterns with other adapters
- ✅ Need error recovery and packet-based debugging

### Migration Path

1. **Current**: AgentTask routing works but lacks memory integration
2. **Next**: Wire v2.6 adapter's `_execute()` to call `handle_slack_with_l_agent()` internally
3. **Future**: Replace AgentTask call with direct AIOS runtime integration

This gives you v2.6 benefits (packets, idempotency, audit) while keeping AgentTask execution.

## Summary

**What's Currently Enabled**:
- ✅ All three Slack implementations are registered
- ✅ Legacy router is default (`L9_ENABLE_LEGACY_SLACK_ROUTER=true`)
- ✅ AgentTask routing available when flag is `false`
- ✅ v2.6 adapter ready but not primary yet

**Recommended Next Steps**:
1. Set `L9_ENABLE_LEGACY_SLACK_ROUTER=false` to enable AgentTask routing (immediate)
2. Wire v2.6 adapter's `_execute()` to use AgentTask routing (get v2.6 benefits)
3. Add `message.im` event subscription in Slack App for DM support
4. Test DM flow without @L mentions
5. Gradually migrate to direct AIOS runtime integration (future)

