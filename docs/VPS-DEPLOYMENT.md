# L9 VPS Deployment Configuration

## Overview

L9 runs on a VPS at `157.180.73.53` with Docker Compose orchestrating all services.

**Directory:** `/opt/l9`

---

## Docker Services

| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| `l9-api` | `l9-l9-api:latest` | 127.0.0.1:8000 | FastAPI application |
| `l9-postgres` | `pgvector/pgvector:pg16` | 127.0.0.1:5432 | PostgreSQL + pgvector |
| `l9-neo4j` | `neo4j:5-community` | 127.0.0.1:7474, 7687 | Graph database |
| `l9-redis` | `redis:7-alpine` | 127.0.0.1:6379 | Cache, queues, rate limiting |

**Network:** All containers on `l9-network` (Docker bridge network)

**Security:** All ports bound to `127.0.0.1` (localhost only). External access via Caddy reverse proxy.

---

## Database Configuration

### PostgreSQL (l9-postgres)

| Setting | Value |
|---------|-------|
| Version | PostgreSQL 16.11 |
| Extension | pgvector 0.8.1 |
| Database | `l9_memory` |
| User | `postgres` |
| Password | (in `.env` file) |
| Host (from containers) | `l9-postgres:5432` |
| Host (from VPS host) | `127.0.0.1:5432` |

**Connection String (inside Docker):**
```
postgresql://postgres:PASSWORD@l9-postgres:5432/l9_memory
```

### Database Tables (17 total)

| Table | Purpose |
|-------|---------|
| `packet_store` | Memory packets (core storage) |
| `semantic_memory` | Vector embeddings for search |
| `world_model_entities` | World model state |
| `world_model_updates` | World model change log |
| `world_model_snapshots` | World model checkpoints |
| `knowledge_facts` | Extracted knowledge |
| `reasoning_traces` | Reasoning audit log |
| `tasks` | Task queue |
| `agent_log` | Agent execution logs |
| `agent_memory_events` | Agent memory operations |
| `graph_checkpoints` | LangGraph state checkpoints |
| `schema_migrations` | Migration tracking |
| + 5 more | Business domain tables |

### Neo4j (l9-neo4j)

| Setting | Value |
|---------|-------|
| Version | Neo4j 5 Community |
| Bolt URI | `bolt://l9-neo4j:7687` |
| HTTP UI | `http://127.0.0.1:7474` |
| User | `neo4j` |
| Password | (in `.env` file) |

### Redis (l9-redis)

| Setting | Value |
|---------|-------|
| Version | Redis 7 Alpine |
| Host (from containers) | `redis:6379` |
| Persistence | AOF enabled |
| Usage | Task queues, rate limiting, caching |

---

## Environment Variables

Configuration stored in `/opt/l9/.env`:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<password>
POSTGRES_DB=l9_memory

# Neo4j
NEO4J_URI=bolt://l9-neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<password>

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# OpenAI
OPENAI_API_KEY=<key>
OPENAI_MODEL=gpt-4-turbo

# L9 API
L9_API_KEY=<key>
L9_USE_KERNELS=true
```

---

## Docker Compose Key Settings

```yaml
services:
  l9-api:
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@l9-postgres:5432/${POSTGRES_DB}
      MEMORY_DSN: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@l9-postgres:5432/${POSTGRES_DB}
      NEO4J_URI: ${NEO4J_URI:-bolt://l9-neo4j:7687}
      REDIS_HOST: ${REDIS_HOST:-redis}
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      redis:
        condition: service_healthy
      neo4j:
        condition: service_healthy
```

**Important:** Database hostnames use container names (`l9-postgres`, `l9-neo4j`, `redis`), NOT `127.0.0.1`.

---

## Common Commands

### Deployment

```bash
cd /opt/l9
git pull origin main
docker compose build --no-cache l9-api
docker compose up -d
```

### Health Check

```bash
curl http://localhost:8000/health
```

### Logs

```bash
docker logs l9-api --tail=50
docker compose logs -f
```

### Database Access

```bash
# PostgreSQL
docker exec -it l9-postgres psql -U postgres -d l9_memory

# List tables
docker exec -it l9-postgres psql -U postgres -d l9_memory -c "\dt"
```

### Container Status

```bash
docker compose ps
docker network ls
```

### Restart Services

```bash
docker compose restart l9-api
docker compose up -d --force-recreate l9-api
```

---

## Migrations

Location: `/opt/l9/migrations/`

| File | Purpose |
|------|---------|
| `0001_init_memory_substrate.sql` | Core packet_store, semantic_memory |
| `0002_enhance_packet_store.sql` | Additional indexes |
| `0003_init_tasks.sql` | Task queue table |
| `0004_init_world_model_entities.sql` | World model |
| `0005_init_knowledge_facts.sql` | Knowledge base |
| `0006_init_world_model_updates.sql` | World model updates |
| `0007_init_world_model_snapshots.sql` | World model snapshots |

Migrations run automatically via `api.db.init_db()` on startup.

---

## Troubleshooting

### "Failed to resolve host" errors
- Ensure containers are on same network: `docker network connect l9-network <container>`
- Use container names, not `127.0.0.1`, in connection strings

### "Connection refused" errors
- Check container is running: `docker ps`
- Check correct port in connection string
- Verify `.env` overrides match container names

### Orphan container warnings
- Cosmetic only - container started outside docker-compose
- Can ignore or run: `docker compose up -d --remove-orphans`

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    VPS (157.180.73.53)                       │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Docker Network (l9-network)             │   │
│   │                                                      │   │
│   │  ┌──────────┐  ┌─────────────┐  ┌─────────────────┐ │   │
│   │  │  l9-api  │──│ l9-postgres │  │    l9-neo4j     │ │   │
│   │  │  :8000   │  │   :5432     │  │  :7474, :7687   │ │   │
│   │  └──────────┘  └─────────────┘  └─────────────────┘ │   │
│   │       │                                              │   │
│   │  ┌──────────┐                                       │   │
│   │  │  redis   │                                       │   │
│   │  │  :6379   │                                       │   │
│   │  └──────────┘                                       │   │
│   └─────────────────────────────────────────────────────┘   │
│                              │                               │
│                    ┌─────────────────┐                      │
│                    │     Caddy       │ (reverse proxy)      │
│                    │    :443/:80     │                      │
│                    └─────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Version History

| Date | Changes |
|------|---------|
| 2025-12-26 | Initial deployment documentation |
| 2025-12-26 | Fixed PostgreSQL/Neo4j connection strings (127.0.0.1 → container names) |



