# L9 Closed-Loop Deployment Pipeline: Specification & Design
## Autonomous Rollout Protocol for LLM Backend (Docker + Git + FastAPI)

**Last Updated:** 2025-12-21  
**Version:** 1.0 (Specification Phase)  
**Status:** READY FOR IMPLEMENTATION  
**Target Audience:** Autonomous agents, senior engineers, and integrated CI systems.

---

## Executive Summary

This document specifies a **deterministic, gated, and reversible deployment pipeline** for the L9 secure AI OS backend. The pipeline treats deployments as a **directed graph of hard gates**, where each state transition is verified by explicit invariants and observables before proceeding to the next stage.

**Core Invariant:** "One-command, low-risk, observable, and reversible—from local refactor to VPS production in a single atomic transaction, with automatic rollback on failure."

**Key Outcomes:**
- ✅ **Reproducible builds**: Locked dependencies, no drift.
- ✅ **Auditable history**: Every deployment tagged and traced.
- ✅ **Zero-downtime rollouts**: Blue-green pattern with health-aware switchovers.
- ✅ **Instant rollback**: Git tags + Docker image immutability = fast recovery.
- ✅ **Observable safety**: Health checks, smoke tests, and log inspection before traffic cutover.

---

## Part 1: Pipeline Architecture as a Gated Graph

### 1.1 The Three Canonical Substrates

The pipeline moves code through three distinct environments, each with its own constraints and invariants:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          LOCAL WORKSPACE                            │
│  Single source of truth: code, tests, locked deps, env examples     │
│  Invariant: CGMP-L9-FIX → SIM → COV → ORACLE all green              │
│  Observable: pytest exit code = 0, Docker healthcheck passes         │
└────────────────────┬────────────────────────────────────────────────┘
                     │ git push + tag (tag = release artifact)
                     ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        GIT REPOSITORY                               │
│  Canonical history: annotated tags, clean branches, audit trail     │
│  Invariant: Only tagged commits are deployed; tags are immutable    │
│  Observable: git tag -v <tag>, git log <tag>                        │
└────────────────────┬────────────────────────────────────────────────┘
                     │ git clone + git checkout <tag>
                     ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      VPS RUNTIME                                    │
│  Production environment: Docker Compose, Caddy, PostgreSQL          │
│  Invariant: healthchecks green, smoke tests pass, no drift          │
│  Observable: /health endpoint, curl tests, process status           │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 State Diagram: Deployment as a Graph of Gates

```
                         START
                           │
                           ↓
                  [LOCAL-READY]
            (git clean, no untracked files)
                           │
                  ┌────────┴────────┐
                  │                 │
         ┌────────▼──────┐   ┌──────▼────────┐
         │ BUILD & TEST  │   │ VERSION LOCK  │
         │ (Docker)      │   │ Check deps    │
         │ CGMP passes   │   │ file versions │
         └────────┬──────┘   └──────┬────────┘
                  │                 │
                  └────────┬────────┘
                           │
                           ↓
                 [TESTS-GREEN]
          (unit, integration, API smoke)
                           │
                           ↓
              [CREATE-ANNOTATED-TAG]
       (format: v<major>.<minor>.<patch>-l9)
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
    ┌───▼────────┐                      ┌────▼──────┐
    │ git push   │                      │ git push  │
    │ origin main│                      │ tags to   │
    │ (commits)  │                      │ origin    │
    └───┬────────┘                      └────┬──────┘
        │                                     │
        └──────────────────┬──────────────────┘
                           │
                           ↓
                   [TAG-IN-GIT]
              (tag exists, commits pushed)
                           │
              ┌────────────┴────────────┐
              │                         │
         ┌────▼────┐          ┌────────▼───┐
         │ SSH to  │          │ git fetch  │
         │ VPS     │          │ verify tag │
         └────┬────┘          └────────┬───┘
              │                        │
              └────────────┬───────────┘
                           │
                           ↓
                 [VPS-TAG-VERIFIED]
         (tag exists locally on VPS)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼──────┐    ┌──────▼──────┐  ┌──────▼───┐
    │ docker   │    │ docker      │  │ docker   │
    │ compose  │    │ compose     │  │ compose  │
    │ build    │    │ pull        │  │ up -d    │
    │ --no-cache   │ (if registry)│  │ --no-build   │
    └───┬──────┘    └──────┬──────┘  └──────┬───┘
        │                  │                 │
        └──────────────────┼─────────────────┘
                           │
                           ↓
             [IMAGES-READY-OR-PULLED]
       (Dockerfile built or pulled from registry)
                           │
                           ↓
            [BLUE-GREEN-LAUNCH-GREEN]
        (start new container on alternate port,
         or in docker-compose as inactive service)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼──────┐    ┌──────▼──────┐  ┌──────▼──────┐
    │ Poll     │    │ Check      │  │ Timeout     │
    │ /health  │    │ logs for   │  │ fail after  │
    │ endpoint │    │ Traceback  │  │ 60 sec      │
    │ 30 times │    │            │  │             │
    └───┬──────┘    └──────┬──────┘  └──────┬──────┘
        │                  │                 │
        └──────────────────┼─────────────────┘
                           │
                  YES ◄────┼────► NO
                  │        │        │
                  │        │    ┌───▼─────┐
                  │        │    │ ROLLBACK│
                  │        │    │ to old  │
                  │        │    │ tag     │
                  │        │    └───┬─────┘
                  │        │        │
                  │        │   ┌────▼────────┐
                  │        │   │ FAIL-STATE  │
                  │        │   │ Manual      │
                  │        │   │ review      │
                  │        │   └─────────────┘
                  │        │
                  ↓        │
       [GREEN-HEALTHY]     │
       (container passes    │
        health checks &    │
        smoke tests)        │
         │                 │
         │                 │
         ↓                 │
    [ROUTE-TRAFFIC]        │
    (Caddy switch,        │
     or proxy update)     │
         │                │
         ↓                │
   [BLUE-DRAIN]           │
   (wait SIGTERM grace)    │
         │                │
         ↓                │
   [BLUE-SHUTDOWN]        │
   (stop old container)    │
         │                │
         ↓                │
   [CLEANUP-IMAGES]       │
   (remove dangling)       │
         │                │
         ↓                │
   [SUCCESS]              │
   ✅ Production live      │
         │                │
         └────────────────┘
```

### 1.3 Deployment Invariants by Substrate

#### **LOCAL WORKSPACE**

| Invariant | Rationale | Observable Check |
|-----------|-----------|------------------|
| No untracked files (except `.env.local` patterns) | Ensures reproducibility; no hidden artifacts deployed | `git status --porcelain` ≠ empty (or only allowed patterns) |
| No uncommitted changes | Ensures all code is reviewable in git history | `git status --porcelain` shows nothing for tracked files |
| CGMP-L9 test suite passes in Docker | Ensures app logic is sound before release | `docker compose run test pytest -v` exit code = 0 |
| Dependencies locked in `pyproject.toml` and `requirements.txt` | Prevents version drift and surprises in production | `pip freeze > /tmp/lock.txt` matches expectations |
| `.env.example` documents all required keys | Enables safe environment setup without hardcoding | Manual audit: all prod vars in `.env.example` |

#### **GIT REPOSITORY**

| Invariant | Rationale | Observable Check |
|-----------|-----------|------------------|
| Only annotated tags trigger deployments | Tags are immutable; floating branches are not | `git tag -v <tag>` succeeds and shows tagger, date |
| Tag exists and is reachable from `main` | Prevents deployment of orphaned commits | `git log main \| grep <tag-ish>` |
| Commit message is clear and references context | Enables audit trail and blame if rollback needed | `git log -1 --pretty=%B <tag>` is non-empty |
| No sensitive data in committed files | Prevents credential leaks | Manual scan: no API keys, passwords in `.py` or `.txt` |

#### **VPS RUNTIME**

| Invariant | Rationale | Observable Check |
|-----------|-----------|------------------|
| Docker Compose healthcheck passes (green for 10s) | App is truly ready to serve traffic | `docker inspect l9-api \| grep -A 5 Health` |
| `/health` endpoint returns 200 + "healthy" | Critical path is working; DB connected | `curl -s http://127.0.0.1:8000/health \| jq .status` = "healthy" |
| Smoke test: POST to memory endpoint succeeds | API accepts requests and processes them | `curl -X POST http://127.0.0.1:8000/memory/packet -H "..." -d "..."` → 200 |
| Logs show no Traceback or ERROR in last 100 lines | No unhandled exceptions or critical failures | `docker logs l9-api --tail 100 \| grep -i traceback` = empty |
| No drift: running tag matches git tag on VPS | Running code is exactly what's in the repo | `cat /opt/l9/.deployed-tag` = current git tag |
| Caddy reload succeeds (status 200) | Reverse proxy is configured and routing correctly | `curl -s http://127.0.0.1:2019/config/apps/http` → valid JSON |

---

## Part 2: Local Workspace as the Single Source of Truth

### 2.1 Local Policy: Non-Bypassable CGMP Gate

The L9 system defines a disciplined local testing sequence:

```
Code Changes → [CGMP-L9-FIX] → [SIM] → [COV] → [ORACLE]
                                                      ↓
                                              All stages GREEN
                                                      ↓
                                            Eligible for commit
```

**Enforcement**: Create a **pre-commit hook** and **pre-tag script** that enforces this:

```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit (or scripts/pre-commit.sh)
set -e

echo "🔒 Running L9 pre-commit gate..."

# 1. Check git status (no untracked tracked files)
if [ -n "$(git status --porcelain | grep -v '^??')" ]; then
    echo "❌ FAIL: Uncommitted changes detected. Stage them first."
    exit 1
fi

# 2. Run CGMP test suite inside Docker
echo "→ Running CGMP-L9 tests in Docker..."
cd /path/to/l9
docker compose run --rm test pytest tests/test_cgmp.py -v --strict-markers
if [ $? -ne 0 ]; then
    echo "❌ FAIL: CGMP tests did not pass."
    exit 1
fi

# 3. Quick dependency check
echo "→ Verifying locked dependencies..."
python -m pip freeze > /tmp/current-lock.txt
diff -u /tmp/expected-lock.txt /tmp/current-lock.txt || {
    echo "⚠️  WARNING: Dependency mismatch. Run 'pip install -r requirements.txt' and rebuild."
    exit 1
}

echo "✅ PASS: All pre-commit gates cleared. Proceeding with commit."
```

**Key principle**: Running tests **inside Docker containers built from the same Dockerfile** ensures that the test environment exactly matches production. No "works on my machine" surprises.

### 2.2 Environment Management: `.env.example` and Production Secrets

**Rule:** `.env.example` is the **canonical schema** for all environment variables. No hardcoded secrets ever committed.

```bash
# .env.example (committed to git)
# ============================================================================
# Python Runtime
# ============================================================================
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
ENV=production
LOG_LEVEL=INFO

# ============================================================================
# Database
# ============================================================================
# DSN format: postgresql://user:password@host:port/dbname
# WARNING: Password must be configured in .env (VPS only), never committed.
MEMORY_DSN=postgresql://postgres:YOUR_PASSWORD_HERE@127.0.0.1:5432/l9_memory

# ============================================================================
# LLM & Integrations
# ============================================================================
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
SLACK_BOT_TOKEN=xoxb-YOUR_TOKEN_HERE
SLACK_SIGNING_SECRET=YOUR_SECRET_HERE

# ... (all other keys documented similarly)
```

**On VPS:**
- `.env` file is **NOT committed**. It lives in `/opt/l9/.env` and is owned by root or a deploy user.
- Use **secrets management** (e.g., 1Password, Vault, or managed secrets) to rotate and audit changes.
- Deploy script validates `.env` keys against `.env.example` schema before launching containers.

**Local dev:**
- Copy `.env.example` to `.env.local` and fill in test/staging values.
- Never use production credentials locally.

### 2.3 Version Locking: Reproducible Builds

**Dockerfile must pin all critical versions:**

```dockerfile
FROM python:3.12-slim  # Pin to specific patch version (e.g., 3.12.7)

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Minimal OS packages; pin if possible
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl=7.88.1-13+deb12u5 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Use --no-cache every time to force fresh pull of latest patches
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "api.server_memory:app", "--host", "0.0.0.0", "--port", "8000"]
```

**requirements.txt must use exact versions:**

```
# Do NOT use >= or ~= in production
fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg[binary]==3.1.18
openai==1.3.9
slack-bolt==1.18.1
python-dotenv==1.0.0
# ... (all pinned exactly)
```

**Local rebuild after version changes:**

```bash
# Never skip --no-cache after changing dependency constraints
docker compose build --no-cache l9-api
# Then run full CGMP test suite in the new image
docker compose run --rm test pytest tests/ -v
```

---

## Part 3: Hardened Git Workflow for Deployability

### 3.1 Branching Model: Trunk + Short-Lived Feature Branches

**Principle**: One long-lived branch (`main`); all work happens on short-lived feature branches.

```
origin/main (trunk: always deployable, always clean)
    │
    ├─── feature/auth-refactor (local branch, push to origin)
    │        │
    │        └── [work, test, commit messages clear]
    │             │
    │             └─► [Create PR against main]
    │                  │
    │                  ├─ Code review (≥1 approver)
    │                  │
    │                  ├─ CI checks pass (CGMP on PR)
    │                  │
    │                  └─► [Merge to main via PR]
    │
    ├─── feature/memory-schema
    │        │
    │        └─► [same workflow]
    │
    └─► [Tag released version on main only]
```

**Constraints:**
- ✅ **Feature branches**: `feature/<short-desc>`, e.g., `feature/auth-refactor`, `feature/memory-schema`
- ✅ **Bugfix branches**: `bugfix/<issue-number>`, e.g., `bugfix/12345-deadlock`
- ✅ **Hotfix branches**: `hotfix/<issue-number>` (only for critical prod issues)
- ✅ **No direct commits to main**: Always via PR with code review
- ❌ **No long-lived branches**: Merge or delete within 1 week
- ❌ **Never commit to main without a PR**: Enforce via branch protection

### 3.2 Commit Hygiene: Clear, Atomic, Focused

Each commit should be independently reviewable and rollback-safe:

```bash
# ✅ GOOD: One concern per commit
git log --oneline main..feature/auth-refactor
abcdef1 Fix: Update JWT expiry check in auth.py
ghijkl2 Refactor: Extract verify_api_key into utils
mnopqr3 Test: Add unit tests for JWT edge cases

# ❌ BAD: Multiple concerns mixed
commit: "Fix auth, update deps, refactor memory routes, bump version"
```

**Commit message format:**

```
[TYPE]: Brief, imperative description (50 chars max)

Longer explanation (if needed):
- Why the change?
- What was broken before?
- How does this fix it?

References: #issue-number (if applicable)
```

Example:

```
Fix: Prevent deadlock in memory.insert_embedding

The previous implementation held a connection lock while
waiting for vector embedding completion, which caused
deadlocks under concurrent load.

This commit refactors to release the lock immediately after
queuing the async embedding task, then polls for completion
separately.

Fixes: #1042
```

### 3.3 Tagging Strategy: Semantic Versioning + Release Tags

**Tag format**: `v<major>.<minor>.<patch>-l9`

Examples:
- `v0.5.0-l9` (first production release)
- `v0.5.1-l9` (patch: minor bug fix)
- `v0.6.0-l9` (minor: new features, backward compatible)
- `v1.0.0-l9` (major: breaking changes)

**Versioning rules:**

| Increment | When | Examples |
|-----------|------|----------|
| **MAJOR** | Breaking API changes, major refactors, new kernel systems | `v0.x.x` → `v1.0.0` if agent API contract changes |
| **MINOR** | New features, new endpoints, new integrations (backward compatible) | `v0.5.x` → `v0.6.0` if adding `/memory/semantic/search` |
| **PATCH** | Bug fixes, performance tweaks, config changes (no new features) | `v0.5.0` → `v0.5.1` if fixing JWT expiry |

**Creating a release tag (locally):**

```bash
# Ensure main is up-to-date and clean
git checkout main
git pull origin main

# Verify tests pass locally
docker compose run --rm test pytest tests/ -v

# Create annotated tag (not lightweight)
git tag -a v0.5.1-l9 -m "Release v0.5.1-l9: Fix memory embedding deadlock

Fixes:
- Prevent lock contention in vector DB writes
- Add timeout guards to async operations

Testing:
- All CGMP tests pass locally
- 100% code coverage on changed files
- Manual smoke tests on /memory endpoints

Deployment: Blue-green with health checks.
Rollback: 'git checkout v0.5.0-l9' if needed."

# Push commits and tags to origin
git push origin main
git push origin v0.5.1-l9
```

**Viewing deployment history:**

```bash
# List all release tags
git tag -l 'v*-l9' | sort -V

# Show details of a specific tag
git show v0.5.1-l9

# View commits between two tags
git log v0.5.0-l9..v0.5.1-l9 --oneline
```

---

## Part 4: Deterministic Docker Images and Health Awareness

### 4.1 Dockerfile Constraints for Production

```dockerfile
FROM python:3.12-slim@sha256:abc123...  # Pinned by digest for absolute reproducibility

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Minimize OS layer: only essential packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl=7.88.1-13+deb12u5 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy locked dependencies
COPY requirements.txt pyproject.toml ./

# Upgrade pip, install deps without cache (force fresh fetch)
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Bake code into image (no runtime mounts)
COPY . /app

# Health check: Docker will use this to mark container healthy/unhealthy
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

EXPOSE 8000

# Explicit start command (no shell wrapping unless needed)
CMD ["uvicorn", "api.server_memory:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key principles:**
- ✅ **No `.:/app` mounts in production**: Code is baked in at build time.
- ✅ **Healthcheck included in image**: Docker daemon can auto-restart unhealthy containers.
- ✅ **Minimal base image**: `python:3.12-slim` is ~200MB vs `python:3.12` at ~900MB.
- ✅ **Pinned digest**: `@sha256:...` prevents even base image surprises.

### 4.2 `/health` Endpoint: Required Contract

Every L9 container must expose a `/health` endpoint that reports operational status:

```python
# api/server_memory.py

from fastapi import FastAPI
import psycopg
import os

app = FastAPI(title="L9 Phase 2 Secure AI OS")

@app.get("/health")
async def health():
    """
    Readiness and liveness probe for orchestration.
    Returns 200 with body only if all critical subsystems are operational.
    """
    try:
        # Check database connection
        dsn = os.getenv("MEMORY_DSN")
        with psycopg.connect(dsn, timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "L9 Phase 2 Memory System",
            "version": "0.5.1",
            "database": "connected",
            "memory_system": "operational",
        }
    except Exception as e:
        # Return 503 if any critical resource is down
        return {
            "status": "unhealthy",
            "error": str(e),
        }, 503
```

**Docker Compose integration:**

```yaml
services:
  l9-api:
    build:
      context: /opt/l9
      dockerfile: docker/Dockerfile
    container_name: l9-api
    restart: unless-stopped
    env_file: /opt/l9/.env
    network_mode: "host"
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s  # Grace period before first check
    
    stop_grace_period: 30s  # Allow graceful shutdown (SIGTERM)
    stop_signal: SIGTERM
```

**Observables:**

```bash
# Check container health status
docker inspect l9-api | jq '.[] | .State.Health'

# Output:
# {
#   "Status": "healthy",
#   "FailingStreak": 0,
#   "Logs": [...]
# }
```

### 4.3 Reproducibility: Build Once, Deploy Everywhere

**Local Build and Test:**

```bash
cd /opt/l9

# 1. Clean build (no cache) after dependency changes
docker compose build --no-cache l9-api

# 2. Run full test suite in the new image
docker compose run --rm test pytest tests/test_cgmp.py -v

# 3. Quick smoke test
docker compose up -d l9-api
sleep 5
curl -s http://127.0.0.1:8000/health | jq .

# 4. Tag the image locally if tests pass
docker tag l9-api:latest l9-api:v0.5.1-l9
```

**Push to registry (optional, for faster VPS deploys):**

```bash
# If using a registry (e.g., Docker Hub, GitHub Container Registry):
docker tag l9-api:v0.5.1-l9 your-registry.azurecr.io/l9-api:v0.5.1-l9
docker push your-registry.azurecr.io/l9-api:v0.5.1-l9

# Then on VPS, change docker-compose.yml to pull instead of build:
# image: your-registry.azurecr.io/l9-api:v0.5.1-l9
# instead of:
# build:
#   context: /opt/l9
#   dockerfile: docker/Dockerfile
```

**Tradeoff:** Building on VPS is slower but guarantees source-level reproducibility. Registry push is faster but requires managing credentials and attestation.

**Recommendation for L9**: Build locally, push to private registry, then pull on VPS. Encrypt registry credentials in `/opt/l9/.docker/config.json`.

---

## Part 5: VPS Rollout Protocol (The Deployment Runbook)

### 5.1 Standard Operating Procedure: Step-by-Step

**Prerequisites:**
- SSH access to VPS (user: `admin`, alias: `ssh l9`)
- Git and Docker installed on VPS
- PostgreSQL running and accessible
- Caddy service running
- `.env` file in `/opt/l9/` with production credentials

**Rollout Steps:**

#### Step 1: Verify and Fetch Tag on VPS

```bash
ssh l9

# On VPS:
cd /opt/l9

# Fetch latest commits and tags from origin
git fetch origin main
git fetch --tags origin

# Verify the tag exists and is valid
git tag -v v0.5.1-l9  # Should show tagger, date, signature
if [ $? -ne 0 ]; then
    echo "❌ FAIL: Tag v0.5.1-l9 not found or signature invalid."
    exit 1
fi

# Verify the tag is on main (not orphaned)
if ! git log origin/main | grep "$(git rev-list -n 1 v0.5.1-l9)"; then
    echo "❌ FAIL: Tag v0.5.1-l9 is not reachable from main."
    exit 1
fi

echo "✅ PASS: Tag v0.5.1-l9 verified and is on main."
```

#### Step 2: Checkout Tag

```bash
cd /opt/l9

# Checkout the exact commit tagged v0.5.1-l9
git checkout v0.5.1-l9

# Verify we're on the exact commit
git describe --tags
# Output: v0.5.1-l9

# Store the tag for later rollback reference
echo "v0.5.1-l9" > /tmp/l9-current-tag.txt
```

#### Step 3: Validate Environment and Dependencies

```bash
# Verify .env file exists and has required keys
if [ ! -f /opt/l9/.env ]; then
    echo "❌ FAIL: /opt/l9/.env not found."
    exit 1
fi

# Check that all keys from .env.example are present in .env
while IFS= read -r line; do
    key="${line%%=*}"
    if [ -z "$key" ] || [[ "$key" == \#* ]]; then continue; fi
    
    if ! grep -q "^$key=" /opt/l9/.env; then
        echo "⚠️  WARNING: Key $key from .env.example not found in .env"
    fi
done < /opt/l9/.env.example

echo "✅ Environment validation passed."
```

#### Step 4: Build or Pull Images

**Option A: Build locally on VPS (slower but verifiable)**

```bash
cd /opt/l9

# Clean build
docker compose build --no-cache l9-api

if [ $? -ne 0 ]; then
    echo "❌ FAIL: Docker build failed."
    exit 1
fi

echo "✅ Docker image built successfully."
```

**Option B: Pull from registry (faster)**

```bash
cd /opt/l9

# If using a registry, pull the exact image
docker compose pull l9-api

if [ $? -ne 0 ]; then
    echo "❌ FAIL: Docker pull failed."
    exit 1
fi

echo "✅ Docker image pulled successfully."
```

#### Step 5: Blue-Green Launch (Green Container)

For **zero-downtime deployment**, we use blue-green pattern:

```bash
cd /opt/l9/docker

# Current docker-compose.yml should define both blue and green services:
# services:
#   l9-api-blue:
#     container_name: l9-api-blue
#     ...
#   l9-api-green:
#     container_name: l9-api-green
#     restart: "no"  # Starts as inactive
#     ...

# Start the GREEN container (new version)
echo "→ Starting GREEN container with new image..."
docker compose up -d l9-api-green

# Wait for it to be healthy
echo "→ Waiting for GREEN to become healthy..."
TIMEOUT=60
ELAPSED=0
INTERVAL=5

while [ $ELAPSED -lt $TIMEOUT ]; do
    HEALTH=$(docker inspect l9-api-green | jq -r '.[0].State.Health.Status' 2>/dev/null)
    
    if [ "$HEALTH" = "healthy" ]; then
        echo "✅ GREEN container is healthy."
        break
    fi
    
    echo "  ... health check $((ELAPSED))s / ${TIMEOUT}s"
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ "$HEALTH" != "healthy" ]; then
    echo "❌ FAIL: GREEN container did not become healthy within ${TIMEOUT}s."
    docker logs l9-api-green --tail 50
    docker compose down l9-api-green
    exit 1
fi
```

#### Step 6: Smoke Tests

Before switching traffic, validate the new container can handle requests:

```bash
echo "→ Running smoke tests against GREEN..."

# Test 1: /health endpoint
HEALTH_RESP=$(curl -s -w "\n%{http_code}" http://127.0.0.1:8001/health)  # GREEN port
HTTP_CODE=$(echo "$HEALTH_RESP" | tail -1)

if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ FAIL: /health returned $HTTP_CODE, expected 200."
    docker logs l9-api-green --tail 50
    docker compose down l9-api-green
    exit 1
fi

echo "✅ /health endpoint OK"

# Test 2: Check logs for errors
if docker logs l9-api-green --tail 100 | grep -i "traceback\|error\|exception" | grep -v "DEBUG"; then
    echo "❌ FAIL: Errors found in container logs."
    docker logs l9-api-green --tail 100
    docker compose down l9-api-green
    exit 1
fi

echo "✅ Container logs clean (no Tracebacks)"

# Test 3: Optional API test (e.g., memory endpoint)
# MEMORY_TEST=$(curl -s -X POST \
#   -H "Authorization: Bearer ${L9_EXECUTOR_API_KEY}" \
#   http://127.0.0.1:8001/memory/packet \
#   -d '{"content":"test"}')
# 
# if ! echo "$MEMORY_TEST" | jq . > /dev/null 2>&1; then
#     echo "❌ FAIL: /memory/packet test failed."
#     exit 1
# fi
# echo "✅ Memory endpoint works"

echo "✅ All smoke tests passed. GREEN is ready for traffic."
```

#### Step 7: Route Traffic (Caddy Switch)

Switch Caddy (or your reverse proxy) to route traffic to the GREEN container:

```bash
echo "→ Routing traffic to GREEN container..."

# Option A: If using Caddy admin API (recommended for zero-downtime)
# Patch the upstream to point to GREEN:
CADDY_ADMIN="127.0.0.1:2019"

curl -s -X PATCH \
  -H "Content-Type: application/json" \
  -d '{
    "apps": {
      "http": {
        "servers": {
          "srv0": {
            "routes": [
              {
                "handle": [
                  {
                    "handler": "reverse_proxy",
                    "upstreams": [{"dial": "127.0.0.1:8001"}]
                  }
                ]
              }
            ]
          }
        }
      }
    }
  }' \
  "http://${CADDY_ADMIN}/config/apps/http" || {
    echo "❌ FAIL: Caddy admin API patch failed."
    exit 1
  }

echo "✅ Caddy now routes to GREEN (port 8001)."

# Option B: Manual Caddyfile edit + reload (has brief downtime)
# sed -i 's/127.0.0.1:8000/127.0.0.1:8001/' /etc/caddy/Caddyfile
# sudo systemctl reload caddy
```

#### Step 8: Drain and Shutdown BLUE

```bash
echo "→ Gracefully draining BLUE container..."

# BLUE will receive SIGTERM and have 30 seconds to finish requests
docker compose down l9-api-blue

# Wait for graceful shutdown (set by stop_grace_period in compose file)
sleep 5

# Verify it's down
if docker ps | grep -q l9-api-blue; then
    echo "⚠️  BLUE still running after grace period. Force-stopping..."
    docker stop l9-api-blue --time=5
    docker rm l9-api-blue || true
fi

echo "✅ BLUE container shut down cleanly."
```

#### Step 9: Rebuild BLUE with New Image

```bash
echo "→ Rebuilding BLUE container with new image..."

# Start BLUE with the new image (identical to GREEN now)
docker compose up -d l9-api-blue

# Wait for health
ELAPSED=0
TIMEOUT=60
while [ $ELAPSED -lt $TIMEOUT ]; do
    HEALTH=$(docker inspect l9-api-blue | jq -r '.[0].State.Health.Status' 2>/dev/null)
    if [ "$HEALTH" = "healthy" ]; then
        echo "✅ BLUE is healthy."
        break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
done

if [ "$HEALTH" != "healthy" ]; then
    echo "❌ FAIL: BLUE did not become healthy. Reverting to previous tag."
    # Fallback: see Rollback section below
    exit 1
fi
```

#### Step 10: Verify Traffic on BLUE, Cleanup

```bash
echo "→ Verifying traffic flows correctly to BLUE..."

# Quick test on BLUE port (8000)
curl -s http://127.0.0.1:8000/health | jq .

# Route Caddy back to BLUE (if not already)
curl -s -X PATCH \
  -H "Content-Type: application/json" \
  -d '{
    "apps": {
      "http": {
        "servers": {
          "srv0": {
            "routes": [
              {
                "handle": [
                  {
                    "handler": "reverse_proxy",
                    "upstreams": [{"dial": "127.0.0.1:8000"}]
                  }
                ]
              }
            ]
          }
        }
      }
    }
  }' \
  "http://127.0.0.1:2019/config/apps/http"

echo "✅ Traffic routed back to BLUE."

# Shutdown GREEN (or leave as standby)
docker compose down l9-api-green || true

# Clean up dangling images
docker image prune -af --filter "until=24h"

echo "✅ Cleanup complete."
```

#### Step 11: Record Deployment

```bash
# Store deployment metadata for audit trail
cat > /opt/l9/.deployed-metadata.json <<EOF
{
  "deployed_tag": "v0.5.1-l9",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "deployed_by": "$(whoami)@$(hostname)",
  "commit": "$(git rev-parse HEAD)",
  "status": "SUCCESS"
}
EOF

echo "✅ Deployment complete."
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Deployment Summary"
echo "═══════════════════════════════════════════════════════════════"
echo "Tag:     v0.5.1-l9"
echo "Status:  ✅ LIVE"
echo "URL:     https://l9.quantumaipartners.com/health"
echo "Time:    $(date)"
echo ""
echo "If issues arise, rollback with:"
echo "  /opt/l9/scripts/rollback.sh v0.5.0-l9"
echo "═══════════════════════════════════════════════════════════════"
```

### 5.2 Rollback Protocol: Tag-Based Instant Recovery

**Rollback is a first-class operation**, not an afterthought. The procedure mirrors deployment but targets the previous known-good tag:

```bash
#!/usr/bin/env bash
# scripts/rollback.sh v0.5.0-l9

set -e

PREVIOUS_TAG="${1:-}"
if [ -z "$PREVIOUS_TAG" ]; then
    echo "Usage: $0 <previous-tag>"
    echo "Example: $0 v0.5.0-l9"
    exit 1
fi

cd /opt/l9

echo "🔄 Rolling back to tag: $PREVIOUS_TAG"

# 1. Verify tag exists
if ! git tag -v "$PREVIOUS_TAG" > /dev/null 2>&1; then
    echo "❌ FAIL: Tag $PREVIOUS_TAG not found."
    exit 1
fi

echo "✅ Tag verified."

# 2. Checkout previous tag
git checkout "$PREVIOUS_TAG"
echo "✅ Checked out $PREVIOUS_TAG"

# 3. Rebuild/pull image (same as deployment)
docker compose build --no-cache l9-api 2>&1 | tail -5
echo "✅ Image built/pulled."

# 4. Blue-green rollback (same as deployment, but simpler: no GREEN overhead)
docker compose down l9-api || true
docker compose up -d l9-api

# 5. Wait for health
ELAPSED=0
TIMEOUT=60
while [ $ELAPSED -lt $TIMEOUT ]; do
    HEALTH=$(docker inspect l9-api | jq -r '.[0].State.Health.Status' 2>/dev/null)
    if [ "$HEALTH" = "healthy" ]; then
        echo "✅ Container healthy after rollback."
        break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
done

if [ "$HEALTH" != "healthy" ]; then
    echo "❌ FAIL: Rollback did not succeed. Manual intervention required."
    exit 1
fi

# 6. Smoke test
if ! curl -s http://127.0.0.1:8000/health | jq . > /dev/null; then
    echo "❌ FAIL: Health check failed after rollback."
    exit 1
fi

echo "✅ Smoke test passed."

# 7. Record rollback
cat > /opt/l9/.deployed-metadata.json <<EOF
{
  "deployed_tag": "$PREVIOUS_TAG",
  "rolled_back_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "rolled_back_by": "$(whoami)",
  "reason": "manual",
  "status": "ROLLED_BACK"
}
EOF

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ ROLLBACK SUCCESSFUL"
echo "═══════════════════════════════════════════════════════════════"
echo "Tag:     $PREVIOUS_TAG"
echo "Status:  LIVE"
echo "Time:    $(date)"
echo "Next:    Review logs and previous deployment for root cause."
echo "═══════════════════════════════════════════════════════════════"
```

**Rollback is nearly instant:**
- Tag already in git (no network fetch needed)
- Image either cached locally or pulled from registry
- Container starts and healthchecks within 30s
- Total time: < 2 minutes

### 5.3 Drift Detection and Reconciliation

**Periodic audit: Is the running system exactly what's in git?**

```bash
#!/usr/bin/env bash
# scripts/drift-check.sh (run hourly via cron)

set -e
cd /opt/l9

# 1. Git status clean?
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  DRIFT DETECTED: Uncommitted changes in /opt/l9"
    echo "$(git status --porcelain)"
    exit 1
fi

# 2. Running container matches deployed tag?
DEPLOYED_TAG=$(cat /opt/l9/.deployed-metadata.json | jq -r .deployed_tag)
RUNNING_COMMIT=$(git rev-parse HEAD)
DEPLOYED_COMMIT=$(git rev-parse "$DEPLOYED_TAG")

if [ "$RUNNING_COMMIT" != "$DEPLOYED_COMMIT" ]; then
    echo "⚠️  DRIFT DETECTED: Running commit != deployed tag"
    echo "  Running:   $RUNNING_COMMIT"
    echo "  Deployed:  $DEPLOYED_TAG ($DEPLOYED_COMMIT)"
    exit 1
fi

# 3. Image hash matches?
# (Optional: if using registry, verify image digest)

echo "✅ PASS: No drift detected. Running system matches git."
```

**Add to crontab:**

```bash
# /etc/cron.d/l9-health-checks
0 * * * * /opt/l9/scripts/drift-check.sh >> /var/log/l9-drift-check.log 2>&1
```

---

## Part 6: Autonomous One-Command Deploy Script

The following script encodes the entire pipeline as a single, deterministic transaction. It can be run locally or integrated into CI/CD:

### 6.1 Script Specification: `deploy.sh`

```bash
#!/usr/bin/env bash
# scripts/deploy.sh
# USAGE: ./scripts/deploy.sh <version-tag>
# 
# This script orchestrates a complete, safe, reversible deployment from
# local workspace → git → VPS production in a single transaction.
#
# All-or-nothing semantics: either fully deployed and healthy, or fully
# rolled back to previous state.

set -euo pipefail

# ═════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═════════════════════════════════════════════════════════════════════════════

VERSION_TAG="${1:-}"
VPS_HOST="157.180.73.53"
VPS_USER="admin"
VPS_PATH="/opt/l9"
VPS_SSH="${VPS_USER}@${VPS_HOST}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ═════════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

fail() {
    log_error "$*"
    exit 1
}

# Print usage
usage() {
    cat <<EOF
Usage: $0 <version-tag>

Deploy a tagged release to production VPS with automatic rollback on failure.

Arguments:
  <version-tag>    Git tag to deploy (e.g., v0.5.1-l9)

Environment Variables (optional):
  VPS_HOST         VPS IP address (default: ${VPS_HOST})
  VPS_USER         SSH user (default: ${VPS_USER})
  VPS_PATH         App path on VPS (default: ${VPS_PATH})
  L9_EXECUTOR_API_KEY  For smoke tests (if defined)

Examples:
  $0 v0.5.1-l9
  VPS_HOST=1.2.3.4 $0 v0.5.1-l9

EOF
    exit 1
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 1: LOCAL VALIDATION
# ═════════════════════════════════════════════════════════════════════════════

phase_local_validation() {
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "PHASE 1: LOCAL VALIDATION"
    log_info "═══════════════════════════════════════════════════════════════"
    
    cd "$REPO_ROOT"
    
    # Check version tag format
    if ! [[ "$VERSION_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+-l9$ ]]; then
        fail "Invalid version tag format: $VERSION_TAG (expected: vX.Y.Z-l9)"
    fi
    log_info "✅ Version tag format valid: $VERSION_TAG"
    
    # Git status clean
    if [ -n "$(git status --porcelain | grep -v '^??')" ]; then
        fail "Uncommitted changes detected. Please commit all changes first."
    fi
    log_info "✅ Git status clean"
    
    # Check that tag exists locally
    if ! git rev-parse "$VERSION_TAG" > /dev/null 2>&1; then
        fail "Tag $VERSION_TAG not found locally. Create it with: git tag -a $VERSION_TAG -m '...'"
    fi
    log_info "✅ Tag exists locally: $VERSION_TAG"
    
    # Run CGMP tests locally
    log_info "→ Running CGMP tests locally..."
    docker compose run --rm test pytest tests/test_cgmp.py -v --tb=short || \
        fail "CGMP tests failed locally. Fix issues before deploying."
    log_info "✅ CGMP tests passed"
    
    # Quick Docker build test
    log_info "→ Building Docker image locally..."
    docker compose build --no-cache l9-api > /tmp/docker-build.log 2>&1 || {
        log_error "Docker build failed. See /tmp/docker-build.log"
        fail "Local Docker build failed"
    }
    log_info "✅ Docker image built successfully"
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2: GIT PUSH
# ═════════════════════════════════════════════════════════════════════════════

phase_git_push() {
    log_info ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "PHASE 2: GIT PUSH (commits + tags)"
    log_info "═══════════════════════════════════════════════════════════════"
    
    cd "$REPO_ROOT"
    
    # Ensure we're on main
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        fail "Not on main branch (current: $CURRENT_BRANCH). Check out main first."
    fi
    log_info "✅ On main branch"
    
    # Fetch and verify tag is on main
    git fetch origin main > /dev/null 2>&1 || log_warn "Could not fetch from origin"
    if ! git log origin/main | grep -q "$(git rev-parse $VERSION_TAG)"; then
        fail "Tag $VERSION_TAG is not reachable from origin/main. This tag may be local-only or on a different branch."
    fi
    log_info "✅ Tag is on origin/main"
    
    # Push commits
    log_info "→ Pushing commits to origin/main..."
    git push origin main || fail "Failed to push commits to origin"
    log_info "✅ Commits pushed"
    
    # Push tags
    log_info "→ Pushing tags to origin..."
    git push origin "$VERSION_TAG" || fail "Failed to push tag $VERSION_TAG"
    log_info "✅ Tag pushed: $VERSION_TAG"
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 3: VPS DEPLOYMENT
# ═════════════════════════════════════════════════════════════════════════════

phase_vps_deployment() {
    log_info ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "PHASE 3: VPS DEPLOYMENT"
    log_info "═══════════════════════════════════════════════════════════════"
    
    # Save current tag on VPS before deploying (for rollback)
    PREVIOUS_TAG=$(ssh "$VPS_SSH" \
        "cat ${VPS_PATH}/.deployed-metadata.json 2>/dev/null | jq -r .deployed_tag // 'unknown'" \
        || echo "unknown")
    
    log_info "Current VPS tag: $PREVIOUS_TAG"
    log_info "Deploying tag:   $VERSION_TAG"
    
    # Deploy via SSH
    log_info "→ Executing deployment script on VPS..."
    
    DEPLOY_SCRIPT=$(cat <<'DEPLOY_EOF'
#!/usr/bin/env bash
set -euo pipefail

VERSION_TAG="$1"
VPS_PATH="$2"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[VPS]${NC} $*"; }
log_error() { echo -e "${RED}[VPS]${NC} $*" >&2; }

cd "$VPS_PATH"

# 1. Fetch and verify tag
log_info "Fetching and verifying tag..."
git fetch origin main > /dev/null 2>&1
git fetch --tags origin > /dev/null 2>&1

if ! git tag -v "$VERSION_TAG" > /dev/null 2>&1; then
    log_error "Tag $VERSION_TAG not found or signature invalid."
    exit 1
fi
log_info "✅ Tag verified."

# 2. Checkout
log_info "Checking out $VERSION_TAG..."
git checkout "$VERSION_TAG" > /dev/null 2>&1
log_info "✅ Checked out."

# 3. Validate .env
log_info "Validating .env..."
if [ ! -f "${VPS_PATH}/.env" ]; then
    log_error ".env not found."
    exit 1
fi
log_info "✅ .env exists."

# 4. Build/pull image
log_info "Building/pulling Docker image..."
cd "${VPS_PATH}/docker"
docker compose build --no-cache l9-api > /tmp/docker-compose-build.log 2>&1 || {
    log_error "Docker build failed. See /tmp/docker-compose-build.log"
    exit 1
}
log_info "✅ Image ready."

# 5. Start new container
log_info "Starting new container..."
docker compose up -d l9-api

# 6. Wait for health
log_info "Waiting for container to become healthy..."
ELAPSED=0
TIMEOUT=60
INTERVAL=5

while [ $ELAPSED -lt $TIMEOUT ]; do
    HEALTH=$(docker inspect l9-api 2>/dev/null | jq -r '.[0].State.Health.Status' 2>/dev/null || echo "starting")
    
    if [ "$HEALTH" = "healthy" ]; then
        log_info "✅ Container is healthy."
        break
    fi
    
    echo -n "."
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ "$HEALTH" != "healthy" ]; then
    log_error "Container did not become healthy within ${TIMEOUT}s."
    docker logs l9-api --tail 50
    exit 1
fi

# 7. Smoke tests
log_info "Running smoke tests..."
HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health)

if [ "$HEALTH_CODE" != "200" ]; then
    log_error "/health returned $HEALTH_CODE, expected 200."
    docker logs l9-api --tail 50
    exit 1
fi
log_info "✅ /health endpoint OK"

# Check logs
if docker logs l9-api --tail 100 | grep -i "traceback" 2>/dev/null; then
    log_error "Tracebacks found in logs."
    docker logs l9-api --tail 100 | grep -i traceback
    exit 1
fi
log_info "✅ Logs clean"

# 8. Record deployment
mkdir -p "$VPS_PATH"
cat > "${VPS_PATH}/.deployed-metadata.json" <<METADATA
{
  "deployed_tag": "$VERSION_TAG",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "deployed_by": "$(whoami)",
  "commit": "$(git rev-parse HEAD)",
  "status": "SUCCESS"
}
METADATA

log_info "✅ Deployment successful. Tag: $VERSION_TAG"

DEPLOY_EOF
)
    
    # Execute on VPS
    ssh "$VPS_SSH" bash -s "$VERSION_TAG" "$VPS_PATH" <<< "$DEPLOY_SCRIPT" || {
        log_error "VPS deployment failed. Attempting rollback..."
        phase_rollback "$PREVIOUS_TAG"
        fail "Deployment failed and was rolled back."
    }
    
    log_info "✅ VPS deployment successful"
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 4: VERIFICATION
# ═════════════════════════════════════════════════════════════════════════════

phase_verification() {
    log_info ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "PHASE 4: POST-DEPLOYMENT VERIFICATION"
    log_info "═══════════════════════════════════════════════════════════════"
    
    # Test external endpoint
    log_info "→ Testing external endpoint..."
    EXTERNAL_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://l9.quantumaipartners.com/health || echo "000")
    
    if [ "$EXTERNAL_CODE" = "200" ]; then
        log_info "✅ External endpoint responding: https://l9.quantumaipartners.com/health"
    else
        log_warn "External endpoint returned $EXTERNAL_CODE. Check Caddy/DNS if unexpected."
    fi
    
    log_info "✅ Verification complete"
}

# ═════════════════════════════════════════════════════════════════════════════
# ROLLBACK (emergency only)
# ═════════════════════════════════════════════════════════════════════════════

phase_rollback() {
    local ROLLBACK_TAG="${1:-}"
    
    if [ -z "$ROLLBACK_TAG" ]; then
        log_error "No previous tag available for rollback."
        return 1
    fi
    
    log_warn "ROLLING BACK to $ROLLBACK_TAG..."
    
    ssh "$VPS_SSH" bash -s "$ROLLBACK_TAG" <<'ROLLBACK_EOF'
#!/usr/bin/env bash
set -euo pipefail
TAG="$1"
cd /opt/l9
git checkout "$TAG" > /dev/null 2>&1
cd /opt/l9/docker
docker compose build --no-cache l9-api > /dev/null 2>&1
docker compose down l9-api || true
docker compose up -d l9-api
sleep 10
curl -s http://127.0.0.1:8000/health > /dev/null 2>&1 && echo "Rollback successful" || echo "Rollback check failed"
ROLLBACK_EOF
}

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

main() {
    if [ -z "$VERSION_TAG" ]; then
        usage
    fi
    
    log_info "L9 Autonomous Deployment Pipeline"
    log_info "Version: $VERSION_TAG"
    log_info ""
    
    phase_local_validation
    phase_git_push
    phase_vps_deployment
    phase_verification
    
    log_info ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "✅ DEPLOYMENT SUCCESSFUL"
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "Tag:      $VERSION_TAG"
    log_info "Status:   LIVE"
    log_info "URL:      https://l9.quantumaipartners.com/health"
    log_info "Time:     $(date)"
    log_info ""
    log_info "If issues arise, rollback with:"
    log_info "  ssh $VPS_SSH"
    log_info "  /opt/l9/scripts/rollback.sh v0.5.0-l9"
    log_info "═══════════════════════════════════════════════════════════════"
}

main
```

### 6.2 Usage Examples

```bash
# Create and tag a new release
git tag -a v0.5.1-l9 -m "Release v0.5.1-l9: Fix memory deadlock"

# Deploy with one command
./scripts/deploy.sh v0.5.1-l9

# Output:
# [INFO] L9 Autonomous Deployment Pipeline
# [INFO] Version: v0.5.1-l9
# [INFO] ═══════════════════════════════════════════════════════════════
# [INFO] PHASE 1: LOCAL VALIDATION
# [INFO] ═══════════════════════════════════════════════════════════════
# [INFO] ✅ Version tag format valid: v0.5.1-l9
# [INFO] ✅ Git status clean
# ...
# [INFO] ✅ DEPLOYMENT SUCCESSFUL
# [INFO] Tag:      v0.5.1-l9
# [INFO] Status:   LIVE
```

---

## Part 7: Future Extensions: CI/CD and GitOps Integration

### 7.1 GitHub Actions Workflow (Optional)

Once the deploy script is proven, integrate it with GitHub Actions for automatic CI on every tag:

```yaml
# .github/workflows/deploy.yml

name: Deploy L9

on:
  push:
    tags:
      - 'v*-l9'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for git operations
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Run CGMP tests
        run: |
          docker compose run --rm test pytest tests/test_cgmp.py -v
      
      - name: Build Docker image
        run: |
          docker compose build --no-cache l9-api
      
      - name: Deploy to VPS
        env:
          VPS_HOST: ${{ secrets.VPS_HOST }}
          VPS_USER: ${{ secrets.VPS_USER }}
          VPS_KEY: ${{ secrets.VPS_SSH_KEY }}
          VPS_PATH: /opt/l9
        run: |
          mkdir -p ~/.ssh
          echo "$VPS_KEY" > ~/.ssh/id_ed25519
          chmod 600 ~/.ssh/id_ed25519
          ssh-keyscan -H "$VPS_HOST" >> ~/.ssh/known_hosts
          
          ./scripts/deploy.sh ${GITHUB_REF#refs/tags/}
      
      - name: Notify Slack on success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: "✅ L9 deployment successful: ${{ github.ref }}"
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
      
      - name: Notify Slack on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: "❌ L9 deployment failed: ${{ github.ref }}"
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 7.2 Argocd/Flux for GitOps (Future)

For larger rollouts, consider adopting ArgoCD or Flux:

```yaml
# argocd/l9-app.yaml (future GitOps manifest)

apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: l9
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/l9
    targetRevision: HEAD  # Always follow main
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: l9-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

---

## Part 8: Summary and Checklist

### 8.1 Deployment Invariants (Quick Reference)

| Substrate | Invariant | Check |
|-----------|-----------|-------|
| **LOCAL** | CGMP passes in Docker | `docker compose run test pytest -v` |
| **LOCAL** | Deps locked | `grep "==" requirements.txt` |
| **LOCAL** | Git status clean | `git status --porcelain` |
| **GIT** | Only tagged commits deployed | `git tag -v <tag>` |
| **GIT** | Tag on main | `git log origin/main \| grep <tag>` |
| **VPS** | Container healthy | `docker inspect l9-api \| jq .State.Health` |
| **VPS** | /health returns 200 | `curl http://127.0.0.1:8000/health` |
| **VPS** | No Tracebacks in logs | `docker logs l9-api --tail 100 \| grep -i traceback` |
| **VPS** | Drift-free | `git status --porcelain` on VPS is empty |

### 8.2 Implementation Checklist

- [ ] **Local policy**
  - [ ] Pre-commit hook runs CGMP tests
  - [ ] `.env.example` documents all prod vars
  - [ ] `requirements.txt` uses exact versions
  - [ ] Dockerfile pins base image and OS packages

- [ ] **Git workflow**
  - [ ] `main` branch is protected (no direct commits)
  - [ ] Feature branches use naming convention
  - [ ] Tagging script and docs available
  - [ ] `.deployed-tag` file tracked locally

- [ ] **Docker/VPS**
  - [ ] `/health` endpoint implemented in FastAPI
  - [ ] `docker-compose.yml` includes `healthcheck` section
  - [ ] Blue-green or dual services available
  - [ ] Rollback script tested and documented

- [ ] **Deployment**
  - [ ] `deploy.sh` written and tested
  - [ ] Pre-flight checks (git, Docker, env)
  - [ ] Smoke tests after deployment
  - [ ] Metadata recorded (`/.deployed-metadata.json`)

- [ ] **Monitoring**
  - [ ] `drift-check.sh` runs hourly via cron
  - [ ] Logs aggregated or accessible via `docker logs`
  - [ ] Slack/email alerts on deployment failure

---

## Part 9: Production Readiness Criteria

Before deploying to production, ensure:

1. ✅ **Code**: CGMP tests pass locally inside Docker.
2. ✅ **Dependencies**: All pinned to exact versions. No `latest` or floating constraints.
3. ✅ **Git**: Tag created, signed (optional), and on main.
4. ✅ **VPS Infra**: PostgreSQL running, Caddy configured, `.env` in place.
5. ✅ **Health**: `/health` endpoint returns 200 and meaningful status.
6. ✅ **Observability**: Logs accessible and clean (no Tracebacks).
7. ✅ **Smoke Tests**: API responds to POST/GET; memory operations succeed.
8. ✅ **Rollback Plan**: Previous stable tag identified and tested locally.

---

## Part 10: Conclusion

This specification codifies a **deterministic, auditable, and reversible deployment pipeline** for L9. The key principles are:

1. **Local is Source of Truth**: CGMP tests + locked deps ensure reproducibility.
2. **Git is Immutable Record**: Annotated tags + commit history = audit trail.
3. **VPS is Observable**: Health checks + smoke tests + drift detection = safety.
4. **Rollback is Instant**: Tag-based recovery means minutes, not hours.
5. **Automation is Enforced**: Pre-commit hooks, branch protection, and deploy scripts encode the process.

With this pipeline in place, deployments become **low-friction and high-confidence**: push a tag, run `deploy.sh`, and the system handles the rest—with automatic rollback on failure.

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-21  
**Status**: Ready for implementation and integration testing.

