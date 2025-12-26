# 🚀 QUICK TEST - COPY THIS ENTIRE BLOCK TO PERPLEXITY LABS

---

You are a senior L9 system architect. Generate a complete Module-Spec-v2.5 YAML for the following module:

**Module:** `health_routes`
**Description:** FastAPI health check endpoints for L9 API server. Provides /health (simple), /health/ready (dependencies checked), and /health/live (liveness probe) endpoints.

## L9 CONTEXT

- **Tiers 0-7** startup ordering (0=first, 7=last)
- **PacketEnvelope** protocol for all inter-module communication
- **structlog** only for logging (never print/logging module)
- **httpx** only for HTTP (never requests/aiohttp)
- **PostgreSQL + pgvector** for memory substrate
- **Redis** for caching

## GENERATE COMPLETE YAML

Include ALL 26 sections of Module-Spec-v2.5:

```yaml
# ============================================================================
# L9 MODULE SPEC — health_routes v2.5.0
# ============================================================================
schema_version: "2.5"

# SECTION 1: METADATA
metadata:
  module_id: "health_routes"
  name: "Health Check Routes"
  tier: "5"  # API routes tier
  description: "FastAPI health check endpoints for L9 API server"
  system: "L9"
  language: "python"
  runtime: "python>=3.11"

# SECTION 2: OWNERSHIP
ownership:
  team: "core"
  primary_contact: "platform_engineer"

# Continue with ALL sections 3-26...
# - runtime_wiring
# - runtime_contract
# - external_surface
# - dependency_contract
# - dependencies
# - packet_contract
# - packet_expectations
# - idempotency
# - error_policy
# - observability
# - runtime_touchpoints
# - tier_expectations
# - test_scope
# - acceptance (positive and negative tests)
# - global_invariants_ack
# - spec_confidence
# - repo (file manifest)
# - interfaces (routes)
# - environment (env vars)
# - orchestration
# - boot_impact
# - standards
# - goals / non_goals
# - notes_for_perplexity
```

Generate the COMPLETE spec with real values. No placeholders like `{{...}}`.
This is a simple module - health checks don't emit packets or have complex dependencies.
Focus on: correct tier, correct interfaces, correct test coverage.

---

# END OF PAYLOAD - Copy everything above

