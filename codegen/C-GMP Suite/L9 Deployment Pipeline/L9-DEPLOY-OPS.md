# L9 Deployment Pipeline: Integration & Operations Guide
## How to Operationalize the System

**Last Updated:** 2025-12-21  
**Status:** Complete, ready for rollout  
**Audience:** DevOps, senior engineers, autonomous agents

---

## Overview: Three Documents, One System

This deployment pipeline is specified in **three complementary documents**:

1. **L9-DEPLOY-PIPELINE.md** — Theoretical foundations, invariants, protocols, and design rationale
2. **L9-DEPLOY-KIT.md** — Production-ready scripts, templates, and implementations
3. **L9-DEPLOY-OPERATIONS.md** (this file) — How to integrate and operate the system

---

## Part 1: Quick Start (First Deployment in 10 Minutes)

### Prerequisites

- [ ] VPS access via SSH (user: `admin`, IP: `157.180.73.53`)
- [ ] Git repo cloned locally with `main` branch
- [ ] Docker and Docker Compose installed locally and on VPS
- [ ] `.env` file in place on VPS at `/opt/l9/.env` (production credentials)

### Checklist: One-Time Setup

```bash
# Local machine (repository root)
cd /path/to/l9-repo

# 1. Create scripts directory
mkdir -p scripts

# 2. Copy all scripts from L9-DEPLOY-KIT.md
# → .git/hooks/pre-commit
# → scripts/create-release-tag.sh
# → scripts/deploy.sh
# → scripts/drift-check.sh
# → scripts/validate-env.sh

# 3. Make scripts executable
chmod +x .git/hooks/pre-commit
chmod +x scripts/*.sh

# 4. Test locally
./scripts/validate-env.sh .env.example .env.local

# 5. SSH to VPS and verify structure
ssh l9
  ls -la /opt/l9/docker/docker-compose.yml
  cat /opt/l9/.env | head
  exit

# 6. Copy rollback script to VPS
scp scripts/rollback.sh l9:/opt/l9/scripts/rollback.sh
ssh l9 chmod +x /opt/l9/scripts/rollback.sh

# 7. Install cron job on VPS for drift checking
ssh l9 << 'EOF'
  sudo tee /etc/cron.d/l9-maintenance > /dev/null << 'CRON'
  SHELL=/bin/bash
  PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
  0 * * * * /opt/l9/scripts/drift-check.sh >> /var/log/l9-drift-check.log 2>&1
  CRON
  sudo systemctl restart cron
EOF

echo "✅ Setup complete"
```

### First Deployment

```bash
cd /path/to/l9-repo

# 1. Make a change, test locally, commit
git commit -m "feat: new memory endpoint"
# (pre-commit hook will run CGMP tests automatically)

# 2. Create release tag
./scripts/create-release-tag.sh patch
# Prompted: creates v0.5.1-l9, pushes to origin

# 3. Deploy to VPS (one command, fully automated)
./scripts/deploy.sh v0.5.1-l9
# Runs:
#   - Local validation (tests, git status)
#   - Git push (commits + tags)
#   - VPS deployment (checkout, build, health checks, smoke tests)
#   - Verification (external endpoint test)

# 4. Verify live
curl https://l9.quantumaipartners.com/health | jq .

echo "✅ Deployment complete"
```

### Rollback (If Needed)

```bash
# SSH to VPS
ssh l9

# View deployment history
cat /opt/l9/.deployed-metadata.json | jq .

# Rollback (one command)
/opt/l9/scripts/rollback.sh v0.5.0-l9

# Verify
curl http://127.0.0.1:8000/health | jq .

exit
```

---

## Part 2: Daily Operations

### 2.1 Standard Development Flow

```
┌─ Work on feature branch ─┐
│                          │
├─ Make changes            │
├─ Test locally:           │
│  - Run CGMP locally      │
│  - Manual tests          │
│                          │
├─ Commit changes          │
│  (pre-commit runs tests) │
│                          │
├─ Create PR against main  │
│  - Code review           │
│  - CI checks (if using)  │
│                          │
└─ Merge to main ──────────┘
                  │
             ┌────▼─────┐
             │           │
             ▼           ▼
        Hotfix?      Regular release?
             │           │
             │           └─ Create release tag
             │              ./scripts/create-release-tag.sh [major|minor|patch]
             │                    │
             │                    ▼
             └──────────────► Deploy tag
                            ./scripts/deploy.sh vX.Y.Z-l9
```

### 2.2 Weekly Audit

**Every Monday (or weekly):**

```bash
# Check drift detection logs
ssh l9 tail -50 /var/log/l9-drift-check.log

# Should see:
# [DRIFT] ✅ Git status clean
# [DRIFT] ✅ Running version matches deployed tag: v0.5.1-l9
# [DRIFT] ✅ Container is running
# [DRIFT] ✅ Container health: healthy
# [DRIFT] ✅ Database connected
# [DRIFT] ✅ No drift detected.
```

**If drift detected:**

```bash
ssh l9
  # Investigate what changed
  git status --porcelain
  git log -1 --oneline
  
  # If unauthorized change: rollback to last known good
  /opt/l9/scripts/rollback.sh <previous-tag>
  
  # Investigation notes (for team)
  echo "Drift detected at $(date). Rolled back to v0.5.0-l9" >> /var/log/l9-drift-log.txt
exit
```

### 2.3 Monthly Dependency Updates

```bash
# Local machine
cd /path/to/l9-repo

# 1. Create feature branch
git checkout -b feature/update-deps-2025-12

# 2. Update requirements
pip install -U pip setuptools wheel
pip list --outdated

# 3. Selectively update (with caution)
# Edit requirements.txt, update pinned versions
# OR use Poetry: poetry update (if using Poetry)

# 4. Build and test locally
docker compose build --no-cache l9-api
docker compose run --rm test pytest tests/ -v

# 5. Commit
git add requirements.txt
git commit -m "chore: update dependencies to latest stable versions

- fastapi: 0.104.1 → 0.105.0
- uvicorn: 0.24.0 → 0.24.1
- psycopg: 3.1.18 → 3.1.19

All tests pass locally. No breaking changes detected."

# 6. Push and create PR
git push origin feature/update-deps-2025-12

# 7. After merge and approval
./scripts/create-release-tag.sh minor
./scripts/deploy.sh vX.Y.Z-l9
```

### 2.4 Emergency Hotfix

```bash
cd /path/to/l9-repo

# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-12345

# 2. Make minimal fix
# (edit one file, fix issue)

# 3. Commit
git commit -m "fix: critical bug in memory.insert_embedding

Prevents deadlock under concurrent load.
Root cause: connection lock held during async operation.
Fix: Release lock immediately after queueing task.

Fixes: #12345
Hotfix: yes"

# 4. Merge immediately to main (bypassing PR if critical)
git checkout main
git pull origin main
git merge --no-ff hotfix/critical-bug-12345

# 5. Tag and deploy immediately
./scripts/create-release-tag.sh patch
./scripts/deploy.sh vX.Y.Z-l9

# 6. Verify
curl https://l9.quantumaipartners.com/health

# 7. Post-deployment review
# Document root cause, prevention measures, testing gaps
```

---

## Part 3: Monitoring and Alerting

### 3.1 VPS Health Monitoring

**Add to your monitoring system** (e.g., Prometheus, Datadog, CloudWatch):

```bash
# Health endpoint
curl https://l9.quantumaipartners.com/health

# Expected response (200 OK):
# {
#   "status": "healthy",
#   "service": "L9 Phase 2 Memory System",
#   "version": "0.5.1",
#   "database": "connected",
#   "memory_system": "operational"
# }
```

**Alert thresholds:**

| Metric | Threshold | Action |
|--------|-----------|--------|
| `/health` HTTP 200 | Not returning 200 for 5 min | Page on-call |
| Container Health | Unhealthy for 10 min | Auto-restart or escalate |
| Logs "Traceback" | Any occurrence | Alert + investigate |
| Drift detected | Any occurrence | Alert + manual review |
| Deployment failure | Any deployment fails | Auto-rollback + alert |

**Example Prometheus alert:**

```yaml
groups:
  - name: l9
    rules:
      - alert: L9HealthCheckFailing
        expr: up{job="l9-health"} == 0
        for: 5m
        annotations:
          summary: "L9 health endpoint failing"
          runbook: "https://internal.wiki/l9/runbooks/health-failing"
      
      - alert: L9DriftDetected
        expr: l9_drift_detected == 1
        for: 1m
        annotations:
          summary: "L9 VPS state drifted from git"
          runbook: "https://internal.wiki/l9/runbooks/drift-detected"
```

### 3.2 Log Aggregation

**Centralize logs from all deployments:**

```bash
# On VPS, ensure logs are accessible
docker logs l9-api --tail 1000 > /tmp/l9-logs.txt

# Aggregate to centralized logging (Datadog, Splunk, ELK, etc.)
# Example with rsyslog:
echo "*.* @@logs.example.com:514" | sudo tee -a /etc/rsyslog.d/99-l9.conf
sudo systemctl restart rsyslog
```

**Key log patterns to monitor:**

```bash
# Errors (should be rare)
docker logs l9-api | grep -i "error\|exception\|traceback"

# Deployment events
tail -f /var/log/l9-drift-check.log

# Container restarts
docker inspect l9-api | jq .State.RestartCount
```

---

## Part 4: Disaster Recovery

### 4.1 Backup and Restore Strategy

**Data persistence:**

L9 uses PostgreSQL for persistent data. **Back up the database, not the Docker container.**

```bash
# On VPS, schedule nightly backups
# Add to crontab:
# 0 2 * * * pg_dump -U postgres l9_memory | gzip > /backups/l9_memory_$(date +\%Y\%m\%d).sql.gz

# Manual backup
ssh l9
  sudo -u postgres pg_dump l9_memory | gzip > /tmp/l9_memory_backup.sql.gz
  scp /tmp/l9_memory_backup.sql.gz local-backup-drive:/backups/
exit

# Restore (if needed)
ssh l9
  scp local-backup-drive:/backups/l9_memory_backup.sql.gz /tmp/
  gunzip < /tmp/l9_memory_backup.sql.gz | sudo -u postgres psql l9_memory
exit
```

**Container layer:**

Container images are ephemeral and reproducible. No backup needed—rebuild from git tag:

```bash
# If image corrupted or lost:
/opt/l9/scripts/rollback.sh v0.5.0-l9
# Automatically pulls/builds from git tag and restarts
```

### 4.2 Multi-Region Failover (Future)

If operating multiple VPS instances:

```bash
# Primary VPS
VPS_PRIMARY="157.180.73.53"

# Secondary VPS (standby)
VPS_SECONDARY="157.180.73.54"

# Failover script (manual):
#!/usr/bin/env bash
PRIMARY=$VPS_PRIMARY
SECONDARY=$VPS_SECONDARY

# 1. Test primary health
if ! curl -s https://l9.quantumaipartners.com/health | jq . > /dev/null; then
    echo "Primary unhealthy. Failing over to secondary..."
    
    # 2. Get current tag from primary (if accessible)
    CURRENT_TAG=$(ssh admin@$PRIMARY "cat /opt/l9/.deployed-metadata.json | jq -r .deployed_tag" 2>/dev/null || echo "v0.5.0-l9")
    
    # 3. Deploy to secondary
    ssh admin@$SECONDARY "/opt/l9/scripts/rollback.sh $CURRENT_TAG"
    
    # 4. Update DNS to point to secondary
    # (manual or via API call to DNS provider)
    
    echo "Failover complete. Secondary is now primary."
fi
```

---

## Part 5: Runbooks (Common Scenarios)

### Scenario 1: Deploy a Bug Fix

```bash
# Time: ~5 minutes
# Risk: Low (single file change, tested locally)

# 1. On local machine
cd /path/to/l9-repo
git checkout main
git pull origin main

# Create bugfix branch
git checkout -b bugfix/jwt-expiry-12345

# Make fix
vim api/auth.py
# (fix the issue)

# Test
docker compose run --rm test pytest tests/test_auth.py::test_jwt_expiry -v

# Commit
git add api/auth.py
git commit -m "fix: JWT expiry check off by one hour

The authentication check was comparing against an incorrect
timestamp, causing valid tokens to be rejected.

Tests added to prevent regression.

Fixes: #12345"

git push origin bugfix/jwt-expiry-12345

# 2. Create PR, wait for review approval

# 3. After approval
git checkout main
git pull origin main
git merge --no-ff bugfix/jwt-expiry-12345

# 4. Create release tag
./scripts/create-release-tag.sh patch
# Creates v0.5.1-l9 (e.g., v0.5.0 → v0.5.1)

# 5. Deploy
./scripts/deploy.sh v0.5.1-l9

# 6. Monitor
curl https://l9.quantumaipartners.com/health
ssh l9 docker logs l9-api --tail 20

# DONE in ~5 minutes
```

### Scenario 2: Deploy New Endpoint (Minor Feature)

```bash
# Time: ~30 minutes
# Risk: Medium (new code path, needs thorough testing)

# 1. Feature branch
git checkout -b feature/semantic-search-endpoint

# Make changes (e.g., add new route to memory router)
vim api/memory/router.py

# Add tests
vim tests/test_memory.py

# Test locally
docker compose build --no-cache l9-api
docker compose run --rm test pytest tests/test_memory.py -v

# Test with Swagger docs
docker compose up -d l9-api
# open http://127.0.0.1:8000/docs

# Commit
git add api/memory/router.py tests/test_memory.py
git commit -m "feat: add semantic search endpoint

New POST /memory/semantic/search endpoint for vector-based search
across stored embeddings.

Endpoint:
  POST /memory/semantic/search
  
Request:
  {
    \"query\": \"search terms\",
    \"limit\": 10
  }

Response:
  {
    \"results\": [...]
  }

Tests:
  - Search returns top-k results
  - Score ordering correct
  - Empty query handling
  - Pagination

Fixes: #1089"

git push origin feature/semantic-search-endpoint

# 2. Create PR, request review

# 3. Reviewers check:
#    - API contract reasonable
#    - Tests comprehensive
#    - Backward compatible
#    - Docs updated

# 4. After approval, merge
git checkout main
git merge --no-ff feature/semantic-search-endpoint

# 5. Create release
./scripts/create-release-tag.sh minor
# Creates v0.6.0-l9 (v0.5.x → v0.6.0)

# 6. Deploy
./scripts/deploy.sh v0.6.0-l9

# 7. Smoke test new endpoint
curl -X POST https://l9.quantumaipartners.com/memory/semantic/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test","limit":5}' | jq .

# DONE in ~30 minutes
```

### Scenario 3: Emergency Rollback

```bash
# Time: ~2 minutes
# Risk: High (immediate action needed)
# Reason: Deployment caused production outage

# 1. Verify issue
curl https://l9.quantumaipartners.com/health
# Returns: error or 503

# 2. SSH to VPS
ssh l9

# 3. Check logs
docker logs l9-api --tail 50 | grep -i error

# 4. Check previous tag
cat /opt/l9/.deployed-metadata.json | jq .deployed_tag

# Output might be: "v0.5.1-l9" (current broken version)
# We want to go back to: "v0.5.0-l9"

# 5. Rollback immediately
/opt/l9/scripts/rollback.sh v0.5.0-l9

# 6. Verify
curl http://127.0.0.1:8000/health | jq .
# Should return healthy response

# 7. Check from outside VPS
exit
curl https://l9.quantumaipartners.com/health | jq .

# DONE in ~2 minutes, service restored
```

### Scenario 4: Database Migration (Major Upgrade)

```bash
# Time: ~1 hour
# Risk: High (data changes, needs coordination)
# Example: Adding pgvector extension or schema migration

# 1. Plan migration locally
git checkout -b feature/pgvector-migration

# Create migration script
cat > migrations/001_add_pgvector.sql <<EOF
CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE memory.embeddings
  ADD COLUMN IF NOT EXISTS vector vector(1536);

CREATE INDEX IF NOT EXISTS embeddings_vector_idx 
  ON memory.embeddings USING ivfflat (vector vector_cosine_ops)
  WITH (lists = 100);
EOF

# Add migration code to app
vim api/db.py
# (add function to run migration if not already applied)

# Test locally with fresh database
docker compose down postgres || true
docker volume rm $(docker volume ls -q | grep l9-postgres) || true
docker compose up -d postgres
sleep 5
docker compose run --rm test pytest tests/test_migrations.py -v

# Commit migration
git add migrations/ api/db.py
git commit -m "feat: add pgvector support for semantic search

Adds pgvector extension and vector column to embeddings table.

Migration: migrations/001_add_pgvector.sql
- Creates vector(1536) column
- Creates IVFFLAT index for fast search
- Migration is idempotent (safe to run multiple times)

Testing:
- Migration applied automatically on app boot
- Existing data preserved
- New query interface works

Rollback: remove vector column and extension

Deployment notes:
- Runs before app starts (db.init_db())
- No downtime during migration
- Backward compatible (old code can still read embeddings table)"

git push origin feature/pgvector-migration

# 2. Get team approval

# 3. Schedule deployment during low-traffic window

# 4. Execute deployment
./scripts/create-release-tag.sh minor
./scripts/deploy.sh vX.Y.Z-l9

# 5. Monitor
ssh l9 docker logs l9-api --tail 50 | grep -i migration
ssh l9 docker logs l9-api --tail 50 | grep -i vector

# Should see logs like:
# "Migration: Adding pgvector support..."
# "Vector column created successfully"

# 6. Verify
curl https://l9.quantumaipartners.com/health | jq .

# DONE in ~1 hour
```

---

## Part 6: Troubleshooting Quick Guide

| Symptom | Cause | Fix |
|---------|-------|-----|
| Deployment fails at "tests" | CGMP tests not passing | `docker compose run test pytest -v`, fix issues, commit |
| Deployment fails at "VPS checkout" | Tag not pushed to origin | `git push origin <tag>` |
| Container unhealthy after deploy | Database connection issue | Check `.env` on VPS, verify PostgreSQL is running |
| Container won't start | Docker build failed | `ssh l9; docker logs l9-api` and check /tmp/docker-build-vps.log |
| `/health` returns 503 | App crashed | `ssh l9; docker logs l9-api --tail 100` |
| Traffic not reaching container | Caddy not reloaded | Check Caddy config, test locally on 8000 port |
| Drift detected | Files changed on VPS | `ssh l9; git status` to see changes, either rollback or recommit |
| Cron job not running | Cron not installed or restarted | `ssh l9; sudo systemctl status cron` |

---

## Part 7: Security Checklist

Before going live with this pipeline:

- [ ] SSH keys for VPS access are secured (not in repo)
- [ ] `.env` file on VPS has restricted permissions (`chmod 600`)
- [ ] No credentials in git history (use `.gitignore`)
- [ ] `git push` requires authentication (not anonymous)
- [ ] Tags can only be created by authorized users (team policy)
- [ ] `.deployed-metadata.json` auditable (who deployed when)
- [ ] Rollback scripts have clear audit trail
- [ ] Log aggregation sends data securely
- [ ] Drift detection alerts go to appropriate channels
- [ ] Emergency contacts documented for production issues

---

## Part 8: Conclusion: The Autonomous Pipeline is Live

With these three documents + implementation kit in place, the L9 deployment pipeline is:

✅ **Deterministic**: Same inputs → same outputs every time  
✅ **Auditable**: Every deployment tagged, traceable, with metadata  
✅ **Reversible**: Instant rollback to any previous tag  
✅ **Observable**: Health checks, logs, drift detection all automated  
✅ **Scalable**: One command deploys to any environment  
✅ **Safe**: Pre-flight checks, smoke tests, auto-rollback on failure  

**Developers can now:**
- Make changes with confidence
- Test locally in Docker (exact prod environment)
- Push to main via PR (code review)
- Create release with one script
- Deploy to production with one command
- Know immediately if something breaks
- Rollback in under 2 minutes if needed

**Ops teams can:**
- Monitor health automatically (drift checks hourly)
- Alert on failures (logs, health endpoint)
- Audit all deployments (.deployed-metadata.json)
- Enforce policy (pre-commit hooks, tag signing)
- Recover quickly (tag-based rollback)

**The autonomous agent can:**
- Execute deployments end-to-end
- Detect and fix drift automatically
- Coordinate multi-environment rollouts (future)
- Generate deployment reports
- Trigger alerts and escalations

---

**Ready to deploy. Good luck.** 🚀

