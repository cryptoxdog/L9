# QUICK START: VPS Docker Deployment (Your 4-Service Setup)

**For L9 @ 157.180.73.53 (root) @ /opt/l9**

---

## 30-Second Overview

You have **4 services in docker-compose.yml** (redis, neo4j, postgres, l9-api).

**OLD PROBLEM:** `docker compose build --no-cache l9-api` only built 1 service → 3 missing on VPS

**FIX:** Use new deployment scripts that handle all 4 services automatically

---

## What You Need to Do (TODAY)

### 1. Download 5 Files from This Conversation
```
√ docker-validator.sh
√ vps-deploy-helper.sh
√ l9-deploy-runner-updated.sh
√ DOCKER-DEPLOYMENT-GUIDE.md
√ INTEGRATION-CHECKLIST-UPDATED.md (the updated one with 4-service info)
```

### 2. Copy to Your Repo
```bash
cd /path/to/l9
cp ~/Downloads/docker-validator.sh ./
cp ~/Downloads/vps-deploy-helper.sh ./
cp ~/Downloads/l9-deploy-runner-updated.sh ./
cp ~/Downloads/DOCKER-DEPLOYMENT-GUIDE.md ./
cp ~/Downloads/INTEGRATION-CHECKLIST-UPDATED.md ./

chmod +x docker-validator.sh vps-deploy-helper.sh l9-deploy-runner-updated.sh
```

### 3. Test Locally
```bash
cd /path/to/l9

# Quick validation (30 seconds)
./docker-validator.sh check-only

# If it passes, you're good!
# If not, it shows which service failed

# Full test (builds all 4 services, ~10-15 min)
./docker-validator.sh build
```

### 4. Commit & Push
```bash
git add docker-validator.sh vps-deploy-helper.sh l9-deploy-runner-updated.sh \
        DOCKER-DEPLOYMENT-GUIDE.md INTEGRATION-CHECKLIST-UPDATED.md

git commit -m "feat: add multi-service deployment system for 4-service stack"
git push origin main
```

### 5. Deploy (When Ready)
```bash
# From your local machine
./l9-deploy-runner-updated.sh 0.6.1-l9

# Follows entire pipeline:
# Step 1: Validates git + Docker
# Step 2: Local build (all 4 services)
# Step 3: Tests
# Step 4: Coverage approval
# Step 5: ORACLE verification
# Step 6: Tags + pushes
# Step 7: Deploys to VPS (automatically or manual confirmation)
```

---

## What Each Script Does (For Your 4 Services)

### docker-validator.sh
**Runs on your machine, before commit**

```bash
./docker-validator.sh check-only
# Phase 1: Discovers docker-compose.yml (finds redis, neo4j, postgres, l9-api)
# Phase 2: Validates YAML syntax
# Phase 3: Checks all referenced Dockerfiles exist
# Phase 4: Validates build contexts
# Phase 5: Validates Dockerfile structure
# Result: ✓ or ✗ (error message)

./docker-validator.sh build
# Same as above, then actually builds all 4 services locally
# Ensures "if it builds here, it'll build on VPS"
```

### vps-deploy-helper.sh
**Runs on VPS, after git checkout**

```bash
ssh root@157.180.73.53
cd /opt/l9
./vps-deploy-helper.sh v0.6.1-l9

# Phase 1: Discover services (finds 4)
# Phase 2: Detect changes (smart rebuild)
# Phase 3: Validate docker-compose.yml
# Phase 4: Backup current state
# Phase 5: Build all 4 services
# Phase 6: Stop old containers
# Phase 7: Start new containers
# Phase 8: Health check all 4
# Phase 9: Post-deploy verification
```

### l9-deploy-runner-updated.sh
**Master orchestrator, runs on your machine**

```bash
./l9-deploy-runner-updated.sh 0.6.1-l9

# Step 1: Validate git (no uncommitted changes)
# Step 2: Local SIM (calls docker-validator.sh build)
# Step 3: Run tests (pytest)
# Step 4: Coverage approval (manual gate)
# Step 5: ORACLE verification (manual gate)
# Step 6: Git tag + push
# Step 7: VPS deploy (calls vps-deploy-helper.sh or asks for confirmation)
```

---

## Your Current Setup (What Gets Deployed)

```
docker-compose.yml
├─ redis:7-alpine
│  ├─ Port: 6379 (internal)
│  ├─ Volume: redis_data
│  └─ Health: redis-cli ping
│
├─ neo4j:5-community
│  ├─ Ports: 7474 (HTTP), 7687 (Bolt)
│  ├─ Volumes: neo4j_data, neo4j_logs
│  └─ Health: wget http://localhost:7474
│
├─ l9-postgres:pgvector:pg16
│  ├─ Port: 5432 (internal)
│  ├─ Volume: postgres_data
│  └─ Health: pg_isready
│
└─ l9-api (runtime/Dockerfile)
   ├─ Port: 8000
   ├─ Depends on: All 3 above (healthy)
   └─ Health: curl /health

Network: l9-network (all 4 connected)
```

---

## Common Deployment Scenarios

### Scenario 1: Update Just the API
```bash
vim runtime/Dockerfile
# or
vim api/server.py

./docker-validator.sh check-only  # Should pass
git commit -m "fix: api changes"
git push origin main

# Later:
./l9-deploy-runner-updated.sh 0.6.1-l9  # Rebuilds l9-api only (redis/neo4j cached)
```

### Scenario 2: Update Docker Compose (Add New Service)
```bash
vim docker-compose.yml
# Add new service entry

./docker-validator.sh check-only  # Validates new service
./docker-validator.sh build       # Builds all 4 + new one

git commit -m "feat: add new service"
git push origin main

./l9-deploy-runner-updated.sh 0.6.2-l9  # Deploys all 5 services
```

### Scenario 3: Update Requirements.txt
```bash
vim requirements.txt
# Add new dependency

./docker-validator.sh build  # Rebuilds l9-api with new deps
git commit -m "deps: add new package"
git push origin main

./l9-deploy-runner-updated.sh 0.6.1-l9  # Deploys with new deps
```

### Scenario 4: Emergency Rollback
```bash
# On VPS
ssh root@157.180.73.53
cd /opt/l9
git checkout previous-tag
docker compose down
docker compose up -d

# Or from local machine
make rollback  # (if implemented)
```

---

## VPS Post-Deployment Tasks

**From TODO-ON-VPS.md - Do AFTER deployment succeeds**

```bash
ssh root@157.180.73.53
cd /opt/l9

# 1. Neo4j Repo Graph (CRITICAL - must do)
python3 tools/export_repo_indexes.py
python3 scripts/load_indexes_to_neo4j.py
# Expected: ~1,910 classes loaded, ~5,273 methods

# 2. Database Migrations (HIGH)
for f in migrations/*.sql; do
  PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER \
    -d $POSTGRES_DB -f "$f"
done

# 3. Verify Services (MEDIUM)
docker compose ps
# Expected: All 4 healthy (redis, neo4j, l9-postgres, l9-api)

curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}
```

---

## Troubleshooting

### docker-validator.sh fails at Phase 2
**Problem:** docker-compose.yml invalid syntax
```bash
# Check syntax
docker-compose config

# Fix and retry
./docker-validator.sh check-only
```

### docker-validator.sh fails at Phase 3
**Problem:** Referenced Dockerfile doesn't exist
```bash
# Check what docker-compose.yml references
grep "dockerfile:" docker-compose.yml

# Verify file exists
ls -la runtime/Dockerfile

# Fix path or create file, then retry
```

### docker-validator.sh build fails
**Problem:** One of the 4 services failed to build
```bash
# Logs show which service + error
# Example: "l9-api: pip install failed"

# Fix the issue locally, then retry
./docker-validator.sh build
```

### VPS deployment fails at health check
**Problem:** One of 4 services didn't start properly
```bash
# ssh to VPS and check
ssh root@157.180.73.53
cd /opt/l9
docker compose logs l9-api --tail=50  # Check API logs
docker compose logs neo4j --tail=50   # Check Neo4j logs
# etc.

# vps-deploy-helper.sh will auto-rollback
# Fix locally, rebuild, redeploy
```

---

## Key Differences from Old System

| Aspect | Old | New |
|--------|-----|-----|
| **Build Command** | `docker compose build l9-api` | `docker compose build` (all 4) |
| **VPS Build** | Manual on VPS | Smart helper script |
| **Service Discovery** | Implicit (hoped for) | Explicit (docker-compose.yml) |
| **Dependencies** | Ignored | Honored (depends_on) |
| **Health Checks** | None | All 4 services |
| **Volumes** | Unknown | Managed + backed up |
| **Rollback** | Manual | Automatic |
| **Validation** | Never | Before each commit |

---

## Timeline for Full Deployment

1. **Now (5 min):** Download 5 files
2. **Next (5 min):** Copy to repo + chmod
3. **Then (1 min):** Run `./docker-validator.sh check-only`
4. **When Ready (15 min):** Run `./docker-validator.sh build` (optional but recommended)
5. **Commit:** Git commit + push (2 min)
6. **Deploy:** `./l9-deploy-runner-updated.sh 0.6.1-l9` (10-20 min)
7. **Post-Deploy (10 min):** Neo4j setup (from TODO-ON-VPS.md)

**Total: ~45 minutes first time, ~15 min thereafter**

---

## Safety Features

✅ **Local validation first** - All 4 services tested locally before VPS  
✅ **Git state clean** - No uncommitted changes allowed  
✅ **Syntax validation** - docker-compose.yml checked  
✅ **Service discovery** - Automatically finds all 4  
✅ **Health checks** - Verifies each service  
✅ **State backup** - Saves current state before changes  
✅ **Auto-rollback** - Reverts if any service fails  
✅ **Clear output** - See exactly what's happening at each phase  

---

## Files to Keep Handy

```
├─ docker-validator.sh          ← Run before commit
├─ l9-deploy-runner-updated.sh  ← Run to deploy
├─ vps-deploy-helper.sh         ← Runs automatically on VPS
├─ DOCKER-DEPLOYMENT-GUIDE.md   ← Full reference
├─ INTEGRATION-CHECKLIST-UPDATED.md ← This checklist
├─ TODO-ON-VPS.md              ← Post-deploy tasks
└─ docker-compose.yml          ← Your 4-service config
```

---

## Questions?

Refer to:
1. **INTEGRATION-CHECKLIST-UPDATED.md** - Step-by-step setup
2. **DOCKER-DEPLOYMENT-GUIDE.md** - Complete reference
3. **TODO-ON-VPS.md** - VPS-specific tasks

Or run:
```bash
./docker-validator.sh --help
./vps-deploy-helper.sh --help
./l9-deploy-runner-updated.sh --help
```

---

## You're Ready! 🚀

Your 4-service stack now has:
- ✅ Automatic discovery
- ✅ Local validation
- ✅ Smart VPS deployment
- ✅ Auto-rollback
- ✅ Health verification

**Next step:**
```bash
./docker-validator.sh check-only
```

Go! 🚀

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | VPS-OPER-010 |
| **Component Name** | Quick Start 4 Services |
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
| **Purpose** | Documentation for QUICK START 4 SERVICES |

---
