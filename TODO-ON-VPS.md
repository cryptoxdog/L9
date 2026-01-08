# TODO on VPS

> **VPS:** 157.180.73.53 (root)  
> **Path:** /opt/l9  
> **Updated:** 2026-01-06

---

## Quick Reference

```bash
# SSH to VPS
ssh root@157.180.73.53

# Common commands (run from /opt/l9)
docker compose ps                    # Check service status
docker compose logs -f l9-api        # Tail API logs
docker compose restart l9-api        # Restart API
source .env                          # Load environment
make vps-status                      # Full status check (from local)
```

---

## 🔴 CRITICAL: Post-Commit Tasks

### 1. Neo4j Repo Graph Setup

**After pulling latest code:**

```bash
cd /opt/l9
git pull origin main

# 1. Verify Neo4j running
docker ps --filter "name=neo4j"

# 2. Check/set credentials
grep NEO4J_PASSWORD .env
# If missing: echo "NEO4J_PASSWORD=<password>" >> .env

# 3. Run repo index + Neo4j load
source .env
python3 tools/export_repo_indexes.py
python3 scripts/load_indexes_to_neo4j.py

# 4. Verify (expect ~1,900+ classes)
python3 -c "
from neo4j import GraphDatabase
import os
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', os.getenv('NEO4J_PASSWORD')))
with driver.session() as s:
    r = s.run('MATCH (c:RepoClass) RETURN count(c) as count')
    print(f'Classes loaded: {r.single()[\"count\"]}')
driver.close()
"
```

- [ ] Neo4j credentials verified
- [ ] Index files generated (33 files)
- [ ] Graph loaded (~1,910 classes, ~5,273 methods)

---

## 🟠 HIGH: Database Migrations

### Run Pending Migrations

```bash
cd /opt/l9
source .env

# Check which migrations exist
ls -la migrations/*.sql

# Run migrations (adjust for your DB setup)
for f in migrations/*.sql; do
  echo "Running: $f"
  PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -f "$f"
done
```

**Current migrations (0001-0011):**
- [ ] 0001_init_memory_substrate.sql
- [ ] 0002_enhance_packet_store.sql
- [ ] 0003_init_tasks.sql
- [ ] 0004_init_world_model_entities.sql
- [ ] 0005_init_knowledge_facts.sql
- [ ] 0006_init_world_model_updates.sql
- [ ] 0007_init_world_model_snapshots.sql
- [ ] 0008_memory_substrate_10x.sql
- [ ] 0009_feedback_and_effectiveness.sql
- [ ] 0011_tool_audit_log.sql

---

## 🟠 HIGH: Service Deployment

### Deploy Latest Code

```bash
cd /opt/l9
git pull origin main

# Method 1: Using deploy script
./deploy/deploy.sh

# Method 2: Manual
docker compose build l9-api
docker compose up -d
docker compose logs -f l9-api
```

### Verify All Services Running

```bash
docker compose ps

# Expected services:
# - l9-api (healthy)
# - l9-postgres (healthy)
# - neo4j (healthy)
# - redis (running)
# - jaeger (optional)
# - prometheus (optional)
```

- [ ] l9-api container healthy
- [ ] l9-postgres container healthy
- [ ] neo4j container healthy
- [ ] redis container running

---

## 🟡 MEDIUM: Environment Verification

### Check Required Environment Variables

```bash
cd /opt/l9
grep -E "^[A-Z]" .env | grep -v "^#" | cut -d= -f1 | sort
```

**Required variables:**
- [ ] `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`
- [ ] `NEO4J_USER` / `NEO4J_PASSWORD`
- [ ] `REDIS_URL` (if external)
- [ ] `OPENAI_API_KEY`
- [ ] `ANTHROPIC_API_KEY`
- [ ] `SLACK_APP_ID` / `SLACK_BOT_TOKEN` (if using Slack)

### Verify API Health

```bash
curl -s http://localhost:8000/health | jq .
# Expected: {"status": "healthy", ...}

curl -s http://localhost:8000/api/os/status | jq .
# Expected: Full system status
```

- [ ] Health endpoint returns 200
- [ ] OS status endpoint returns valid JSON

---

## 🔵 LOW: Observability

### Jaeger Tracing (Optional)

```bash
# Verify Jaeger running
docker ps --filter "name=jaeger"

# Access UI (if port forwarded)
# http://localhost:16686
```

### Prometheus Metrics (Optional)

```bash
# Verify Prometheus running
docker ps --filter "name=prometheus"

# Check metrics endpoint
curl -s http://localhost:8000/metrics | head -20
```

---

## Rollback Procedure

If deployment fails:

```bash
cd /opt/l9

# Option 1: Rollback to previous image
docker compose down
git checkout HEAD~1
docker compose up -d --build

# Option 2: Use Makefile (from local)
make rollback
```

---

## GMP-Specific Tasks

### GMP-30: Neo4j + Redis Tool Wiring
- [ ] Verify Neo4j connection from l9-api container
- [ ] Verify Redis connection from l9-api container

### GMP-31: MCP-Memory Governance
- [ ] MCP memory server configured (if running separately)

### GMP-32: Repo Index Enhancement
- [ ] Run `python3 tools/export_repo_indexes.py`
- [ ] Verify 33 index files in `readme/repo-index/`

### GMP-33: Neo4j Bootstrap Schema
- [ ] Run `python3 scripts/load_indexes_to_neo4j.py`
- [ ] Verify graph nodes created

---

## Notes

- VPS uses `/opt/l9` not `/root/L9` (Makefile has old path)
- Docker internal hostnames: `neo4j:7687`, `l9-postgres:5432`
- Host-side scripts need `localhost` for ports
- Script auto-corrects `bolt://neo4j:7687` → `bolt://localhost:7687`

---

## Machine-Readable Metadata

```yaml
vps:
  host: 157.180.73.53
  user: root
  path: /opt/l9
  
services:
  - name: l9-api
    port: 8000
    health: /health
  - name: l9-postgres
    port: 5432
  - name: neo4j
    bolt_port: 7687
    http_port: 7474
  - name: redis
    port: 6379

last_updated: 2026-01-06
pending_tasks: 15
critical_tasks: 1
```

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | L9-OPER-004 |
| **Component Name** | Todo On Vps |
| **Module Version** | 1.0.0 |
| **Created At** | 2026-01-08T03:17:26Z |
| **Created By** | L9_DORA_Injector |
| **Layer** | operations |
| **Domain** | TODO-ON-VPS.md |
| **Type** | schema |
| **Status** | active |
| **Governance Level** | medium |
| **Compliance Required** | True |
| **Audit Trail** | True |
| **Purpose** | Documentation for TODO ON VPS |

---
