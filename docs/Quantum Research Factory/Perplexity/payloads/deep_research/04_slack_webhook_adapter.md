# SONAR DEEP RESEARCH — slack_webhook_adapter (Module 4 of 5)

## API Payload (for curl/httpx)

```json
{
  "model": "sonar-deep-research",
  "messages": [{"role": "user", "content": "SEE_PROMPT_BELOW"}],
  "temperature": 0.2,
  "max_tokens": 8000
}
```

---

## PROMPT (Copy everything below for Perplexity Labs)

---

You are a senior L9 system architect conducting deep research to generate a production-ready Module Specification.

# MODULE TO SPECIFY

**Module ID:** `slack_webhook_adapter`
**Name:** Slack Webhook Adapter
**Tier:** 4 (External Adapters - receives external webhooks)
**Description:** Receives inbound Slack webhook events, validates HMAC-SHA256 signatures, normalizes to PacketEnvelope format, routes to AIOS for processing, and posts replies back to Slack using Web API.

# RESEARCH REQUIREMENTS

Conduct comprehensive research on:

1. **Slack Events API** — webhook payload structure, event types, challenge verification
2. **Slack signature verification** — HMAC-SHA256 with `X-Slack-Signature`, `X-Slack-Request-Timestamp`
3. **Slack Web API** — chat.postMessage, response formatting, rate limits
4. **Timestamp validation** — replay attack prevention, 5-minute window
5. **Idempotency** — using `event_id` for deduplication, at-least-once delivery
6. **FastAPI webhook handling** — raw body access, header extraction, async handlers
7. **Error handling** — what to return to Slack, 3-second timeout requirement
8. **Slack rate limits** — Tier 1-4 methods, burst handling, 429 responses

# L9 SYSTEM CONTEXT

```yaml
system: L9
core_protocol: PacketEnvelope
memory: PostgreSQL + pgvector (for packet storage)
cache: Redis (for idempotency cache)
logging: structlog (NEVER print or logging module)
http_client: httpx (NEVER requests or aiohttp)
startup_tiers: 0-7 (lower = earlier)
aios_endpoint: /chat
root_path: /Users/ib-mac/Projects/L9
```

# OUTPUT FORMAT

Generate a COMPLETE Module-Spec-v2.5 YAML with ALL 26 sections.
Use your research findings to fill in REAL Slack-specific values.

```yaml
# ============================================================================
# L9 MODULE SPEC — slack_webhook_adapter v2.5.0
# ============================================================================
schema_version: "2.5"

# SECTION 1: METADATA
metadata:
  module_id: "slack_webhook_adapter"
  name: "Slack Webhook Adapter"
  tier: "4"
  description: "Slack Events API webhook handler with HMAC verification and reply posting"
  system: "L9"
  language: "python"
  runtime: "python>=3.11"

# SECTION 2: OWNERSHIP
ownership:
  team: "integrations"
  primary_contact: "integrations_engineer"

# SECTION 3: RUNTIME WIRING
runtime_wiring:
  service: "api"
  startup_phase: "normal"
  depends_on:
    - "config_loader"
    - "structlog_setup"
    - "packet_protocol"
    - "memory_substrate"
    - "redis_cache"
  blocks_startup_on_failure: false  # Slack adapter failure shouldn't block boot

# Continue with ALL 26 sections...
# Include REAL Slack headers: X-Slack-Signature, X-Slack-Request-Timestamp
# Include REAL Slack event types: message, app_mention, etc.
# Include REAL Slack API endpoints: chat.postMessage
# Include REAL rate limit handling patterns
```

# CRITICAL REQUIREMENTS

1. **HMAC-SHA256 verification:** Use `X-Slack-Signature` header, reject invalid.
2. **Timestamp validation:** Reject if `X-Slack-Request-Timestamp` > 5 minutes old.
3. **Challenge verification:** Handle `url_verification` event type.
4. **3-second response:** Acknowledge within 3s, process async if needed.
5. **Idempotency:** Use Slack's `event_id` to deduplicate.
6. **Packet emission:** Emit `slack.in`, `slack.out`, `slack.error` packets.

Generate the COMPLETE specification with all 26 sections filled in.

---

# END OF PAYLOAD

