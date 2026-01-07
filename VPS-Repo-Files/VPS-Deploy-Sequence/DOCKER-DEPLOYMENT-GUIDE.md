# Multi-Dockerfile Deployment Guide

---

## ⚠️ DOCKER AUTHORITY DECLARATION

**READ THIS FIRST.** If you're an AI agent (Codex, Cursor, L) or a human developer:

### Canonical Docker Configuration

The **ONLY** authoritative Docker runtime configuration is:

| Component | Path | Status |
|-----------|------|--------|
| **Compose file** | `docker-compose.yml` (ROOT) | ✅ CANONICAL — gitignored, contains secrets |
| **API Dockerfile** | `runtime/Dockerfile` | ✅ CANONICAL |
| **SymPy Dockerfile** | `services/symbolic_computation/Dockerfile` | ✅ CANONICAL (standalone service) |

### Legacy/Reference Files (DO NOT USE FOR DEPLOYMENT)

| Path | Purpose |
|------|---------|
| `docs/_Context-L9-Repo/docker/*.yaml` | Reference documentation only |
| `docs/__01-04-2026/Governance Audit/Orphaned Files/yaml/docker-compose.yaml` | Historical artifact |

### Rules

1. **Never deploy from `docs/`** — Those are reference copies, not production.
2. **Always use ROOT `docker-compose.yml`** — It has correct env vars and secrets.
3. **Codex/AI agents:** If you find Docker config in `docs/`, **IGNORE IT** for deployment.
4. **.gitignore protects secrets** — `docker-compose.yml` is gitignored intentionally.

---

## Problem Solved

You have **multiple Dockerfiles in different locations** (runtime, services, etc) and local vs VPS differences. The new system handles this safely.

---

## Architecture: 3-Script Deployment System

### Script 1: `docker-validator.sh` (LOCAL)
**Purpose:** Validate ALL Dockerfiles before committing

**Location:** Root of repo

**When to use:**
```bash
# Before committing code with Docker changes
./docker-validator.sh check-only

# Full validation (pre-deployment)
./docker-validator.sh validate-only

# Actually build locally to verify everything
./docker-validator.sh build
```

**What it does:**
1. Discovers all `docker-compose*.yml` files
2. Discovers all `Dockerfile*` files
3. Validates compose file syntax
4. Verifies all Dockerfiles referenced in compose exist
5. Checks build contexts are valid
6. Optionally builds everything locally

**Output:**
```
✓ Dockerfile discovered at: runtime/Dockerfile
✓ Dockerfile discovered at: services/symboliccomputation/Dockerfile
✓ docker-compose.yml valid
✓ Build context exists: runtime
✓ All checks passed
```

---

### Script 2: `vps-deploy-helper.sh` (VPS)
**Purpose:** Smart deployment on VPS (handles multiple services)

**Location:** `/opt/l9/` on VPS

**How to use:**
```bash
ssh admin@157.180.73.53
cd /opt/l9
./vps-deploy-helper.sh v0.6.0-l9
```

**What it does:**
1. Validates repo state post-checkout
2. Discovers all services in docker-compose
3. Detects which Dockerfiles have changed
4. Backs up current running state
5. Builds all services (with layer caching)
6. Stops old containers gracefully
7. Starts new containers
8. Runs health checks
9. Provides rollback if anything fails

**Example output:**
```
[deploy] Phase 1: Discovering services...
[deploy]   • l9-api
[deploy]   • l9-postgres
[deploy]   • l9-redis
[deploy]   • l9-neo4j
[deploy] Phase 2: Detecting which Dockerfiles have changed...
[!] Changed: runtime/Dockerfile (will rebuild)
[deploy] Phase 5: Building services...
✓ Build completed
[deploy] Phase 7: Starting new containers...
✓ Containers started
[deploy] Phase 8: Running health checks...
✓ L9 API is healthy
✓ All health checks passed
[✓] DEPLOYMENT SUCCESSFUL
```

---

### Script 3: `l9-deploy-runner-updated.sh` (LOCAL)
**Purpose:** Orchestrate entire deployment (replaces old version)

**Location:** Root of repo

**How to use:**
```bash
./l9-deploy-runner-updated.sh 0.6.0-l9
```

**Complete flow:**
1. **Step 1:** Local validation (git, docker, structure)
2. **Step 2:** Local Docker SIM (build + boot services)
3. **Step 3:** Run tests (pytest)
4. **Step 4:** Coverage gate (approval required)
5. **Step 5:** ORACLE gate (manual verification)
6. **Step 6:** Git tag + push
7. **Step 7:** VPS deployment (checkout + run helper)

**Key difference from old version:**
- ~~No longer tries to build on VPS~~ (was failing)
- Uses `vps-deploy-helper.sh` instead (handles complexity)
- Safer separation of concerns

---

## Step-by-Step Deployment

### 1. Make Code Changes
```bash
cd /path/to/l9/repo
# Make your changes, add new services, update Dockerfiles, etc.
git add .
git commit -m "feat: add new service"
```

### 2. Validate Dockerfiles Locally
```bash
chmod +x docker-validator.sh
./docker-validator.sh build

# Output should show:
# ✓ All checks passed
# ✓ Build successful
```

### 3. Commit to Git
```bash
git push origin main
```

### 4. Deploy to VPS
```bash
chmod +x l9-deploy-runner-updated.sh
./l9-deploy-runner-updated.sh 0.6.0-l9

# Follow prompts:
# - Step 3: Tests run automatically
# - Step 4: Approve coverage results
# - Step 5: Verify system state in Cursor, approve ORACLE
# - Step 6: Code tagged and pushed
# - Step 7: VPS deployment runs automatically OR manually

# If manual:
ssh admin@157.180.73.53 'cd /opt/l9 && ./vps-deploy-helper.sh 0.6.0-l9'
```

### 5. Verify
```bash
# Check health endpoints
curl https://l9.quantumaipartners.com/health
curl https://memory.quantumaipartners.com/health

# Check running services
ssh admin@157.180.73.53 'cd /opt/l9 && docker-compose ps'
```

---

## When Things Change

### Adding a New Dockerfile
```bash
# 1. Create it
vim services/mynewservice/Dockerfile

# 2. Reference it in docker-compose.yml
vim docker-compose.yml
# Add:
# services:
#   mynewservice:
#     build:
#       context: ./services/mynewservice
#       dockerfile: Dockerfile

# 3. Validate
./docker-validator.sh check-only

# 4. Deploy normally
./l9-deploy-runner-updated.sh 0.6.0-l9
```

### Updating Multiple Dockerfiles
```bash
# Update all files as needed
vim runtime/Dockerfile
vim services/symboliccomputation/Dockerfile

# Validate finds all changes automatically
./docker-validator.sh check-only

# Deploy detects which ones changed and rebuilds intelligently
./l9-deploy-runner-updated.sh 0.6.0-l9
```

### Adding New Services to docker-compose.yml
```bash
# Update the compose file with new services
vim docker-compose.yml

# Validate syntax
docker-compose config > /dev/null

# Our validator will discover the new services automatically
./docker-validator.sh validate-only
```

---

## Troubleshooting

### "docker-compose.yml is invalid"
```bash
# Check syntax
docker-compose config

# Shows the specific error
# Fix it, then retry
./docker-validator.sh check-only
```

### "Dockerfile not found at X"
```bash
# Check the path in docker-compose.yml
grep "dockerfile:" docker-compose.yml

# Verify the file exists
ls -la path/to/Dockerfile

# Fix path or create file
./docker-validator.sh check-only
```

### "Build failed on VPS"
```bash
# SSH to VPS and check logs
ssh admin@157.180.73.53
cd /opt/l9
docker-compose logs l9-api --tail=100

# Check which service failed
docker-compose build

# The output shows which Dockerfile has issues
# Fix locally, then redeploy
```

### "Health check failed"
```bash
# Check container is running
docker-compose ps

# Check logs
docker-compose logs l9-api --tail=50

# If services didn't start, helper auto-attempts rollback
# Manual rollback:
git checkout HEAD~1
docker-compose up -d
```

---

## VPS Setup (One-Time)

Deploy helper needs to be on VPS:

```bash
ssh admin@157.180.73.53
cd /opt/l9

# Copy helper script
# (Can be committed to repo and checked out with code)
wget https://your-repo/vps-deploy-helper.sh
chmod +x vps-deploy-helper.sh

# Or check in to repo and it's available after checkout
git checkout your-branch
ls vps-deploy-helper.sh  # Should exist
```

---

## Configuration

### Environment Variables for Scripts

#### docker-validator.sh
```bash
VERBOSE=1 ./docker-validator.sh build
```

#### vps-deploy-helper.sh
```bash
# Skip build phase (use cached images)
SKIP_BUILD=1 ./vps-deploy-helper.sh v0.6.0-l9

# Verbose output
VERBOSE=1 ./vps-deploy-helper.sh v0.6.0-l9
```

#### l9-deploy-runner-updated.sh
```bash
# Run normally
./l9-deploy-runner-updated.sh 0.6.0-l9

# Skip local SIM (risky, not recommended)
# (Not exposed via env var for safety)
```

---

## Files to Commit to Repo

```
l9/
├── docker-validator.sh              ✅ Add to repo
├── vps-deploy-helper.sh             ✅ Add to repo
├── l9-deploy-runner-updated.sh      ✅ Add to repo (replace old one)
├── docker-compose.yml               (update as needed)
├── runtime/Dockerfile               (update as needed)
├── services/symboliccomputation/Dockerfile  (update as needed)
├── services/symboliccomputation/docker-compose.yml  (if needed)
└── ...
```

---

## Key Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Multiple Dockerfiles** | Manual, error-prone | Automated discovery |
| **Validation** | None, fail at deploy | Pre-deploy validation |
| **Build on VPS** | Often failed | Guaranteed to work (tested locally first) |
| **Service Detection** | Manual checking | Automatic discovery |
| **Rollback** | Manual cleanup | Automatic rollback |
| **Health Checks** | Manual verification | Automated with retries |
| **Local vs VPS** | Different behavior | Same behavior (unified) |

---

## Deployment Checklist

- [ ] Code changes committed
- [ ] `./docker-validator.sh build` passes
- [ ] Tests pass in Step 3
- [ ] Coverage approved in Step 4
- [ ] ORACLE gate approved in Step 5
- [ ] `git tag` created in Step 6
- [ ] `vps-deploy-helper.sh` runs successfully
- [ ] `curl https://l9.quantumaipartners.com/health` returns 200
- [ ] `curl https://memory.quantumaipartners.com/health` returns 200
- [ ] All expected services running: `docker-compose ps` shows all containers

---

## Emergency Procedures

### Quick Rollback
```bash
ssh admin@157.180.73.53
cd /opt/l9
git checkout v0.5.9-l9  # Go back to previous tag
docker-compose down
docker-compose up -d
curl http://127.0.0.1:8000/health
```

### Rebuild Specific Service
```bash
# On VPS
docker-compose build --no-cache l9-api
docker-compose up -d l9-api
```

### See Full Build Log
```bash
# On VPS, when running helper manually
VERBOSE=1 ./vps-deploy-helper.sh v0.6.0-l9
```

---

## Questions?

Refer to the individual script help:
```bash
./docker-validator.sh --help
./vps-deploy-helper.sh --help
./l9-deploy-runner-updated.sh --help
```

All scripts have inline documentation and error messages.
