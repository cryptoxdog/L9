# L9 Memory Substrate v1.0.0

Hybrid memory + structured reasoning substrate for L9 and PlasticOS using Postgres + pgvector + LangGraph.

## Overview

The Memory Substrate provides:

- **PacketEnvelope API** - Canonical interface for all agent events and memory writes
- **Semantic Memory** - pgvector-powered similarity search with 1536-dimension embeddings
- **LangGraph DAG** - Processing pipeline for intake → reasoning → memory → embedding → checkpoint
- **11 Postgres Tables** - Structured storage for events, traces, checkpoints, and domain entities

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI REST API                         │
│               POST /packet    POST /semantic/search             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MemorySubstrateService                       │
│         Orchestrates repository, semantic, and DAG              │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  Repository   │      │    Semantic   │      │  LangGraph    │
│   (asyncpg)   │      │   (pgvector)  │      │     DAG       │
└───────────────┘      └───────────────┘      └───────────────┘
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │  PostgreSQL + pgvector  │
                    │     (11 tables)     │
                    └─────────────────────┘
```

## Quick Start

### 1. Deploy with Docker Compose

```bash
# Navigate to deploy directory
cd L9/deploy

# Copy environment example and configure
cp .env.example .env
# Edit .env with your settings

# Start services
docker compose -f docker-compose.memory_substrate_v1.0.0.yaml up -d
```

### 2. Run Migrations

Migrations run automatically on Postgres startup via the initdb script, but you can run them manually:

```bash
# Connect to postgres container
docker exec -it l9-memory-postgres psql -U l9_user -d l9_memory

# Or run migration file directly
psql -U l9_user -d l9_memory -f migrations/0001_init_memory_substrate.sql
```

### 3. Test the API

#### Health Check

```bash
curl http://localhost:8080/health
```

#### Submit a Packet

```bash
curl -X POST http://localhost:8080/api/v1/memory/packet \
  -H "Content-Type: application/json" \
  -d '{
    "packet_type": "event",
    "payload": {
      "action": "user_query",
      "content": "Find HDPE suppliers in California"
    },
    "metadata": {
      "agent": "plasticos_agent",
      "domain": "plastic_brokerage"
    }
  }'
```

Response:

```json
{
  "packet_id": "a1b2c3d4-...",
  "written_tables": ["packet_store", "agent_memory_events", "reasoning_traces"],
  "status": "ok"
}
```

#### Semantic Search

```bash
curl -X POST http://localhost:8080/api/v1/memory/semantic/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "HDPE suppliers",
    "top_k": 5
  }'
```

Response:

```json
{
  "query": "HDPE suppliers",
  "hits": [
    {
      "embedding_id": "...",
      "score": 0.92,
      "payload": { "content": "..." }
    }
  ]
}
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | Postgres connection string |
| `EMBEDDING_MODEL` | No | `text-embedding-3-large` | OpenAI embedding model |
| `OPENAI_API_KEY` | No | - | Required for real embeddings |
| `API_HOST` | No | `0.0.0.0` | API bind host |
| `API_PORT` | No | `8080` | API port |
| `DB_POOL_SIZE` | No | `5` | Connection pool size |

### Without OpenAI (Stub Embeddings)

The system works without an OpenAI API key using deterministic stub embeddings. This is useful for development and testing, but semantic search will not produce meaningful results.

```bash
# No OPENAI_API_KEY - uses stub provider
export DATABASE_URL="postgresql://user:pass@localhost:5432/l9_memory"
```

### With OpenAI (Real Embeddings)

```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/l9_memory"
export OPENAI_API_KEY="sk-..."
export EMBEDDING_MODEL="text-embedding-3-large"
```

## Database Schema

### Core Tables

| Table | Purpose |
|-------|---------|
| `packet_store` | All PacketEnvelopes |
| `agent_memory_events` | Agent memory events with packet refs |
| `semantic_memory` | Vector embeddings (pgvector) |
| `reasoning_traces` | Structured reasoning blocks |
| `graph_checkpoints` | LangGraph state checkpoints |
| `agent_log` | Centralized logging |

### Domain Tables

| Table | Purpose |
|-------|---------|
| `buyer_profiles` | Buyer entities |
| `supplier_profiles` | Supplier entities |
| `transactions` | Material transactions |
| `material_edges` | Knowledge graph edges |
| `entity_metadata` | Generic metadata |

## LangGraph DAG

The processing pipeline:

```
intake_node ──► reasoning_node ──┬──► memory_write_node ──► checkpoint_node
                                 │
                                 └──► semantic_embed_node ──►
```

### Node Functions

1. **intake_node** - Validates envelope, ensures required fields
2. **reasoning_node** - Generates StructuredReasoningBlock with features and inference steps
3. **memory_write_node** - Writes to packet_store, agent_memory_events, reasoning_traces
4. **semantic_embed_node** - Generates embedding and stores in semantic_memory
5. **checkpoint_node** - Saves graph state to graph_checkpoints

## API Reference

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/memory/packet` | Submit a PacketEnvelope |
| `POST` | `/api/v1/memory/semantic/search` | Search semantic memory |
| `GET` | `/api/v1/memory/packet/{id}` | Retrieve packet by ID |
| `GET` | `/api/v1/memory/events/{agent_id}` | Get agent memory events |
| `GET` | `/api/v1/memory/traces` | Get reasoning traces |
| `GET` | `/api/v1/memory/checkpoint/{agent_id}` | Get agent checkpoint |
| `GET` | `/api/v1/memory/health` | Health check |

### PacketEnvelope Schema

```json
{
  "packet_id": "uuid (auto-generated)",
  "packet_type": "event | memory_write | reasoning_trace | ...",
  "timestamp": "ISO datetime (auto-generated)",
  "payload": { "any": "json object" },
  "metadata": {
    "schema_version": "1.0.0",
    "reasoning_mode": "chain_of_thought",
    "agent": "agent_name",
    "domain": "plastic_brokerage"
  },
  "provenance": {
    "parent_packet": "uuid",
    "source": "source_system",
    "tool": "tool_name"
  },
  "confidence": {
    "score": 0.95,
    "rationale": "explanation"
  }
}
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/test_memory_substrate_basic.py -v
```

### Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt
pip install asyncpg pgvector langgraph langchain pydantic-settings

# Set environment
export DATABASE_URL="postgresql://user:pass@localhost:5432/l9_memory"

# Run migrations
psql -U user -d l9_memory -f migrations/0001_init_memory_substrate.sql

# Start API
python -m uvicorn l.api.memory_api:create_app --factory --reload
```

## Troubleshooting

### Connection Refused

```bash
# Check postgres is running
docker logs l9-memory-postgres

# Verify connectivity
psql $DATABASE_URL -c "SELECT 1"
```

### pgvector Extension Missing

```sql
-- Inside postgres
CREATE EXTENSION IF NOT EXISTS vector;
```

### Import Errors

Ensure `PYTHONPATH` includes the L9 directory:

```bash
export PYTHONPATH=/path/to/L9:$PYTHONPATH
```

## Version History

- **1.0.0** - Initial release with core substrate functionality

## License

Internal L9 Platform use.

