# L9 Memory Substrate

Hybrid memory + structured reasoning substrate for L9 using PostgreSQL + pgvector + LangGraph.

## Components

| File | Purpose |
|------|---------|
| `substrate_models.py` | Pydantic models (PacketEnvelope, DTOs, state) |
| `substrate_repository.py` | Async database accessors (asyncpg) |
| `substrate_graph.py` | LangGraph DAG for packet processing |
| `substrate_service.py` | Service facade for API layer |
| `substrate_semantic.py` | Semantic embedding operations |

## Schema Version

**v1.1.0** — Includes `thread_id`, `parent_ids`, `tags`, `ttl` for enhanced threading and lineage.

## Migrations

Apply in order:

```bash
psql $DATABASE_URL -f migrations/0001_init_memory_substrate.sql
psql $DATABASE_URL -f migrations/0002_enhance_packet_store.sql
psql $DATABASE_URL -f migrations/0003_init_tasks.sql
```

## Usage

```python
from memory.substrate_models import PacketEnvelope
from memory.substrate_service import MemorySubstrateService

# Submit a packet
envelope = PacketEnvelope(
    packet_type="event",
    payload={"action": "user_query", "content": "..."}
)
result = await service.write_packet(envelope)
```

## Related Docs

- [PacketEnvelope Reference](../docs/memory/PacketEnvelope.md)
- [Schema Spec](../core/schemas/Memory.yaml)

