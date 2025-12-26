# SONAR DEEP RESEARCH — health_routes (Module 5 of 5)

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

**Module ID:** `health_routes`
**Name:** Health Check Routes
**Tier:** 5 (API Routes - exposes HTTP endpoints)
**Description:** FastAPI health check endpoints for L9 API server. Provides `/health` (simple), `/health/ready` (dependencies checked), and `/health/live` (liveness probe) endpoints for Kubernetes and Docker health checks.

# RESEARCH REQUIREMENTS

Conduct comprehensive research on:

1. **Kubernetes health probes** — liveness vs readiness vs startup probes, timing
2. **Docker HEALTHCHECK** — CMD patterns, intervals, retries, start period
3. **FastAPI health endpoints** — async dependency checks, timeout handling
4. **Database health checks** — PostgreSQL connection validation, query patterns
5. **Redis health checks** — PING command, connection pool validation
6. **Graceful degradation** — partial health, dependency status reporting
7. **Health check response formats** — simple vs detailed, JSON structure

# L9 SYSTEM CONTEXT

```yaml
system: L9
core_protocol: PacketEnvelope
memory: PostgreSQL + pgvector
cache: Redis
logging: structlog (NEVER print or logging module)
http_client: httpx (NEVER requests or aiohttp)
startup_tiers: 0-7 (lower = earlier)
root_path: /Users/ib-mac/Projects/L9
```

# OUTPUT FORMAT

Generate a COMPLETE Module-Spec-v2.5 YAML with ALL 26 sections.
Use your research findings to fill in REAL, production-ready values.

```yaml
# ============================================================================
# L9 MODULE SPEC — health_routes v2.5.0
# ============================================================================
schema_version: "2.5"

# SECTION 1: METADATA
metadata:
  module_id: "health_routes"
  name: "Health Check Routes"
  tier: "5"
  description: "Kubernetes/Docker health check endpoints for L9 API"
  system: "L9"
  language: "python"
  runtime: "python>=3.11"

# SECTION 2: OWNERSHIP
ownership:
  team: "infra"
  primary_contact: "platform_engineer"

# SECTION 3: RUNTIME WIRING
runtime_wiring:
  service: "api"
  startup_phase: "late"  # Health routes register after other routes
  depends_on:
    - "config_loader"
    - "structlog_setup"
    - "postgres_pool"  # To check DB health
    - "redis_cache"    # To check Redis health
  blocks_startup_on_failure: false  # Health routes not critical to boot

# Continue with ALL 26 sections...
# Include REAL Kubernetes probe patterns from research
# Include REAL Docker HEALTHCHECK patterns
# Include REAL PostgreSQL/Redis check queries
```

# CRITICAL REQUIREMENTS

1. **Three endpoints:**
   - `GET /health` — Simple 200 OK (for load balancers)
   - `GET /health/live` — Liveness probe (is the process alive?)
   - `GET /health/ready` — Readiness probe (can it serve traffic?)
2. **Dependency checks in /health/ready:** Check PostgreSQL, Redis, critical services.
3. **Fast response:** Health checks MUST respond < 1 second.
4. **No packets:** Health routes do NOT emit PacketEnvelopes.
5. **No authentication:** Health endpoints MUST be public.

Generate the COMPLETE specification with all 26 sections filled in.

---

# END OF PAYLOAD

