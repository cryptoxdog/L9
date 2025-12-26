# SONAR DEEP RESEARCH — packet_protocol (Module 3 of 5)

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

**Module ID:** `packet_protocol`
**Name:** Packet Protocol
**Tier:** 2 (Core Services - after infrastructure, before adapters)
**Description:** PacketEnvelope creation, validation, and serialization. Defines the canonical message format for all L9 inter-module communication. Provides factory functions, validation, and correlation ID propagation.

# RESEARCH REQUIREMENTS

Conduct comprehensive research on:

1. **Pydantic models for protocols** — BaseModel, Field, validators, serialization
2. **Message envelope patterns** — CloudEvents, envelope + payload, metadata propagation
3. **Correlation ID patterns** — UUID generation, propagation across services, tracing
4. **UUIDv5 deterministic IDs** — namespace-based generation, reproducibility
5. **JSON serialization** — Pydantic model_dump, orjson optimization, datetime handling
6. **Validation strategies** — input validation, schema evolution, backwards compatibility
7. **Type safety** — Literal types, discriminated unions, exhaustive matching

# L9 PACKET STRUCTURE

```python
# Canonical L9 Packet Structure (research and refine):
class PacketMetadata(BaseModel):
    task_id: str
    thread_uuid: UUID
    source: str
    tool_id: str
    correlation_id: UUID
    timestamp: datetime

class PacketProvenance(BaseModel):
    created_by: str
    created_at: datetime
    version: str

class PacketEnvelopeIn(BaseModel):
    packet_type: str  # e.g., "slack.in", "email.out", "aios.error"
    payload: Dict[str, Any]
    metadata: PacketMetadata
    provenance: PacketProvenance
```

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
# L9 MODULE SPEC — packet_protocol v2.5.0
# ============================================================================
schema_version: "2.5"

# SECTION 1: METADATA
metadata:
  module_id: "packet_protocol"
  name: "Packet Protocol"
  tier: "2"
  description: "PacketEnvelope creation, validation, and serialization for L9 IPC"
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
  startup_phase: "normal"
  depends_on:
    - "config_loader"
    - "structlog_setup"
  blocks_startup_on_failure: true

# Continue with ALL 26 sections...
# Include real Pydantic patterns from research
# Include real correlation ID propagation patterns
# Include real UUIDv5 generation patterns
```

# CRITICAL REQUIREMENTS

1. **Tier 2 semantics:** Core service that higher tiers depend on.
2. **This IS the packet contract:** All other modules import from here.
3. **UUIDv5 for thread_uuid:** Deterministic, reproducible, testable.
4. **Factory functions:** `create_packet()`, `create_inbound_packet()`, etc.
5. **Validation:** Invalid packets MUST raise, never silently pass.
6. **No HTTP endpoints:** This is a library, not a service.

Generate the COMPLETE specification with all 26 sections filled in.

---

# END OF PAYLOAD

