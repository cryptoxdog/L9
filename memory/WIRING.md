# L9 Memory Production Wiring

## Overview

This document describes the production wiring of the L9 Memory system. All components are wired, tested, and ready for production use.

## Memory Ingestion

### Canonical Entrypoint

**Single point of entry**: `memory.ingestion.ingest_packet()`

All packets MUST pass through this function. It:
1. Validates the packet
2. Routes to `MemorySubstrateService.write_packet()`
3. Runs the full DAG pipeline (intake → reasoning → memory → embedding → checkpoint)

### Where Memory is Hooked

1. **FastAPI Routes** (`api/memory/router.py`)
   - `/memory/packet` endpoint → `ingest_packet()`

2. **WebSocket Events** (`api/server.py`)
   - All WebSocket messages → `ingest_packet()` (non-blocking)

3. **Manual Integration**
   ```python
   from memory.ingestion import ingest_packet
   from memory.substrate_models import PacketEnvelopeIn
   
   packet = PacketEnvelopeIn(
       packet_type="my_event",
       payload={"data": "..."},
   )
   result = await ingest_packet(packet)
   ```

## Migrations

### Auto-Execution

Migrations run automatically on FastAPI startup via `lifespan()` context manager in `api/server.py`.

**Location**: `memory/migration_runner.py`

**Process**:
1. On startup, `run_migrations()` is called
2. Checks `schema_migrations` table for applied migrations
3. Executes pending migrations in order
4. Logs results (applied/skipped/errors)

**Idempotent**: Migrations can be run multiple times safely.

### Manual Execution

```bash
python -c "import asyncio; from memory.migration_runner import run_migrations; asyncio.run(run_migrations())"
```

## LangGraph Decision

**Status**: OPTIONAL / NOT REQUIRED

- `PacketNodeAdapter` exists but is not wired into main execution flow
- Memory system works independently via `ingest_packet()` → `MemorySubstrateService` → `SubstrateDAG`
- `SubstrateDAG` uses LangGraph internally for processing pipeline
- See `langgraph/STATUS.md` for details

## Verification

### Smoke Test

Run after server startup to verify:
- Migrations applied
- Memory service initialized
- Packet ingestion works
- Data appears in store

```bash
python -m memory.smoke_test
```

### Health Check

```bash
curl http://localhost:8000/memory/stats
```

## Startup Sequence

1. FastAPI app starts
2. `lifespan()` context manager runs:
   - Runs migrations (`run_migrations()`)
   - Initializes memory service (`init_service()`)
3. Server ready
4. On shutdown:
   - Closes memory service (`close_service()`)

## Configuration

Required environment variables:
- `MEMORY_DSN` or `DATABASE_URL` - Postgres connection string
- `OPENAI_API_KEY` (optional) - For OpenAI embeddings
- `EMBEDDING_PROVIDER` (optional) - "openai" or "stub" (default: "stub")
- `EMBEDDING_MODEL` (optional) - Model name (default: "text-embedding-3-large")

## Error Handling

- **Memory not initialized**: Returns 503 with clear error message
- **Migration failures**: Logged but don't block startup (check logs)
- **Ingestion failures**: Logged, packet status marked as "error" or "partial"

## No Dead Code

All memory code paths are:
- ✅ Wired into execution flow
- ✅ Tested via smoke test
- ✅ Documented in this file

No placeholders, no "future TODOs", no silent failures.

