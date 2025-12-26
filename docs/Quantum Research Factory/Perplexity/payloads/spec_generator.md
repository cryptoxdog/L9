# PERPLEXITY PAYLOAD: Module Spec Generator

Copy everything below this line and paste into Perplexity Labs:

---

You are a senior L9 system architect. Generate a **complete, production-ready Module Spec** in YAML format following the L9 Module-Spec-v2.5 schema.

## MODULE TO SPECIFY

**Name:** `slack_webhook_adapter`
**Description:** Receives inbound Slack webhook events, validates HMAC signatures, normalizes to PacketEnvelope format, routes to AIOS for processing, and posts replies back to Slack.

## CONTEXT

L9 is a modular AI orchestration system with:
- **PacketEnvelope protocol** for all inter-module communication
- **Memory Substrate** (PostgreSQL + pgvector) for persistence
- **AIOS runtime** at `/chat` endpoint for LLM processing
- **Tiers 0-7** for startup ordering (lower = earlier)
- **structlog** for logging (never `print` or `logging`)
- **httpx** for HTTP clients (never `requests` or `aiohttp`)

## REQUIREMENTS

Generate the COMPLETE YAML spec with ALL 26 sections filled in:

1. **metadata** - module_id, name, tier, description
2. **ownership** - team, primary_contact
3. **runtime_wiring** - service type, startup_phase, depends_on, blocks_startup
4. **runtime_contract** - runtime_class, execution_model
5. **external_surface** - http endpoint, webhook, tool exposure
6. **dependency_contract** - inbound callers, outbound targets
7. **dependencies** - allowed_tiers, outbound_calls with interfaces
8. **packet_contract** - emits list, requires_metadata
9. **packet_expectations** - on_success, on_error, durability
10. **idempotency** - pattern, source, durability
11. **error_policy** - default, retries, escalation, specific error handlers
12. **observability** - logs, metrics (counters/histograms), traces
13. **runtime_touchpoints** - db, tools, network, boot impact
14. **tier_expectations** - requires_runtime_wiring, packet_contract, negative_tests
15. **test_scope** - unit, integration, docker_smoke
16. **acceptance** - positive and negative test cases with IDs
17. **global_invariants_ack** - all invariants acknowledged
18. **spec_confidence** - level and basis
19. **repo** - root_path, allowed_new_files, allowed_modified_files
20. **interfaces** - inbound routes with auth, outbound calls with timeout
21. **environment** - required and optional env vars
22. **orchestration** - validation steps, context reads, aios calls, side effects
23. **boot_impact** - level and reason
24. **standards** - identity, logging, http_client
25. **goals** and **non_goals**
26. **notes_for_perplexity** - implementation guidance

## OUTPUT FORMAT

```yaml
# ============================================================================
# L9 MODULE SPEC — slack_webhook_adapter v2.5.0
# ============================================================================
schema_version: "2.5"

metadata:
  module_id: "slack_webhook_adapter"
  name: "Slack Webhook Adapter"
  tier: "4"
  description: "..."
  # ... continue with ALL sections
```

Generate the COMPLETE spec. Do not skip or abbreviate any section.
Do not use placeholders like `{{...}}` - fill in real, production-ready values.

