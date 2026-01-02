# Slack Adapter Documentation

## Overview

L9 has **two Slack integration implementations** that coexist:

1. **Slack Routes (v2.0+)** - Primary working implementation (`api/routes/slack.py`)
2. **Legacy Webhook Handler** - Original implementation (`api/webhook_slack.py`)

## Current Status

### What's Enabled

Both implementations are **conditionally registered** based on `SLACK_APP_ENABLED`:

- **Slack Routes (v2.0+)**: Registered in `api/server.py` if `_has_slack` is True AND `settings.slack_app_enabled` is True
- **Legacy Webhook**: Registered in `api/server_memory.py` if `settings.slack_app_enabled` is True (behavior gated by `L9_ENABLE_LEGACY_SLACK_ROUTER`)

**Note**: The v2.6 adapter in `api/adapters/slack_adapter/` exists but is incomplete (stub implementation). It is not used for production processing.

**Initialization Requirements**:
- Both `api/server.py` and `api/server_memory.py` validate `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` before initializing
- If tokens are missing, routes are NOT mounted (fail-safe behavior)
- Configuration is loaded from `IntegrationSettings` in `config/settings.py` (falls back to `os.getenv`)

### Feature Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `SLACK_APP_ENABLED` | `false` | Master toggle for all Slack functionality |
| `L9_ENABLE_LEGACY_SLACK_ROUTER` | `true` | When `false`, routes through AgentTask + L-CTO agent instead of legacy handlers |

## Architecture

### 1. Slack Routes (v2.0+) - Primary Implementation

**Location**: `api/routes/slack.py`

**Routes**:
- `POST /slack/events` - Events API handler
- `POST /slack/commands` - Slash command handler

**Features**:
- HMAC-SHA256 signature validation via `SlackRequestValidator`
- Request normalization via `SlackRequestNormalizer`
- Routes to memory ingestion layer (`memory/slack_ingest.py`)
- HTTP POST to `/chat` endpoint for processing (not AIOS runtime object)
- Posts replies back to Slack via `SlackAPIClient`
- Packet emission to memory substrate (`slack.in`, `slack.out`, `slack.command`)
- Dependency injection via FastAPI `Depends`

**Initialization**: 
- Validator and client initialized in `api/server.py` lifespan (if `settings.slack_app_enabled` is True)
- Configuration loaded from `IntegrationSettings` (`config/settings.py`) with fallback to `os.getenv`
- Tokens validated before initialization; if missing, adapter is not initialized (no routes mounted)
- Stored in `app.state.slack_validator` and `app.state.slack_client`
- `app.state.aios_base_url` set to `AIOS_BASE_URL` env var (default: `http://localhost:8000`)

**Processing Flow**:
```
Slack Event → /slack/events (api/routes/slack.py)
  → Signature validation
  → handle_slack_events() (memory/slack_ingest.py)
  → HTTP POST to {aios_base_url}/chat
  → Post reply to Slack via SlackAPIClient
  → Store packets in memory substrate
```

### 2. Legacy Webhook Handler

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

### Primary Flow (Slack Routes)

```
Slack Event → POST /slack/events (api/routes/slack.py)
  → Signature validation (SlackRequestValidator)
  → handle_slack_events() (memory/slack_ingest.py)
  → Dedupe check (event_id lookup)
  → Retrieve thread context from memory
  → HTTP POST to {aios_base_url}/chat
  → Post reply to Slack (SlackAPIClient.post_message)
  → Store inbound/outbound packets in memory substrate
```

### Legacy Flow (Legacy Router Enabled)

```
Slack Event → /slack/events (webhook_slack.py)
  → Legacy routing (if L9_ENABLE_LEGACY_SLACK_ROUTER=true)
  → OR handle_slack_with_l_agent() → AgentTask → L-CTO (if flag=false)
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

### Required (for Slack integration to work)
```bash
SLACK_SIGNING_SECRET=xoxb-...  # From Slack App → Basic Information → Signing Secret
SLACK_BOT_TOKEN=xoxb-...       # From Slack App → OAuth & Permissions → Bot User OAuth Token
```

### Optional (but recommended)
```bash
SLACK_APP_ENABLED=true          # Master toggle (must be true for routes to mount)
L9_ENABLE_LEGACY_SLACK_ROUTER=false  # Use AgentTask routing (recommended)
AIOS_BASE_URL=http://localhost:8000  # Base URL for /chat endpoint (default: http://localhost:8000)
```

### Future OAuth Variables (defined in settings, not currently used)
```bash
SLACK_APP_ID=...              # For future OAuth installation flows
SLACK_CLIENT_ID=...           # For future OAuth installation flows
SLACK_CLIENT_SECRET=...       # For future OAuth installation flows
SLACK_VERIFICATION_TOKEN=...  # Legacy token (for future OAuth flows)
```

**Configuration Loading**:
- All variables are loaded via `IntegrationSettings` in `config/settings.py`
- Falls back to `os.getenv()` if settings module unavailable
- Variables can be set in `.env` file or environment

## Testing

### Unit Tests
```bash
pytest api/adapters/slack_adapter/tests/test_slack_webhook.py
```

### Integration Tests
```bash
pytest api/adapters/slack_adapter/tests/test_slack_webhook_integration.py
```

## Implementation Details

### How Processing Works

The primary implementation (`api/routes/slack.py` → `memory/slack_ingest.py`) processes Slack events as follows:

1. **Signature Validation**: HMAC-SHA256 verification using `SLACK_SIGNING_SECRET`
2. **Request Normalization**: Extracts thread UUID, event ID, user/channel info
3. **Deduplication**: Checks for duplicate `event_id` in memory substrate
4. **Context Retrieval**: Fetches thread history and semantic hits from memory
5. **Processing**: HTTP POST to `/chat` endpoint (not an AIOS runtime object)
6. **Reply**: Posts response back to Slack via `SlackAPIClient`
7. **Persistence**: Stores `slack.in` and `slack.out` packets in memory substrate

**Note**: The `/chat` endpoint is a standard HTTP endpoint, not an AIOS runtime integration. The code makes HTTP POST requests to `{AIOS_BASE_URL}/chat` (default: `http://localhost:8000/chat`).

## Troubleshooting

### Slack adapter not initializing
- Check: `SLACK_SIGNING_SECRET` and `SLACK_BOT_TOKEN` are set in environment or `.env` file
- Check: `SLACK_APP_ENABLED=true` (required for initialization)
- Check logs for: "Slack adapter not initialized: SLACK_SIGNING_SECRET or SLACK_BOT_TOKEN not set"
- **Note**: If tokens are missing, routes are NOT mounted (fail-safe). Check both `api/server.py` and `api/server_memory.py` logs.

### Events not received
- Verify Request URL in Slack App settings matches your server
- Check that `url_verification` challenge is handled correctly
- Ensure event subscriptions are enabled in Slack App dashboard

### Messages not routing to L-CTO
- Check: `L9_ENABLE_LEGACY_SLACK_ROUTER=false` (to use AgentTask path)
- Verify: `app.state.agent_executor` is initialized in `server.py`
- Check logs for: "handle_slack_with_l_agent: agent_executor not available"

## Related Files

- `api/routes/slack.py` - Primary working implementation (v2.0+ routes)
- `memory/slack_ingest.py` - Core processing logic (HTTP /chat calls, packet storage)
- `api/slack_adapter.py` - Validation/normalization utilities
- `api/slack_client.py` - Slack API client for posting replies
- `api/webhook_slack.py` - Legacy implementation
- `l-cto/slack.scope.md` - OAuth scopes reference
- `igor/slack enabling.md` - GMP prompt for enabling DM routing

## Summary

**What's Currently Enabled**:
- ✅ Slack Routes (v2.0+) - Primary working implementation
- ✅ Legacy webhook handler - Available but gated by `L9_ENABLE_LEGACY_SLACK_ROUTER`
- ✅ Packet emission to memory substrate (`slack.in`, `slack.out`, `slack.command`)
- ✅ HTTP integration with `/chat` endpoint (not AIOS runtime object)

**Key Implementation Notes**:
- Processing uses HTTP POST to `/chat` endpoint, not an AIOS runtime integration
- All packets are stored in memory substrate for audit trail
- Signature validation is mandatory (fail-closed security)
- Deduplication prevents duplicate processing of Slack retries
- Configuration is centralized in `IntegrationSettings` (`config/settings.py`)
- Token validation happens before route mounting (fail-safe: missing tokens = no routes)
- Both `api/server.py` and `api/server_memory.py` independently validate and initialize Slack components

