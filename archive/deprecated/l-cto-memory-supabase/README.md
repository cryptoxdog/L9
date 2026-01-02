# l-cto/memory/ - Supabase-Based Memory (DEPRECATED)

**Status**: ✅ Archived  
**Date**: 2025-12-30  
**Reason**: Replaced by `MemorySubstrateService` (PostgreSQL + Neo4j + pgvector)

---

## What Was Here

This folder contained the **Supabase-based memory system** for l-cto agent:

### l1/ - L1 Memory Layer
- `l1_writer.py` - Writes to Supabase tables (l_directives, l_reasoning_patterns, etc.)
- `l1_reader.py` - Reads from Supabase tables
- `l1_router.py` - Routes L1 table operations
- `l1_query.py` - Advanced queries (filter, search, count)
- `l1_models.py` - Pydantic models (DirectiveModel, ReasoningPatternModel, etc.)
- `l1_validators.py` - Payload validation
- `diagnostics.py` - Table counts, error tracking
- `retention_processor.py` - Memory retention processing

### meta/ - META (System Governance) Layer
- `meta_router.py` - Routes META table operations (meta_audit_log, meta_incident_log)
- `meta_versioning.py` - Schema versioning/snapshots

### shared/ - Shared Utilities
- `supabase_client.py` - Supabase client
- `governance_filter.py` - Payload validation (forbidden keys, size limits)
- `connection_validator.py` - Validates Supabase connection and tables
- `constants.py` - Table name constants (L1_TABLES, MAC_TABLES, META_TABLES)
- `hashing.py` - Payload hashing
- `logging_hooks.py` - Logging utilities
- `kg_sync.py` - Knowledge graph sync
- Other utilities: sanitizer, normalizer, locks, rate_limiter, etc.

---

## Replacement

**Use instead:**
```python
from memory.substrate_service import MemorySubstrateService
from memory.substrate_models import PacketEnvelopeIn, PacketMetadata

await substrate_service.write_packet(
    PacketEnvelopeIn(
        packet_type="agent.l_cto.directive",
        payload=payload,
        metadata=PacketMetadata(agent="l-cto", schema_version="1.0.0")
    )
)
```

**Benefits:**
- ✅ Uses PacketEnvelope.yaml spec
- ✅ Async/await (non-blocking)
- ✅ Full DAG pipeline (validation → reasoning → embedding → storage)
- ✅ PostgreSQL + Neo4j + pgvector (not Supabase)
- ✅ Multi-agent support via `metadata.agent` field

---

## Migration Status

- ✅ All Supabase references removed from active code
- ✅ `MemoryRouterV4` deprecated and archived
- ✅ All memory operations use `MemorySubstrateService`
- ✅ This folder archived (no longer in active codebase)

