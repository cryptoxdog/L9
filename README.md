# L9 — Agentic Intelligence Platform

> **Version:** 1.1.0  
> **Status:** Deployment Ready

## Overview

L9 is a modular agentic AI platform combining:
- **Memory Substrate** — Postgres + pgvector for semantic & episodic memory
- **Reasoning Engine** — LangGraph-powered DAG orchestration with CoT/ToT/FoT strategies
- **World Model** — Insight-driven updates with scheduling and propagation
- **Orchestrators** — Modular agent coordination patterns

## Directory Structure

```
L9/
├── api/                  # FastAPI endpoints
│   ├── server.py         # Main API server
│   ├── os_routes.py      # OS health & status routes
│   ├── agent_routes.py   # Agent task management routes
│   └── memory/           # Memory API router
├── core/                 # Core schemas & interfaces
│   ├── schemas/          # Pydantic models, YAML specs
│   └── retrievers/       # Retrieval patterns
├── memory/               # Memory substrate implementation
│   ├── substrate_graph.py    # LangGraph DAG with insight extraction
│   ├── substrate_models.py   # PacketEnvelope, KnowledgeFact models
│   ├── substrate_repository.py # Database operations
│   ├── substrate_service.py  # Service orchestration
│   └── substrate_semantic.py # Embedding providers
├── orchestrators/        # Agent orchestration patterns
│   ├── reasoning/        # CoT/ToT/FoT reasoning engine
│   ├── world_model/      # World model lifecycle & scheduling
│   ├── memory/           # Memory housekeeping
│   ├── action_tool/      # Tool execution
│   ├── evolution/        # Self-improvement
│   ├── meta/             # Meta-reasoning
│   └── research_swarm/   # Multi-agent research
├── world_model/          # World model implementation
├── services/             # Business logic services
├── config/               # Configuration & settings
├── deploy/               # Docker, compose files
├── docs/                 # Documentation
├── migrations/           # SQL migrations (0001-0004)
└── tests/                # Test suites
```

## Quick Start

### Local Development

```bash
# 1. Set environment variables
export DATABASE_URL="postgresql://l9_user:YOUR_PASSWORD@localhost:5432/l9_memory"
export OPENAI_API_KEY="sk-..."  # Optional, uses stub provider if not set

# 2. Start PostgreSQL with pgvector
docker run -d --name l9-postgres \
  -e POSTGRES_USER=l9_user \
  -e POSTGRES_PASSWORD=YOUR_PASSWORD \
  -e POSTGRES_DB=l9_memory \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# 3. Apply migrations
psql $DATABASE_URL -f migrations/0001_init_memory_substrate.sql
psql $DATABASE_URL -f migrations/0002_enhance_packet_store.sql
psql $DATABASE_URL -f migrations/0004_init_knowledge_facts.sql

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start API server
uvicorn api.server:app --reload --port 8000
```

### Docker Compose (Recommended)

```bash
# Start all services
docker compose up -d

# With Redis (optional)
docker compose --profile redis up -d

# View logs
docker compose logs -f l9-api
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root status |
| `/health` | GET | Health check |
| `/os/health` | GET | OS layer health |
| `/os/status` | GET | System status |
| `/agent/health` | GET | Agent layer health |
| `/agent/task` | POST | Submit agent task |
| `/memory/test` | POST | Memory endpoint test |
| `/memory/embeddings` | POST/GET | Embedding operations |

## Key Modules

| Module | Purpose |
|--------|---------|
| `memory/` | PacketEnvelope, semantic search, insight extraction, knowledge facts |
| `orchestrators/reasoning/` | Chain/Tree/Forest-of-thought reasoning |
| `orchestrators/world_model/` | Insight-driven world model updates |
| `core/schemas/` | Pydantic models, validation |

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | Postgres connection string |
| `OPENAI_API_KEY` | No | - | For OpenAI embeddings |
| `EMBEDDING_MODEL` | No | text-embedding-3-large | Embedding model |
| `EMBEDDING_PROVIDER` | No | stub | `openai` or `stub` |
| `L9_API_KEY` | No | - | API authentication key |
| `LOG_LEVEL` | No | INFO | Logging level |

## Migrations

Apply in order:
1. `0001_init_memory_substrate.sql` - Core tables
2. `0002_enhance_packet_store.sql` - Thread/lineage/tags/TTL
3. `0004_init_knowledge_facts.sql` - Knowledge facts for insights

## Architecture

```
┌─────────────┐     ┌─────────────────────────────────────────────┐
│   Client    │────▶│              L9 API Server                  │
└─────────────┘     │  ┌─────────┐  ┌──────────┐  ┌───────────┐  │
                    │  │OS Routes│  │Agent     │  │Memory     │  │
                    │  └────┬────┘  │Routes    │  │Routes     │  │
                    │       │       └────┬─────┘  └─────┬─────┘  │
                    └───────┼────────────┼──────────────┼────────┘
                            │            │              │
                    ┌───────▼────────────▼──────────────▼────────┐
                    │            Memory Substrate DAG             │
                    │  intake → reasoning → memory_write →        │
                    │  semantic_embed → extract_insights →        │
                    │  store_insights → world_model_trigger →     │
                    │  checkpoint                                 │
                    └────────────────────┬───────────────────────┘
                                         │
                    ┌────────────────────▼───────────────────────┐
                    │         PostgreSQL + pgvector               │
                    │  packet_store | semantic_memory |           │
                    │  reasoning_traces | knowledge_facts         │
                    └─────────────────────────────────────────────┘
```

## VPS Deploy

```bash
# 1. Local pre-flight
venv/bin/python tests/smoke_test_root.py && venv/bin/python tests/smoke_email.py

# 2. Push to main
git push origin main

# 3. SSH to VPS
ssh your-vps-alias

# 4. Run release gate
cd /opt/l9 && sudo bash ops/vps_release_gate.sh

# 5. Verify
curl -sS http://127.0.0.1:8000/health | jq .

# 6. Reboot test (optional)
sudo reboot  # then reconnect and verify services auto-start
```

See [Go-Live.md](Go-Live.md) for full deployment documentation.

## Documentation

- [Memory Substrate Guide](docs/memory_substrate_readme_v1.0.0.md)
- [PacketEnvelope Reference](docs/memory/PacketEnvelope.md)
- [Memory Integration](DOCS-IB/MEMORY_SUBSTRATE_INTEGRATION.md)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2025-12-08 | Insight extraction, knowledge facts, world model integration |
| 1.0.0 | 2025-12-01 | Initial memory substrate release |

---

*L9 Platform — Internal Use*

