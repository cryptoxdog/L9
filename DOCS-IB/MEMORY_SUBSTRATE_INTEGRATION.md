# L9 Memory Substrate Integration

**Version:** 1.0.0  
**Date:** 2025-12-07  
**Status:** Integrated

---

## Summary

The L9 Memory Substrate has been integrated into L9_Unified as a black-box service. All services now run on a single Docker network with automatic database migrations.

## What Changed

| Component | Change |
|-----------|--------|
| `docker-compose.yml` | Merged memory substrate services (postgres, l9-memory-api, longrag) |
| `clients/memory_client.py` | New async HTTP client using httpx |
| `services/research/research_graph.py` | Added `store_insights` node after `finalize_node` |
| `services/research/insight_extractor.py` | New agent for extracting structured insights |
| `services/research/graph_state.py` | Added `stored_insights` field |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    l9-network (bridge)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│   │  l9-runtime  │───▶│ l9-memory-api│───▶│   postgres   │  │
│   │    :8000     │    │    :8080     │    │    :5432     │  │
│   └──────────────┘    └──────────────┘    │  (pgvector)  │  │
│          │                                 └──────────────┘  │
│          │            ┌──────────────┐           │           │
│          └───────────▶│   longrag    │───────────┘           │
│                       │    :8090     │                       │
│                       └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Usage

### Starting Services

```bash
# Start core services (runtime + memory)
docker compose up -d

# Include LongRAG service
docker compose --profile longrag up -d
```

### Using MemoryClient

```python
from clients.memory_client import get_memory_client

async def example():
    client = get_memory_client()
    
    # Write a packet
    result = await client.write_packet(
        packet_type="insight",
        payload={
            "content": "Key finding from analysis",
            "source": "research_graph",
        },
        metadata={"agent": "my_agent", "domain": "research"},
        confidence={"score": 0.85, "rationale": "High-quality source"},
    )
    print(f"Packet ID: {result.packet_id}")
    
    # Semantic search
    hits = await client.semantic_search(
        query="What are the key findings?",
        top_k=5,
    )
    for hit in hits.hits:
        print(f"Score: {hit.score}, Payload: {hit.payload}")
```

### Using Context Manager

```python
from clients.memory_client import MemoryClient

async def example():
    async with MemoryClient() as client:
        result = await client.write_packet(
            packet_type="event",
            payload={"action": "user_login"},
        )
```

---

## Research Graph Flow

```
START → planning → research → merge → critic
                                         │
                    ┌────────────────────┘
                    ▼
           (score < threshold?)
                    │
         ┌─────────┴─────────┐
         ▼                   ▼
    planning            finalize
    (retry)                  │
                             ▼
                      store_insights ← NEW
                             │
                             ▼
                            END
```

The `store_insights` node:
1. Calls `InsightExtractorAgent` to extract structured insights
2. Writes each insight as a `PacketEnvelope v1.0.1` via `MemoryClient`
3. Stores results in `state.stored_insights`

---

## Packet Schema (Memory.yaml v1.0.1)

```yaml
PacketEnvelopeIn:
  packet_type: string  # "insight", "event", etc.
  payload: object      # Flexible JSON
  metadata: object?    # {schema_version, agent, domain}
  provenance: object?  # {parent_packet, source_agent}
  confidence: object?  # {score, rationale}
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/memory/packet` | POST | Write a PacketEnvelope |
| `/api/v1/memory/semantic/search` | POST | Search semantic memory |
| `/health` | GET | Health check |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_API_BASE_URL` | `http://l9-memory-api:8080` | Memory API URL |
| `POSTGRES_USER` | `l9_user` | Database user |
| `POSTGRES_PASSWORD` | `l9_secure_password` | Database password |
| `POSTGRES_DB` | `l9_memory` | Database name |
| `OPENAI_API_KEY` | - | For embeddings |
| `EMBEDDING_MODEL` | `text-embedding-3-large` | Embedding model |

---

## Files Created/Modified

```
L9/
├── docker-compose.yml              # MODIFIED - merged memory services
├── clients/
│   ├── __init__.py                 # NEW
│   └── memory_client.py            # NEW - httpx async client
├── services/research/
│   ├── research_graph.py           # MODIFIED - added store_insights
│   ├── insight_extractor.py        # NEW
│   └── graph_state.py              # MODIFIED - added stored_insights
└── DOCS-IB/
    └── MEMORY_SUBSTRATE_INTEGRATION.md  # NEW - this file
```

