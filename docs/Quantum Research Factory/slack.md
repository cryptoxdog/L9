# Slack Adapter for L9

This document describes the Slack integration for the L9 AI OS. It provides:
- Webhook handlers for Slack Events API and slash commands
- Message routing to AIOS `/chat` endpoint
- Full packet persistence in the memory substrate
- Thread-aware deduplication and context retrieval

## Quick Start

### 1. Slack App Setup

Create a Slack app at https://api.slack.com/apps:

1. **Events API**:
   - Enable "Events Subscriptions"
   - Request URL: `https://<your-domain>/slack/events`
   - Subscribe to bot events:
     - `message.channels` (channel messages)
     - `app_mention` (bot mentions)

2. **Slash Commands**:
   - Create a new command: `/l9`
   - Request URL: `https://<your-domain>/slack/commands`
   - Submit on load: disabled

3. **OAuth & Permissions**:
   - Scopes needed:
     - `chat:write` (post messages)
     - `channels:read` (view channels)
   - Copy **Bot User OAuth Token** (xoxb-...)

4. **Signing Secret**:
   - From **Basic Information**, copy **Signing Secret** (verify webhook requests)

### 2. Environment Variables

Create a `.env` file with:

```bash
# Slack Integration
SLACK_SIGNING_SECRET=<your-signing-secret>
SLACK_BOT_TOKEN=<your-bot-token>

# AIOS
AIOS_BASE_URL=http://localhost:8000
DATABASE_URL=postgresql://user:pass@localhost/l9
```

### 3. FastAPI App Integration

In your main app file (e.g., `api/server.py`):

```python
from fastapi import FastAPI
from api.routes.slack import router as slack_router
from memory.substrate_service import init_service
from api.slack_adapter import SlackRequestValidator
from api.slack_client import SlackAPIClient
import httpx
import os

app = FastAPI()

# Include Slack routes
app.include_router(slack_router)

@app.on_event("startup")
async def startup_event():
    # Initialize memory substrate
    substrate_service = await init_service(
        database_url=os.environ["DATABASE_URL"],
    )
    
    # Initialize Slack components
    validator = SlackRequestValidator(os.environ["SLACK_SIGNING_SECRET"])
    http_client = httpx.AsyncClient()
    slack_client = SlackAPIClient(
        bot_token=os.environ["SLACK_BOT_TOKEN"],
        http_client=http_client,
    )
    
    # Store in app state for route dependencies
    app.state.slack_validator = validator
    app.state.substrate_service = substrate_service
    app.state.slack_client = slack_client
    app.state.aios_base_url = os.environ.get("AIOS_BASE_URL", "http://localhost:8000")
    app.state.http_client = http_client

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup
    if hasattr(app.state, "http_client"):
        await app.state.http_client.aclose()
    if hasattr(app.state, "substrate_service"):
        from memory.substrate_service import close_service
        await close_service()
```

## Architecture

### Request Flow

```
┌─────────────┐
│ Slack       │
│ Event/Cmd   │
└──────┬──────┘
       │
       │ HTTP POST (signature verified)
       ▼
┌─────────────────────┐
│ /slack/events or    │
│ /slack/commands     │
└──────┬──────────────┘
       │
       │ Parse + Normalize (deterministic thread UUID)
       │
       ▼
┌──────────────────────┐
│ Dedupe Check         │
│ (event_id based)     │
└──────┬───────────────┘
       │
       ├─ Already seen? Return 200 ACK
       │
       └─ New? Continue...
          │
          ├─ Retrieve thread context (semantic search)
          │
          ├─ Call AIOS /chat
          │
          ├─ Store inbound packet
          │
          ├─ Post reply to Slack
          │
          └─ Store outbound packet
```

### Thread Model

All Slack messages belong to a thread, identified by:
- **Thread UUID**: Deterministic UUIDv5 from `team_id:channel_id:thread_ts`
- **Thread String**: Human-readable `slack:T123:C456:1234567890.123456`

The UUID is used internally in the database; the string is stored in packet metadata for observability.

### Packet Types

**Inbound**:
- `slack.in`: A message posted in Slack
- `slack.command`: A slash command invocation

**Outbound**:
- `slack.out`: L9's reply to a message
- `slack.command.response`: L9's response to a command

All packets are immutable and stored in the substrate with full provenance tracking.

### Error Handling

| Scenario | HTTP Response | Action |
|----------|---------------|--------|
| Invalid signature | 401 | Reject, no further processing |
| Invalid JSON | 400 | Reject, no further processing |
| Internal error | 200 | Log error, return OK to Slack (prevent retry loop) |
| AIOS timeout | 200 | Log error, reply with fallback message |
| Slack post fails | 200 | Log error, store error packet |

## Testing

### Unit Tests

Run the test suite:

```bash
pytest tests/test_slack_adapter.py -v
```

Coverage includes:
- Signature verification (pass/fail)
- URL verification challenge
- Thread UUID determinism
- Request parsing and normalization

### Local Testing

**Test Events API**:

```bash
# 1. Start L9 locally
python main.py

# 2. Use ngrok to expose local server
ngrok http 8000

# 3. Update Slack app Events URL to https://<ngrok-url>/slack/events

# 4. Post a message in a Slack channel where the bot is a member

# 5. Check logs for detailed flow
```

**Test Slash Commands**:

```bash
# 1. Ensure Slack app has command registered (/l9)

# 2. In Slack, type: /l9 do make me a summary of our conversation

# 3. Should respond with "Processing your command..." immediately

# 4. After a few seconds, L9 posts the response in channel
```

## Troubleshooting

### Webhook Verification Failing

- Check `SLACK_SIGNING_SECRET` is correct (from Slack app settings)
- Check request timestamp is within 5 minutes of server time
- Ensure webhook URL is publicly accessible

### Bot Not Replying

- Check bot is a member of the channel
- Check `/chat` endpoint is reachable at `AIOS_BASE_URL`
- Check logs for `aios_chat_error` messages
- Ensure bot has `chat:write` permission in Slack

### Duplicate Replies

- Check deduplication logic is working (look for `slack_event_deduplicated` in logs)
- Verify `packet_store` table has unique constraint on `event_id` (in metadata)

### Memory Not Persisting

- Check `DATABASE_URL` is valid and reachable
- Check migrations have run (including `packet_store`, `semantic_memory` tables)
- Check substrate service is initialized on app startup

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SLACK_SIGNING_SECRET` | Yes | Slack app signing secret |
| `SLACK_BOT_TOKEN` | Yes | Slack bot token (xoxb-...) |
| `AIOS_BASE_URL` | Yes | Base URL for AIOS /chat endpoint |
| `DATABASE_URL` | Yes | Postgres DSN for memory substrate |

### Thread Tolerance

- **Signature timestamp tolerance**: 300 seconds (5 minutes)
- Default; not configurable in current version

### Retry Behavior

- **Slack retries**: We return 200 for all internal errors (prevent infinite retry loops)
- **AIOS timeout**: 10 seconds
- **Slack API timeout**: 10 seconds

## Limitations

- No support for interactive components (buttons, menus) yet
- Slash commands process asynchronously (ACK → 200 OK → async reply)
- No rate limiting (relies on Slack API rate limits + app rate limiting)
- Semantic search requires embedding vectors (uses stub provider by default)

## Future Work

- [ ] Thread context retrieval (fetch recent messages in thread)
- [ ] Semantic search integration (find related knowledge)
- [ ] Slash command subcommands (structured `/l9 do <task>` parsing)
- [ ] Slack API rate limiting / circuit breaker
- [ ] Rich message formatting (blocks, threading)
- [ ] User authentication / permission checks

