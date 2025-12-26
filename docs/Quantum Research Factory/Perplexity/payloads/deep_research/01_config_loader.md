# SONAR DEEP RESEARCH — config_loader (Module 1 of 5)

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

**Module ID:** `config_loader`
**Name:** Configuration Loader
**Tier:** 0 (Core Infrastructure - loads before everything else)
**Description:** Environment and YAML configuration management with validation. Provides typed access to all L9 configuration via Pydantic Settings. Fails fast on missing required environment variables.

# RESEARCH REQUIREMENTS

Conduct comprehensive research on:

1. **Pydantic Settings v2** — BaseSettings, environment variable binding, nested models, validation
2. **Python-dotenv patterns** — .env file loading, precedence rules, development vs production
3. **YAML configuration loading** — PyYAML, safe loading, schema validation
4. **12-Factor App config** — environment variable best practices, secrets handling
5. **FastAPI lifespan integration** — startup configuration, dependency injection
6. **Fail-fast patterns** — ValidationError handling, boot-time validation
7. **Configuration hot-reload** — when to support, when to avoid

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
# L9 MODULE SPEC — config_loader v2.5.0
# ============================================================================
schema_version: "2.5"

# SECTION 1: METADATA
metadata:
  module_id: "config_loader"
  name: "Configuration Loader"
  tier: "0"
  description: "Environment and YAML configuration management with Pydantic validation"
  system: "L9"
  language: "python"
  runtime: "python>=3.11"

# SECTION 2: OWNERSHIP
ownership:
  team: "core"
  primary_contact: "platform_engineer"

# SECTION 3: RUNTIME WIRING
runtime_wiring:
  service: "api"
  startup_phase: "early"
  depends_on: []  # Tier 0 - no dependencies
  blocks_startup_on_failure: true  # Missing config = hard failure

# Continue with ALL 26 sections...
# Include real Pydantic Settings patterns from research
# Include real .env handling patterns
# Include real validation error handling
```

# CRITICAL REQUIREMENTS

1. **Tier 0 semantics:** This loads FIRST. Cannot depend on any other L9 module.
2. **Fail-fast:** Missing required env vars MUST crash at startup, not at runtime.
3. **No packets:** Config loader does NOT emit PacketEnvelopes (it's infrastructure).
4. **Single source:** All other modules get config via dependency injection from this.
5. **Type safety:** All config values must be typed via Pydantic, no Dict[str, Any].

Generate the COMPLETE specification with all 26 sections filled in.

---

# END OF PAYLOAD

