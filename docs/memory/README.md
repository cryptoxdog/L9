# L9 Memory Substrate — Architecture Documentation

> **Version:** 1.1.0  
> **Status:** Production Ready

## Overview

The L9 Memory Substrate is a hybrid memory system combining:
- **Structured Storage** — PostgreSQL for packets, events, reasoning traces
- **Vector Storage** — pgvector for semantic embeddings
- **Knowledge Graph** — Extracted facts and insights
- **LangGraph DAG** — Processing pipeline with insight extraction

## Architecture

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                   Memory Substrate DAG                   │
                    │                                                         │
   PacketEnvelope   │  ┌────────┐   ┌───────────┐   ┌──────────────┐         │
        │           │  │ intake │──▶│ reasoning │──▶│ memory_write │         │
        ▼           │  └────────┘   └─────┬─────┘   └──────┬───────┘         │
   ┌─────────┐      │                     │                │                 │
   │ Ingestion│─────│─────────────────────┼────────────────┼─────────────────│
   │ Pipeline │      │                     │                │                 │
   └─────────┘      │                     ▼                ▼                 │
                    │              ┌─────────────┐  ┌───────────────┐        │
                    │              │semantic_embed│  │extract_insights│        │
                    │              └──────┬──────┘  └───────┬───────┘        │
                    │                     │                 │                 │
                    │                     ▼                 ▼                 │
                    │              ┌─────────────────────────────┐           │
                    │              │      store_insights         │           │
                    │              └──────────────┬──────────────┘           │
                    │                             │                          │
                    │                             ▼                          │
                    │              ┌─────────────────────────────┐           │
                    │              │   world_model_trigger       │           │
                    │              └──────────────┬──────────────┘           │
                    │                             │                          │
                    │                             ▼                          │
                    │              ┌─────────────────────────────┐           │
                    │              │       checkpoint            │           │
                    │              └─────────────────────────────┘           │
                    └─────────────────────────────────────────────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         ▼                         │
                    │    ┌─────────────────────────────────────────┐    │
                    │    │          PostgreSQL + pgvector          │    │
                    │    │                                         │    │
                    │    │  ┌──────────────┐  ┌─────────────────┐  │    │
                    │    │  │ packet_store │  │ semantic_memory │  │    │
                    │    │  └──────────────┘  └─────────────────┘  │    │
                    │    │                                         │    │
                    │    │  ┌───────────────────┐  ┌────────────┐  │    │
                    │    │  │ agent_memory_events│  │ knowledge_ │  │    │
                    │    │  └───────────────────┘  │ facts      │  │    │
                    │    │                         └────────────┘  │    │
                    │    │  ┌──────────────────┐  ┌─────────────┐  │    │
                    │    │  │ reasoning_traces │  │ checkpoints │  │    │
                    │    │  └──────────────────┘  └─────────────┘  │    │
                    │    └─────────────────────────────────────────┘    │
                    └───────────────────────────────────────────────────┘
```

## Packet Lifecycle

### 1. Ingestion

```python
from memory.ingestion import get_ingestion_pipeline

pipeline = get_ingestion_pipeline()
result = await pipeline.ingest(PacketEnvelopeIn(
    packet_type="event",
    payload={"action": "user_login", "user_id": "123"},
    tags=["auth", "login"],
    ttl=datetime.utcnow() + timedelta(days=30),
))
```

**Ingestion Steps:**
1. Validate packet structure
2. Auto-generate tags from content
3. Store to `packet_store`
4. Store to `agent_memory_events`
5. Generate embedding (if text content)
6. Update lineage graph
7. Store artifacts

### 2. Processing (DAG)

The LangGraph DAG processes packets through these nodes:

| Node | Function |
|------|----------|
| `intake_node` | Validate, normalize, set defaults |
| `reasoning_node` | Generate StructuredReasoningBlock |
| `memory_write_node` | Persist packet and reasoning |
| `semantic_embed_node` | Generate and store embedding |
| `extract_insights_node` | Extract facts and insights |
| `store_insights_node` | Persist to knowledge_facts |
| `world_model_trigger_node` | Trigger world model updates |
| `gc_trigger_node` | Probabilistic TTL eviction |
| `checkpoint_node` | Save graph state |

### 3. Retrieval

```python
from memory.retrieval import get_retrieval_pipeline

pipeline = get_retrieval_pipeline()

# Semantic search
results = await pipeline.semantic_search("user authentication", top_k=10)

# Hybrid search (semantic + filters)
results = await pipeline.hybrid_search(
    query="login events",
    filters={"packet_type": "event", "tags": ["auth"]},
    min_score=0.7,
)

# Thread reconstruction
thread = await pipeline.fetch_thread(thread_id)

# Lineage traversal
lineage = await pipeline.fetch_lineage(packet_id, direction="ancestors")
```

## Insight Pipeline

### Extraction

The `InsightExtractionPipeline` uses heuristic rules (no ML):

```python
from memory.insight_extraction import get_insight_pipeline

pipeline = get_insight_pipeline()
result = await pipeline.extract_from_packet(envelope)

# Returns:
# {
#   "packet_id": "...",
#   "insights": [...],  # ExtractedInsight objects
#   "facts": [...]      # KnowledgeFact objects
# }
```

### Insight Types

| Type | Description |
|------|-------------|
| `conclusion` | Derived from reasoning decision tokens |
| `pattern` | Text content detection |
| `anomaly` | Unusual patterns or values |
| `recommendation` | Suggested actions |

### Knowledge Facts

Facts are stored as subject-predicate-object triples:

```sql
-- knowledge_facts table
fact_id UUID PRIMARY KEY
subject TEXT NOT NULL        -- "user_123"
predicate TEXT NOT NULL      -- "logged_in_at"
object JSONB NOT NULL        -- "2025-12-08T10:30:00Z"
confidence FLOAT             -- 0.85
source_packet UUID           -- FK to packet_store
```

## Housekeeping

### Garbage Collection

```python
from memory.housekeeping import get_housekeeping_engine

engine = get_housekeeping_engine()
result = await engine.run_full_gc()

# Returns:
# {
#   "status": "ok",
#   "cleaned": {
#     "ttl_evicted": 15,
#     "orphans_cleaned": 3,
#     "tags_gc": 8
#   }
# }
```

### GC Operations

| Operation | Description |
|-----------|-------------|
| `evict_expired_ttl` | Remove packets with expired TTL |
| `cleanup_orphan_packets` | Fix invalid parent references |
| `cleanup_parentless_packets` | Remove abandoned packets |
| `cleanup_orphan_artifacts` | Remove orphan embeddings/events |
| `gc_unused_tags` | Remove low-usage tags |

## API Reference

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/packet` | Submit packet |
| GET | `/packet/{id}` | Get packet by ID |
| POST | `/semantic/search` | Semantic search |
| POST | `/hybrid/search` | Hybrid search |
| GET | `/thread/{id}` | Get thread packets |
| GET | `/lineage/{id}` | Get packet lineage |
| GET | `/facts` | Query knowledge facts |
| GET | `/insights` | Query insights |
| POST | `/gc/run` | Run garbage collection |
| GET | `/gc/stats` | Get GC statistics |
| GET | `/health` | Health check |

### Client SDK

```python
from clients.memory_client import MemoryClient

async with MemoryClient() as client:
    # Write packet
    result = await client.write_packet(
        packet_type="insight",
        payload={"summary": "User behavior analysis"},
    )
    
    # Semantic search
    results = await client.semantic_search("user behavior", top_k=10)
    
    # Hybrid search
    results = await client.hybrid_search(
        query="login events",
        filters={"packet_type": "event"},
    )
    
    # Fetch lineage
    lineage = await client.fetch_lineage(packet_id, direction="ancestors")
    
    # Fetch facts
    facts = await client.fetch_facts(subject="user_123")
    
    # Run GC
    gc_result = await client.run_gc()
```

## Database Schema

### Core Tables

```sql
-- packet_store (central packet storage)
packet_id UUID PRIMARY KEY
packet_type TEXT NOT NULL
envelope JSONB NOT NULL
timestamp TIMESTAMPTZ
thread_id UUID
parent_ids UUID[]
tags TEXT[]
ttl TIMESTAMP

-- semantic_memory (vector embeddings)
embedding_id UUID PRIMARY KEY
agent_id TEXT
vector VECTOR(1536)
payload JSONB
created_at TIMESTAMPTZ

-- knowledge_facts (extracted facts)
fact_id UUID PRIMARY KEY
subject TEXT NOT NULL
predicate TEXT NOT NULL
object JSONB NOT NULL
confidence FLOAT
source_packet UUID REFERENCES packet_store
created_at TIMESTAMP
```

### Migrations

Apply in order:
1. `0001_init_memory_substrate.sql` — Core tables
2. `0002_enhance_packet_store.sql` — Thread/lineage/tags/TTL
3. `0004_init_knowledge_facts.sql` — Knowledge facts table

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection string |
| `OPENAI_API_KEY` | - | For OpenAI embeddings |
| `EMBEDDING_MODEL` | text-embedding-3-large | Embedding model |
| `EMBEDDING_PROVIDER` | stub | `openai` or `stub` |
| `DB_POOL_SIZE` | 5 | Connection pool size |
| `DB_MAX_OVERFLOW` | 10 | Pool overflow limit |

## Examples

### Full Packet Lifecycle

```python
from memory.substrate_models import PacketEnvelopeIn, PacketLineage
from memory.substrate_service import create_substrate_service

# Initialize service
service = await create_substrate_service(
    database_url="postgresql://...",
    embedding_provider_type="openai",
)

# Create packet with lineage
packet = PacketEnvelopeIn(
    packet_type="analysis",
    payload={
        "subject": "user_behavior",
        "content": "Analysis of user login patterns shows...",
        "metrics": {"login_count": 150, "avg_duration": 45.2},
    },
    lineage=PacketLineage(
        parent_ids=[parent_packet_id],
        derivation_type="inference",
    ),
    tags=["analytics", "user_behavior"],
    ttl=datetime.utcnow() + timedelta(days=90),
)

# Process through DAG
result = await service.write_packet(packet)
print(f"Written to: {result.written_tables}")
```

### Insight Extraction

```python
from memory.insight_extraction import get_insight_pipeline

pipeline = get_insight_pipeline()

# Extract insights from existing packet
insights = await pipeline.extract_from_packet(envelope)

# Detect anomalies
anomalies = await pipeline.detect_anomalies(
    packet,
    historical_window=100,
)
```

---

*L9 Memory Substrate Documentation — v1.1.0*
