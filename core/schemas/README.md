# L9 Core Schemas

> Canonical schema definitions for the L9 platform.

## Overview

This directory contains:
- **Pydantic models** — Runtime type definitions
- **YAML specs** — Schema documentation
- **Validation tests** — Schema conformance tests

## Contents

| File | Purpose |
|------|---------|
| `Memory.yaml` | PacketEnvelope schema specification (v1.1.0) |
| `packet_envelope.py` | Core PacketEnvelope Pydantic model |
| `universal_schema.py` | Universal schema utilities |
| `research_factory_*.py` | Research factory schemas |
| `plasticos_memory_substrate_*.yaml` | Module schema spec |

## PacketEnvelope (v1.1.0)

The canonical event container for all memory substrate operations.

### Core Fields (Required)
- `packet_id` — UUID identifier
- `packet_type` — Semantic category
- `timestamp` — UTC timestamp
- `payload` — Arbitrary JSON payload

### v1.1.0 Extensions
- `thread_id` — Conversation threading
- `lineage` — DAG-style parent tracking
- `tags` — Lightweight labels
- `ttl` — Expiration timestamp

## Schema Alignment

```
Memory.yaml          ←→  substrate_models.py
(YAML spec)               (Pydantic runtime)
     ↓                           ↓
packet_store DB    ←→    PacketStoreRow DTO
```

## Validation

```bash
# Run schema tests
pytest tests/ -k "test_packet_envelope"
```

## Adding New Schemas

1. Define YAML spec in this directory
2. Create Pydantic model in corresponding `.py`
3. Add tests in `tests/`
4. Update `__init__.py` exports

---

*L9 Platform — Core Schemas*

