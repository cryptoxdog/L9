# SONAR DEEP RESEARCH — structlog_setup (Module 2 of 5)

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

**Module ID:** `structlog_setup`
**Name:** Structlog Configuration
**Tier:** 0 (Core Infrastructure - configures before any logging happens)
**Description:** Centralized structlog configuration for all L9 modules. Provides consistent JSON logging in production, pretty console output in development. Integrates with FastAPI request context.

# RESEARCH REQUIREMENTS

Conduct comprehensive research on:

1. **structlog configuration** — processors, formatters, context vars, bound loggers
2. **JSON logging for production** — structured output, log aggregation (ELK, Datadog)
3. **Development logging** — ConsoleRenderer, colors, human-readable output
4. **FastAPI integration** — request context, correlation IDs, middleware patterns
5. **Context variables** — thread-local vs contextvars, async-safe patterns
6. **Log levels and filtering** — per-module levels, suppressing noisy libraries
7. **Performance** — async logging, buffering, avoiding blocking I/O

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

# L9 LOGGING STANDARDS

```python
# REQUIRED pattern for all L9 modules:
import structlog
logger = structlog.get_logger(__name__)

# REQUIRED context fields:
logger.info(
    "event_name",
    thread_uuid=thread_uuid,
    correlation_id=correlation_id,
    elapsed_ms=elapsed_ms,
    # ... additional context
)

# FORBIDDEN:
import logging  # NEVER
print(...)      # NEVER
```

# OUTPUT FORMAT

Generate a COMPLETE Module-Spec-v2.5 YAML with ALL 26 sections.
Use your research findings to fill in REAL, production-ready values.

```yaml
# ============================================================================
# L9 MODULE SPEC — structlog_setup v2.5.0
# ============================================================================
schema_version: "2.5"

# SECTION 1: METADATA
metadata:
  module_id: "structlog_setup"
  name: "Structlog Configuration"
  tier: "0"
  description: "Centralized structlog configuration with JSON/console output modes"
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
  depends_on:
    - "config_loader"  # Needs config for LOG_LEVEL, LOG_FORMAT
  blocks_startup_on_failure: true

# Continue with ALL 26 sections...
# Include real structlog processor chains from research
# Include real FastAPI middleware patterns
# Include real contextvars patterns for async
```

# CRITICAL REQUIREMENTS

1. **Tier 0 semantics:** Must configure before ANY other module logs.
2. **Environment-aware:** JSON in production, pretty console in development.
3. **No packets:** Logging infrastructure does NOT emit PacketEnvelopes.
4. **Context propagation:** thread_uuid and correlation_id MUST propagate across async calls.
5. **Depends on config_loader:** Gets LOG_LEVEL, LOG_FORMAT from config.

Generate the COMPLETE specification with all 26 sections filled in.

---

# END OF PAYLOAD

