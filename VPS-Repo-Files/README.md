# VPS Deployment Files

Reference files and documentation for L9 VPS deployment at `157.180.73.53`.

---

## Docker Compose Configuration

| File | Purpose | Tracked |
|------|---------|---------|
| `/docker-compose.yml` (repo root) | **VPS Production** — 7 services with full observability | ✅ Yes |
| `/docker-compose.local.dev.yml` | **Mac Local Testing** — includes `host.docker.internal` | ❌ Gitignored |
| `/docker-compose.override.yml` | Mac-specific overrides (optional) | ❌ Gitignored |

### Key Difference

| Setting | VPS (`docker-compose.yml`) | Mac (`docker-compose.local.dev.yml`) |
|---------|---------------------------|--------------------------------------|
| PostgreSQL host | `l9-postgres` (container) | `l9-postgres` (container) |
| `extra_hosts` | None | `host.docker.internal:host-gateway` |
| Grafana volumes | `./grafana/provisioning/dashboards` | `./grafana/dashboards` |

---

## Services (VPS Production)

| Service | Port | Purpose |
|---------|------|---------|
| `redis` | 6379 | Task queues, caching |
| `neo4j` | 7474/7687 | Knowledge graph |
| `l9-postgres` | 5432 | Memory substrate (pgvector) |
| `l9-api` | 8000 | FastAPI application |
| `prometheus` | 9090 | Metrics collection |
| `grafana` | 3000 | Metrics dashboards |
| `jaeger` | 16686 | Distributed tracing |

---

## VPS Deployment Commands

```bash
# SSH into VPS
ssh root@157.180.73.53

# Navigate to L9
cd /opt/l9

# Pull latest from main
git pull origin main

# Restart services
docker compose down
docker compose up -d

# Check status
docker compose ps
docker compose logs -f l9-api
```

---

## VPS Testing Commands

Run tests inside the `l9-api` container:

```bash
# SSH into VPS
ssh root@157.180.73.53
cd /opt/l9

# Docker Stack Smoke Tests (validates full wiring)
docker compose exec l9-api pytest tests/docker/test_stack_smoke.py -v

# Memory System Smoke Test
docker compose exec l9-api python memory/smoke_test.py

# Tool Graph Tests (mocked Neo4j)
docker compose exec l9-api pytest tests/core/tools/test_tool_graph.py -v

# Slack Adapter Tests
docker compose exec l9-api pytest tests/test_slack_adapter.py -v

# API Health Tests
docker compose exec l9-api pytest tests/api/test_server_health.py -v

# All Integration Tests
docker compose exec l9-api pytest tests/integration/ -v

# Full Test Suite
docker compose exec l9-api pytest tests/ -v --ignore=tests/__pycache__
```

### Test Categories

| Category | Path | What it Tests |
|----------|------|---------------|
| Docker Stack | `tests/docker/` | Container health, port binding |
| Memory | `tests/memory/` + `memory/smoke_test.py` | Packet store, pgvector, ingestion |
| Tools | `tests/core/tools/` | Tool registry, permissions |
| Agents | `tests/core/agents/` | Executor, bootstrap |
| Slack | `tests/test_slack_adapter.py` | Slack webhook dispatch |
| API | `tests/api/` | FastAPI endpoints, health |
| Integration | `tests/integration/` | End-to-end flows |

### Quick Health Check (from Mac)

```bash
curl https://l9.quantumaipartners.com/health
curl https://l9.quantumaipartners.com/api/health
```

---

## Directory Contents

| Item | Description |
|------|-------------|
| `runtime/` | Dockerfile templates |
| `docker/` | Docker-related configs |
| `VPS-Deploy-Sequence/` | Deployment scripts and historical versions |
| `VPS-DIAGNOSTIC-OUTPUT.md` | Troubleshooting reference |

---

## Environment Variables

Ensure `/opt/l9/.env` on VPS contains:

```bash
POSTGRES_USER=l9_user
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=l9_memory
NEO4J_PASSWORD=<secure_password>
OPENAI_API_KEY=<key>
L9_API_KEY=<key>
# ... other secrets
```

---

## Quick Reference

**Local Mac Testing:**
```bash
# Use the local dev compose
docker compose -f docker-compose.local.dev.yml up -d
```

**VPS Production:**
```bash
# Uses root docker-compose.yml automatically
docker compose up -d
```

---

*Last updated: 2026-01-07*

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | VPS-OPER-003 |
| **Component Name** | Readme |
| **Module Version** | 1.0.0 |
| **Created At** | 2026-01-08T03:17:26Z |
| **Created By** | L9_DORA_Injector |
| **Layer** | operations |
| **Domain** | VPS-Repo-Files |
| **Type** | schema |
| **Status** | active |
| **Governance Level** | medium |
| **Compliance Required** | True |
| **Audit Trail** | True |
| **Purpose** | Documentation for README |

---
