# VPS Docker Multi-Service Deployment - Integration Checklist

**UPDATED FOR CURRENT SETUP: 4-Service Architecture**

---

## ✅ What You're Getting

**5 New Downloadable Files (+ existing 4):**

### Scripts (3 files)
1. **docker-validator.sh** (450 lines)
   - Discovers, validates, builds all Dockerfiles locally
   - Prevents commits with broken Docker config
   - **Now validates all 4 services in docker-compose.yml**

2. **vps-deploy-helper.sh** (400 lines)
   - Intelligent VPS deployment script
   - Handles multiple services (redis, neo4j, postgres, l9-api)
   - Auto-rollback on failure
   - **Orchestrates 4-service startup with health checks**

3. **l9-deploy-runner-updated.sh** (280 lines)
   - Updated version of l9-deploy-runner.sh
   - Step 6 now uses helper (safe for 4 services)
   - Full 7-step deployment pipeline

### Documentation (2 files)
4. **DOCKER-DEPLOYMENT-GUIDE.md** (300 lines)
   - Complete reference manual
   - Troubleshooting for all 4 services
   - Emergency procedures

5. **INTEGRATION-CHECKLIST.md** (this file)
   - Step-by-step setup guide
   - Current VPS info included
   - Verification steps for 4-service stack

---

## 🎯 Problem Fixed

**Your Current Setup (docker-compose.yml):**
- 4 Services: redis, neo4j, l9-postgres, l9-api
- 4 Volumes: postgres_data, redis_data, neo4j_data, neo4j_logs
- 1 Network: l9-network
- 40+ Environment Variables

**OLD DEPLOYMENT ISSUE (Step 6):**
```bash
# This line failed with 4 services:
docker compose build --no-cache l9-api
# ✗ Only builds l9-api
# ✗ Ignores redis, neo4j, postgres volumes
# ✗ Network not created properly
# ✗ Dependencies not honored
# ✗ Result: 3 services missing on VPS
```

**NEW SOLUTION (Step 6):**
```bash
# Now runs vps-deploy-helper.sh instead:
# ✓ Discovers ALL 4 services from docker-compose.yml
# ✓ Builds in correct order (handles depends_on)
# ✓ Creates network, volumes, volumes
# ✓ Health checks all 4 services
# ✓ Auto-rollback if any fails
```

---

## 📋 Integration Steps (Copy & Paste)

### Step 1: Download All 5 Files
```bash
# From this conversation, download:
# - docker-validator.sh
# - vps-deploy-helper.sh
# - l9-deploy-runner-updated.sh
# - DOCKER-DEPLOYMENT-GUIDE.md
# - This file (INTEGRATION-CHECKLIST.md)
```

### Step 2: Backup Old Deployment Script
```bash
cd /path/to/l9/repo

# Rename old version (if it exists)
if [ -f l9-deploy-runner.sh ]; then
  mv l9-deploy-runner.sh l9-deploy-runner.sh.backup-$(date +%Y%m%d)
  git add l9-deploy-runner.sh.backup*
fi
```

### Step 3: Add New Files to Repo
```bash
cd /path/to/l9/repo

# Copy the 5 new files
cp ~/Downloads/docker-validator.sh ./
cp ~/Downloads/vps-deploy-helper.sh ./
cp ~/Downloads/l9-deploy-runner-updated.sh ./
cp ~/Downloads/DOCKER-DEPLOYMENT-GUIDE.md ./
cp ~/Downloads/INTEGRATION-CHECKLIST.md ./

# Make scripts executable
chmod +x docker-validator.sh
chmod +x vps-deploy-helper.sh
chmod +x l9-deploy-runner-updated.sh

# Verify
ls -la docker-validator.sh vps-deploy-helper.sh l9-deploy-runner-updated.sh
```

### Step 4: Verify Current docker-compose.yml
```bash
cd /path/to/l9/repo

# Your current file should have 4 services
docker-compose config | grep "^  [a-z]" | head -10

# Expected output:
#   l9-api:
#   l9-postgres:
#   neo4j:
#   redis:
```

### Step 5: Test the Validator Locally
```bash
cd /path/to/l9/repo

# Run validator in check-only mode
./docker-validator.sh check-only

# Expected output:
# [INFO] Phase 1: Discovering Docker files...
# [✓] Found compose file: docker-compose.yml
# [✓] Found Dockerfile: runtime/Dockerfile
# [INFO] Phase 2: Validating docker-compose syntax...
# [✓] Valid: docker-compose.yml
# [INFO] Phase 3: Validating Dockerfile references...
# [✓] Found: runtime/Dockerfile (for l9-api)
# [INFO] Phase 4: Validating build contexts...
# [✓] Build context exists: ./
# [✓] ALL CHECKS PASSED

# If it fails, shows errors - fix docker-compose.yml
```

### Step 6: Validate Locally (Full Build)
```bash
cd /path/to/l9/repo

# Full local validation with build
./docker-validator.sh validate-only

# Then build locally to be 100% sure
./docker-validator.sh build

# This will:
# 1. Build redis (alpine base, fast)
# 2. Build neo4j (larger image)
# 3. Build l9-postgres (pgvector, ~2min)
# 4. Build l9-api (runs requirements.txt + code)
# 5. Report success or specific failure
```

### Step 7: Commit to Git
```bash
cd /path/to/l9/repo

git add docker-validator.sh vps-deploy-helper.sh l9-deploy-runner-updated.sh \
        DOCKER-DEPLOYMENT-GUIDE.md INTEGRATION-CHECKLIST.md

git status  # Verify 5 files staged

git commit -m "feat: add multi-service docker deployment system

- docker-validator.sh: Discover and validate all 4 services locally
- vps-deploy-helper.sh: Smart VPS deployment (handles dependencies)
- l9-deploy-runner-updated.sh: Updated orchestration (Step 6 now safe)
- DOCKER-DEPLOYMENT-GUIDE.md: Complete reference
- INTEGRATION-CHECKLIST.md: Setup guide with 4-service info

Fixes Step 6 issue where only l9-api built, missing redis/neo4j/postgres.
Now validates locally, ensures all services load properly on VPS."

git push origin main
```

---

## 🚀 First Real Deployment with 4 Services

Once integrated:

```bash
cd /path/to/l9/repo

# Make your changes (e.g., update Dockerfile)
vim runtime/Dockerfile
# or
vim docker-compose.yml

# Test locally (all 4 services)
./docker-validator.sh build

# If it passes, you're done testing!
git add .
git commit -m "feat: update docker setup"
git push origin main

# Deploy to VPS (one command)
./l9-deploy-runner-updated.sh 0.6.1-l9

# Follow the prompts:
# Step 1: Validate git + Docker
# Step 2: Local SIM (builds all 4)
# Step 3: Run tests
# Step 4: Coverage approval
# Step 5: ORACLE verification
# Step 6: Git tag + push
# Step 7: VPS deployment (runs helper)
#   └─ Discovers 4 services
#   └─ Builds all 4
#   └─ Starts redis → neo4j → postgres → l9-api
#   └─ Health checks all 4
#   └─ Success!

# Verify
curl https://l9.quantumaipartners.com/health
# Should return: {"status": "healthy", ...}
```

---

## 📝 Your Current VPS Status

### Services in docker-compose.yml
```
✓ redis:7-alpine           (Port: 6379, health: redis-cli)
✓ neo4j:5-community        (Port: 7687, health: wget)
✓ l9-postgres:pgvector     (Port: 5432, health: pg_isready)
✓ l9-api (runtime/Dockerfile) (Port: 8000, health: curl /health)
```

### Network & Volumes
```
✓ l9-network (bridge, all 4 services connected)
✓ postgres_data (persistent database)
✓ redis_data (persistent cache)
✓ neo4j_data (persistent graph)
✓ neo4j_logs (persistent logs)
```

### Environment Variables (40+)
```
✓ DATABASE_URL (l9-postgres:5432)
✓ MEMORY_DSN (l9-postgres:5432)
✓ REDIS_HOST (redis)
✓ NEO4J_URI (bolt://neo4j:7687)
✓ OPENAI_API_KEY (required)
✓ SLACK_* vars (optional)
✓ TWILIO_* vars (optional)
✓ CALENDAR_ADAPTER_* vars (optional)
```

---

## ⚠️ Important Notes for 4-Service Setup

### Network Hostnames (Inside Docker)
```bash
# Internal (inside containers)
l9-postgres:5432      # PostgreSQL
redis:6379            # Redis
neo4j:7687            # Neo4j (Bolt)
neo4j:7474            # Neo4j (HTTP)

# External (from host/VPS)
localhost:5432        # PostgreSQL
localhost:6379        # Redis
localhost:7687        # Neo4j Bolt
localhost:7474        # Neo4j HTTP
localhost:8000        # L9 API
```

### Scripts are Production-Ready for 4 Services
- Handles all 4 services in correct order
- Respects depends_on conditions
- Validates each service independently
- Clear error messages per service
- Auto-rollback if any service fails
- Health checks on all 4

### VPS Setup (from TODO-ON-VPS.md)
```bash
ssh root@157.180.73.53  # Note: root (not admin)
cd /opt/l9
docker compose ps       # All 4 should show healthy

# Critical post-deploy task:
python3 tools/export_repo_indexes.py
python3 scripts/load_indexes_to_neo4j.py
# Loads ~1,910 classes into Neo4j graph
```

### No Manual VPS Build Anymore
```bash
# ❌ OLD (broken with 4 services)
docker compose build --no-cache l9-api

# ✅ NEW (safe, handles all 4)
./vps-deploy-helper.sh v0.6.1-l9
```

---

## 🔍 Verify Integration

After adding files, you should have:

```bash
# In repo root:
ls -la docker-validator.sh           # ✓ Should exist
ls -la vps-deploy-helper.sh          # ✓ Should exist
ls -la l9-deploy-runner-updated.sh   # ✓ Should exist
ls -la DOCKER-DEPLOYMENT-GUIDE.md    # ✓ Should exist
ls -la INTEGRATION-CHECKLIST.md      # ✓ Should exist (this file)

# Should be executable:
[ -x docker-validator.sh ] && echo "✓" || echo "✗"
[ -x vps-deploy-helper.sh ] && echo "✓" || echo "✗"
[ -x l9-deploy-runner-updated.sh ] && echo "✓" || echo "✗"

# Verify docker-compose.yml has 4 services:
docker-compose config | grep "^services:" -A 100 | grep "^  [a-z]" | wc -l
# Should output: 4
```

---

## 🎓 Quick Reference

```bash
# BEFORE COMMITTING (validate all 4 services)
./docker-validator.sh check-only

# BEFORE DEPLOYING (full local test)
./docker-validator.sh build

# DEPLOY TO VPS (orchestrates all 4)
./l9-deploy-runner-updated.sh 0.6.1-l9

# TROUBLESHOOTING (see all 4 services)
./docker-validator.sh --help
./vps-deploy-helper.sh --help

# READ THE GUIDE
cat DOCKER-DEPLOYMENT-GUIDE.md
```

---

## ✅ Checklist: Before Your First Deployment

- [ ] Downloaded all 5 files
- [ ] Copied to repo root
- [ ] Made scripts executable (`chmod +x`)
- [ ] Verified docker-compose.yml has 4 services
- [ ] Ran `./docker-validator.sh check-only` ✓
- [ ] Ran `./docker-validator.sh build` ✓ (all 4 services)
- [ ] Committed to git
- [ ] Pushed to origin
- [ ] Ready to deploy!

---

## 🎉 You're All Set

Your deployment system now handles:
- ✅ Discovers ALL 4 services (not just l9-api)
- ✅ Validates before VPS (prevents failures)
- ✅ Builds safely with correct dependencies
- ✅ Creates network and volumes
- ✅ Health checks all 4 services
- ✅ Auto-rollback (if any service fails)
- ✅ Clear error messages (easy debugging)

**Next deploy command:**
```bash
./l9-deploy-runner-updated.sh 0.6.1-l9
```

That's it. Everything else is automated. 🚀

---

## Post-Deployment VPS Tasks

After successful deploy, complete from TODO-ON-VPS.md:

```bash
ssh root@157.180.73.53
cd /opt/l9

# 1. Neo4j Repo Graph (CRITICAL)
python3 tools/export_repo_indexes.py      # Generates 33 index files
python3 scripts/load_indexes_to_neo4j.py  # Loads ~1,910 classes

# 2. Database Migrations (HIGH)
for f in migrations/*.sql; do
  PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -f "$f"
done

# 3. Verify All Services (MEDIUM)
docker compose ps          # All 4 healthy?
curl http://localhost:8000/health
curl http://localhost:8000/api/os/status
```

All documented in TODO-ON-VPS.md!
