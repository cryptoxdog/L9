# Legacy Slack Implementation — ARCHIVED

## Archive Date: 2026-01-08

## Files Archived

| File | Original Location | Lines | Reason |
|------|-------------------|-------|--------|
| `webhook_slack.py` | `api/webhook_slack.py` | 960 | Never registered in server.py, superseded by routes/slack.py |
| `test_webhook_slack.py` | `tests/api/test_webhook_slack.py` | 999 | Tests legacy module, not the active implementation |

## Active Slack Implementation

Slack integration is now handled by:

```
api/routes/slack.py          ← FastAPI routes (POST /slack/events, /slack/commands)
    ↓
memory/slack_ingest.py       ← Orchestration, memory packets, L-CTO routing
    ↓
api/slack_adapter.py         ← Utilities: SlackRequestValidator, SlackRequestNormalizer
```

## What Was Ported

The useful parts from `webhook_slack.py` were ported to `memory/slack_ingest.py`:

- ✅ Slack signature verification → `api/slack_adapter.py:SlackRequestValidator`
- ✅ Event normalization → `api/slack_adapter.py:SlackRequestNormalizer`
- ✅ L-CTO agent routing → `memory/slack_ingest.py:handle_slack_with_l_agent()`
- ✅ Thread UUID generation → `memory/slack_ingest.py:_generate_thread_uuid()`
- ⚠️ EventDedupeCache → Stub in `memory/slack_ingest.py:_check_duplicate()` (real impl deferred)

## Why Archived

1. **Not registered** — `api/server.py` explicitly said "NOT USED" (lines 307-308)
2. **Duplicate functionality** — All features exist in `api/routes/slack.py` + `memory/slack_ingest.py`
3. **Confusing** — Three implementations caused confusion about which to use

## Do NOT Restore

This code should NOT be restored. If you need Slack functionality:

1. Use `api/routes/slack.py` for HTTP routes
2. Use `memory/slack_ingest.py` for event handling logic
3. Use `api/slack_adapter.py` for validation utilities

## Related Archive

- `_archived/codegen_slack_adapter/` — Generated v2.6 adapter that was never deployed

