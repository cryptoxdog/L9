# 🔬 SONAR DEEP RESEARCH - Module Spec Generator

## ⚠️ Important Notes

- **Model:** `sonar-deep-research`
- **Rate Limit:** 5 requests per minute (1 every 12 seconds)
- **Response Time:** 2-5 minutes per query (autonomous research)
- **Sources:** Will analyze 50-200+ sources automatically
- **Cost:** $0.50-$2.00 per query

## Endpoint & Payload Format

**Endpoint:** `POST https://api.perplexity.ai/chat/completions`

**Or Async (for very long research):**
- Create: `POST https://api.perplexity.ai/async/chat/completions`
- Poll: `GET https://api.perplexity.ai/async/chat/completions/{request_id}`

---

# PAYLOAD - Copy for API call or Perplexity Labs

```json
{
  "model": "sonar-deep-research",
  "messages": [
    {
      "role": "user", 
      "content": "You are a senior L9 system architect. Conduct comprehensive research and generate a complete Module-Spec-v2.5 YAML for:\n\n**Module:** `slack_webhook_adapter`\n**Description:** Receives inbound Slack webhook events, validates HMAC signatures, normalizes to PacketEnvelope format, routes to AIOS for processing, and posts replies back to Slack.\n\n## Research Requirements\n\n1. Research Slack's Event API and webhook signature verification (HMAC-SHA256)\n2. Research FastAPI webhook handling best practices\n3. Research async HTTP client patterns with httpx\n4. Research idempotency patterns for webhook handling\n5. Research error handling for external API integrations\n\n## L9 Context\n\n- PacketEnvelope protocol for inter-module communication\n- PostgreSQL + pgvector memory substrate\n- structlog for logging (never print/logging)\n- httpx for HTTP (never requests/aiohttp)\n- Tiers 0-7 startup ordering\n\n## Output\n\nGenerate a COMPLETE Module-Spec-v2.5 YAML with all 26 sections filled in with researched, production-ready values. Include specific Slack API details discovered during research."
    }
  ],
  "temperature": 0.2,
  "max_tokens": 8000
}
```

---

# For Perplexity Labs UI (Copy Everything Below)

---

You are a senior L9 system architect conducting deep research. Generate a complete Module-Spec-v2.5 YAML.

## MODULE TO SPECIFY

**Module:** `slack_webhook_adapter`
**Description:** Receives inbound Slack webhook events, validates HMAC signatures, normalizes to PacketEnvelope format, routes to AIOS for processing, and posts replies back to Slack.

## DEEP RESEARCH REQUIREMENTS

Conduct comprehensive research on:

1. **Slack Event API** - webhook payload structure, event types, challenge verification
2. **Slack Signature Verification** - HMAC-SHA256 with `X-Slack-Signature` and `X-Slack-Request-Timestamp`
3. **FastAPI Webhook Patterns** - dependency injection, request body handling, async handlers
4. **Idempotency Strategies** - deduplication using `event_id` or composite keys
5. **Error Handling** - what to return to Slack, retry behavior, timeout handling
6. **Rate Limiting** - Slack's rate limits and how to handle them
7. **Security Best Practices** - timestamp validation (< 5 min), signature caching

## L9 SYSTEM CONTEXT

```yaml
# L9 is a modular AI orchestration system
system: L9
core_protocol: PacketEnvelope
memory: PostgreSQL + pgvector (memory substrate)
cache: Redis
logging: structlog (NEVER print or logging module)
http_client: httpx (NEVER requests or aiohttp)
startup_tiers: 0-7 (lower = earlier)
aios_endpoint: /chat
```

## OUTPUT FORMAT

Generate the COMPLETE Module-Spec-v2.5 YAML with ALL 26 sections:

1. metadata (module_id, name, tier, description)
2. ownership (team, contact)
3. runtime_wiring (service, startup_phase, depends_on)
4. runtime_contract (runtime_class, execution_model)
5. external_surface (http, webhook, tool exposure)
6. dependency_contract (inbound, outbound)
7. dependencies (allowed_tiers, outbound_calls)
8. packet_contract (emits, requires_metadata)
9. packet_expectations (on_success, on_error, durability)
10. idempotency (pattern, source, durability)
11. error_policy (default, retries, specific handlers)
12. observability (logs, metrics, traces)
13. runtime_touchpoints (db, tools, network, boot)
14. tier_expectations (requirements by tier)
15. test_scope (unit, integration, smoke)
16. acceptance (positive + negative test cases)
17. global_invariants_ack
18. spec_confidence
19. repo (file manifest)
20. interfaces (inbound routes, outbound calls)
21. environment (required + optional env vars)
22. orchestration (validation, context, aios, side effects)
23. boot_impact
24. standards (identity, logging, http)
25. goals + non_goals
26. notes_for_perplexity

**Use your research findings to fill in REAL values** - Slack-specific headers, endpoints, error codes, rate limits, etc.

---

# END OF DEEP RESEARCH PAYLOAD

