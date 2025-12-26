# PacketEnvelope Reference

> **Schema Version:** 1.1.0  
> **Last Updated:** 2025-12-07  
> **Implementation:** `L9/memory/substrate_models.py`  
> **Schema Spec:** `L9/core/schemas/Memory.yaml`

## Overview

`PacketEnvelope` is the **canonical event container** for the L9 Memory Substrate. Every agent event, memory write, reasoning trace, and insight flows through the system wrapped in a PacketEnvelope.

**Key Properties:**
- Immutable once written to `packet_store`
- Self-describing via `packet_type`
- Flexible payload (arbitrary JSON)
- Optional lineage for DAG-style reasoning chains

---

## Field Reference

### Core Fields (Required)

| Field | Type | Description |
|-------|------|-------------|
| `packet_id` | `UUID` | Unique identifier (auto-generated) |
| `packet_type` | `string` | Semantic category: `event`, `memory_write`, `reasoning_trace`, `insight`, etc. |
| `timestamp` | `datetime` | UTC timestamp (auto-generated) |
| `payload` | `object` | Arbitrary JSON payload |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `metadata` | `object` | Schema version, reasoning mode, agent, domain |
| `provenance` | `object` | Parent packet, source system, tool |
| `confidence` | `object` | Score (0-1) and rationale |
| `reasoning_block` | `object` | Inline StructuredReasoningBlock |

### v1.1.0 Extensions (Backward Compatible)

| Field | Type | Description |
|-------|------|-------------|
| `thread_id` | `UUID` | Conversation/session thread identifier |
| `lineage` | `PacketLineage` | DAG-style parent tracking |
| `tags` | `list[string]` | Lightweight labels for filtering |
| `ttl` | `datetime` | Expiration timestamp for memory hygiene |

---

## JSON Schema

### PacketEnvelope

```json
{
  "packet_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "packet_type": "event",
  "timestamp": "2025-12-07T12:00:00Z",
  "payload": {
    "action": "user_query",
    "content": "Find HDPE suppliers"
  },
  "metadata": {
    "schema_version": "1.1.0",
    "reasoning_mode": "chain_of_thought",
    "agent": "plasticos_agent",
    "domain": "plastic_brokerage"
  },
  "provenance": {
    "parent_packet": "00000000-0000-0000-0000-000000000000",
    "source": "api_gateway",
    "tool": "search_tool"
  },
  "confidence": {
    "score": 0.95,
    "rationale": "High confidence based on source reliability"
  },
  "thread_id": "11111111-2222-3333-4444-555555555555",
  "lineage": {
    "parent_ids": ["uuid-1", "uuid-2"],
    "derivation_type": "inference",
    "generation": 2,
    "root_packet_id": "uuid-root"
  },
  "tags": ["hdpe", "supplier_search", "california"],
  "ttl": "2025-12-14T12:00:00Z"
}
```

### PacketLineage (v1.1.0)

```json
{
  "parent_ids": ["uuid-1", "uuid-2"],
  "derivation_type": "inference",
  "generation": 2,
  "root_packet_id": "uuid-root"
}
```

**Derivation Types:**
- `split` – One packet split into multiple
- `merge` – Multiple packets merged into one
- `transform` – Content transformation
- `inference` – Derived via reasoning

---

## Usage Examples

### Python (Pydantic Model)

```python
from memory.substrate_models import PacketEnvelope, PacketLineage
from uuid import uuid4

# Create a basic packet
envelope = PacketEnvelope(
    packet_type="event",
    payload={"action": "user_query", "content": "Find suppliers"},
)

# Create with lineage (v1.1.0)
envelope = PacketEnvelope(
    packet_type="insight",
    payload={"finding": "Market trend identified"},
    thread_id=uuid4(),
    lineage=PacketLineage(
        parent_ids=[parent_packet_id],
        derivation_type="inference",
    ),
    tags=["market_analysis", "auto_generated"],
    ttl=datetime.utcnow() + timedelta(days=7),
)
```

### API Submission

```bash
curl -X POST http://localhost:8080/api/v1/memory/packet \
  -H "Content-Type: application/json" \
  -d '{
    "packet_type": "event",
    "payload": {"action": "user_query", "content": "Find HDPE"},
    "thread_id": "11111111-2222-3333-4444-555555555555",
    "tags": ["hdpe", "search"]
  }'
```

---

## Database Mapping

### packet_store Table

| Column | Type | Notes |
|--------|------|-------|
| `packet_id` | `UUID` | Primary key |
| `packet_type` | `TEXT` | Indexed |
| `envelope` | `JSONB` | Full envelope JSON |
| `timestamp` | `TIMESTAMPTZ` | Indexed (DESC) |
| `routing` | `JSONB` | Agent routing info |
| `provenance` | `JSONB` | Provenance data |
| `thread_id` | `UUID` | v1.1.0 - Indexed |
| `parent_ids` | `UUID[]` | v1.1.0 - GIN indexed |
| `tags` | `TEXT[]` | v1.1.0 - GIN indexed |
| `ttl` | `TIMESTAMP` | v1.1.0 - Indexed where NOT NULL |

### Indexes

```sql
-- Primary indexes
CREATE INDEX idx_packet_store_packet_type ON packet_store(packet_type);
CREATE INDEX idx_packet_store_timestamp ON packet_store(timestamp DESC);

-- v1.1.0 indexes
CREATE INDEX idx_packet_thread ON packet_store(thread_id);
CREATE INDEX idx_packet_lineage ON packet_store USING GIN(parent_ids);
CREATE INDEX idx_packet_tags ON packet_store USING GIN(tags);
CREATE INDEX idx_packet_ttl ON packet_store(ttl) WHERE ttl IS NOT NULL;
```

---

## Contracts & Invariants

1. **Immutability** – PacketEnvelope cannot be modified after insertion
2. **Required Fields** – Only `packet_type`, `payload`, `timestamp` are required
3. **Payload Freedom** – `payload` is arbitrary JSON, not schema-enforced
4. **Thread Consistency** – All packets with same `thread_id` belong to one conversation
5. **Lineage Integrity** – `parent_ids` should reference existing packets

---

## Related Models

| Model | Location | Purpose |
|-------|----------|---------|
| `PacketEnvelopeIn` | `substrate_models.py` | Input DTO (auto-generates packet_id/timestamp) |
| `PacketWriteResult` | `substrate_models.py` | DAG processing result |
| `PacketStoreRow` | `substrate_models.py` | Database row DTO |
| `PacketLineage` | `substrate_models.py` | Lineage metadata (v1.1.0) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2025-12-07 | Added `thread_id`, `lineage`, `tags`, `ttl` |
| 1.0.1 | 2025-12-06 | Initial aligned schema |
| 1.0.0 | 2025-12-01 | Initial release |

---

## See Also

- [Memory Substrate README](../memory_substrate_readme_v1.0.0.md)
- [Schema Spec](../../core/schemas/Memory.yaml)
- [Pydantic Models](../../memory/substrate_models.py)

