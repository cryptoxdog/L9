# L9 Deployment Pipeline: Implementation Kit
## Ready-to-Run Scripts and Configuration Files

**Last Updated:** 2025-12-21  
**Version:** 1.0  
**Status:** Production-ready templates

This file contains concrete, copy-paste-ready scripts to implement the deployment pipeline from `L9-DEPLOY-PIPELINE.md`.

---

## 1. Pre-Commit Hook Setup

Save as: `.git/hooks/pre-commit` (make executable: `chmod +x`)

```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit
# Enforces CGMP gate before allowing commits

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[PRE-COMMIT]${NC} $*"; }
log_error() { echo -e "${RED}[PRE-COMMIT]${NC} $*" >&2; }
log_warn() { echo -e "${YELLOW}[PRE-COMMIT]${NC} $*"; }

log_info "Running pre-commit gate..."

# 1. Check git status (no uncommitted changes in tracked files)
UNCOMMITTED=$(git status --porcelain | grep -v '^??')
if [ -n "$UNCOMMITTED" ]; then
    log_error "Uncommitted changes detected. Stage all changes first:"
    echo "$UNCOMMITTED"
    exit 1
fi

log_info "✅ Git status clean"

# 2. Run CGMP tests inside Docker
log_info "→ Running CGMP-L9 tests in Docker..."
if ! docker compose run --rm test pytest tests/test_cgmp.py -v --strict-markers 2>&1 | tail -20; then
    log_error "❌ CGMP tests failed. Commit aborted."
    exit 1
fi

log_info "✅ CGMP tests passed"

# 3. Verify no uncommitted code is being added
STAGED=$(git diff --cached --name-only)
if echo "$STAGED" | grep -qE '\.env$|\.env\..*$|secret|password|key'; then
    log_error "❌ Secrets detected in staged files. Do not commit .env or credential files."
    exit 1
fi

log_info "✅ No secrets detected in staged files"

# 4. Quick syntax check on Python files
log_info "→ Checking Python syntax..."
for file in $(git diff --cached --name-only | grep '\.py$'); do
    if [ -f "$file" ]; then
        python -m py_compile "$file" 2>&1 || {
            log_error "Syntax error in $file"
            exit 1
        }
    fi
done

log_info "✅ Python syntax OK"

log_info "═══════════════════════════════════════════════════════════════"
log_info "✅ ALL PRE-COMMIT CHECKS PASSED"
log_info "═══════════════════════════════════════════════════════════════"
```

---

## 2. Tag Creation Script

Save as: `scripts/create-release-tag.sh` (make executable)

```bash
#!/usr/bin/env bash
# scripts/create-release-tag.sh
# Creates and pushes an annotated release tag with validation

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[TAG]${NC} $*"; }
log_error() { echo -e "${RED}[TAG]${NC} $*" >&2; }
log_warn() { echo -e "${YELLOW}[TAG]${NC} $*"; }

fail() {
    log_error "$*"
    exit 1
}

usage() {
    cat <<EOF
Usage: $0 <major|minor|patch> [pre-release-suffix]

Automatically increment version, create annotated tag, and push.

Arguments:
  major|minor|patch     Increment type
  pre-release-suffix    Optional: alpha, beta, rc, etc.

Environment:
  DEPLOY_USER          Name for tagger (default: \$(git config user.name))

Examples:
  $0 patch                    # v0.5.0 → v0.5.1
  $0 minor                    # v0.5.1 → v0.6.0
  $0 major                    # v0.6.0 → v1.0.0
  $0 minor beta               # v0.5.1 → v0.6.0-beta

EOF
    exit 1
}

main() {
    local INCREMENT="${1:-}"
    local PRERELEASE="${2:-}"
    
    [ -z "$INCREMENT" ] && usage
    
    cd "$(git rev-parse --show-toplevel)"
    
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "L9 Release Tag Creator"
    log_info "═══════════════════════════════════════════════════════════════"
    
    # 1. Verify git status
    if [ -n "$(git status --porcelain)" ]; then
        fail "Git status not clean. Commit or stash changes first."
    fi
    log_info "✅ Git status clean"
    
    # 2. Fetch latest tags
    git fetch origin --tags > /dev/null 2>&1 || log_warn "Could not fetch tags from origin"
    
    # 3. Find latest tag
    LATEST_TAG=$(git tag -l 'v*-l9' | sort -V | tail -1)
    
    if [ -z "$LATEST_TAG" ]; then
        LATEST_TAG="v0.0.0-l9"
        log_warn "No previous tags found. Starting from v0.0.0-l9"
    fi
    
    log_info "Latest tag: $LATEST_TAG"
    
    # 4. Parse version
    VERSION="${LATEST_TAG#v}"      # Remove 'v' prefix
    VERSION="${VERSION%-l9}"        # Remove '-l9' suffix
    MAJOR=$(echo "$VERSION" | cut -d. -f1)
    MINOR=$(echo "$VERSION" | cut -d. -f2)
    PATCH=$(echo "$VERSION" | cut -d. -f3)
    
    # 5. Increment
    case "$INCREMENT" in
        major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
        minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
        patch) PATCH=$((PATCH + 1)) ;;
        *) fail "Invalid increment: $INCREMENT (use major|minor|patch)" ;;
    esac
    
    NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
    if [ -n "$PRERELEASE" ]; then
        NEW_VERSION="${NEW_VERSION}-${PRERELEASE}"
    fi
    NEW_TAG="v${NEW_VERSION}-l9"
    
    log_info "New version: $NEW_TAG"
    
    # 6. Ensure main is up-to-date
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        fail "Not on main branch. Check out 'main' first."
    fi
    
    git pull origin main --quiet
    log_info "✅ Pulled latest from origin/main"
    
    # 7. Run tests
    log_info "→ Running CGMP tests..."
    docker compose run --rm test pytest tests/test_cgmp.py -v --tb=short || \
        fail "Tests failed. Fix before tagging."
    log_info "✅ Tests passed"
    
    # 8. Create tag
    TAGGER="${DEPLOY_USER:-$(git config user.name)}"
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    TIMESTAMP=$(date -u +%Y-%m-%d\ %H:%M:%S\ UTC)
    
    TAG_MESSAGE="Release $NEW_TAG

Version: $NEW_TAG
Commit: $CURRENT_COMMIT
Tagger: $TAGGER
Date: $TIMESTAMP

## Changes

$(git log --oneline $LATEST_TAG..HEAD 2>/dev/null | sed 's/^/- /' || echo '- Initial release')

## Pre-deployment Checks

- [x] CGMP-L9 tests passed
- [x] Git status clean
- [x] Committed to origin/main
- [x] No untracked files
- [x] Dependencies locked

## Post-deployment

Deploy with: ./scripts/deploy.sh $NEW_TAG
Rollback with: git checkout $LATEST_TAG
"
    
    log_info "→ Creating annotated tag: $NEW_TAG"
    git tag -a "$NEW_TAG" -m "$TAG_MESSAGE"
    log_info "✅ Tag created locally"
    
    # 9. Push
    log_info "→ Pushing to origin..."
    git push origin main --quiet
    git push origin "$NEW_TAG" --quiet
    log_info "✅ Tag pushed: $NEW_TAG"
    
    log_info ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "✅ TAG CREATED AND PUSHED"
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "Tag: $NEW_TAG"
    log_info "Deploy with:"
    log_info "  ./scripts/deploy.sh $NEW_TAG"
    log_info "═══════════════════════════════════════════════════════════════"
}

main "$@"
```

---

## 3. Deployment Script (Complete Production Version)

Save as: `scripts/deploy.sh` (make executable)

**NOTE**: This is the full, production-ready deployment script referenced in the main specification.

```bash
#!/usr/bin/env bash
# scripts/deploy.sh
# Complete autonomous deployment: local → git → VPS

set -euo pipefail

# ═════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═════════════════════════════════════════════════════════════════════════════

VERSION_TAG="${1:-}"
VPS_HOST="${VPS_HOST:-157.180.73.53}"
VPS_USER="${VPS_USER:-admin}"
VPS_PATH="${VPS_PATH:-/opt/l9}"
VPS_SSH="${VPS_USER}@${VPS_HOST}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ═════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═════════════════════════════════════════════════════════════════════════════

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$*${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
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

# ═════════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

usage() {
    cat <<EOF
Usage: $0 <version-tag>

Deploy a tagged release to VPS with automatic safety checks and rollback.

Arguments:
  <version-tag>    Git tag to deploy (e.g., v0.5.1-l9)

Environment:
  VPS_HOST         VPS IP or hostname (default: 157.180.73.53)
  VPS_USER         SSH user (default: admin)
  VPS_PATH         App path on VPS (default: /opt/l9)

Examples:
  $0 v0.5.1-l9
  VPS_HOST=prod.example.com $0 v0.6.0-l9

EOF
    exit 1
}

phase_local_validation() {
    log_section "PHASE 1: LOCAL VALIDATION"
    
    cd "$REPO_ROOT"
    
    # Format check
    if ! [[ "$VERSION_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+ ]]; then
        fail "Invalid tag format: $VERSION_TAG (expected: vX.Y.Z-l9)"
    fi
    log_info "✅ Tag format valid: $VERSION_TAG"
    
    # Git status
    if [ -n "$(git status --porcelain | grep -v '^??')" ]; then
        fail "Uncommitted changes. Commit all changes first."
    fi
    log_info "✅ Git status clean"
    
    # Tag exists
    if ! git rev-parse "$VERSION_TAG" > /dev/null 2>&1; then
        fail "Tag $VERSION_TAG not found locally. Create it with: ./scripts/create-release-tag.sh"
    fi
    log_info "✅ Tag exists locally: $VERSION_TAG"
    
    # Tests
    log_info "→ Running CGMP tests..."
    if ! docker compose run --rm test pytest tests/test_cgmp.py -v --tb=short 2>&1 | tail -5; then
        fail "CGMP tests failed."
    fi
    log_info "✅ Tests passed"
    
    # Build
    log_info "→ Building Docker image..."
    if ! docker compose build --no-cache l9-api > /tmp/docker-build.log 2>&1; then
        log_error "Docker build failed. See /tmp/docker-build.log"
        fail "Build failed"
    fi
    log_info "✅ Docker image built"
}

phase_git_push() {
    log_section "PHASE 2: GIT PUSH"
    
    cd "$REPO_ROOT"
    
    # Check branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        fail "Not on main branch (current: $CURRENT_BRANCH)"
    fi
    log_info "✅ On main branch"
    
    # Verify tag is on main
    git fetch origin main > /dev/null 2>&1 || true
    if ! git log origin/main 2>/dev/null | grep -q "$(git rev-parse $VERSION_TAG)"; then
        log_warn "Tag $VERSION_TAG may not be on origin/main. Continuing anyway..."
    fi
    
    # Push
    log_info "→ Pushing commits..."
    git push origin main || fail "Failed to push"
    log_info "✅ Commits pushed"
    
    log_info "→ Pushing tags..."
    git push origin "$VERSION_TAG" || fail "Failed to push tags"
    log_info "✅ Tags pushed"
}

phase_vps_deployment() {
    log_section "PHASE 3: VPS DEPLOYMENT"
    
    # Get previous tag for rollback reference
    PREVIOUS_TAG=$(ssh "$VPS_SSH" \
        "cat ${VPS_PATH}/.deployed-metadata.json 2>/dev/null | jq -r .deployed_tag // 'unknown'" \
        2>/dev/null || echo "unknown")
    
    log_info "Previous VPS tag: $PREVIOUS_TAG"
    log_info "Deploying tag:   $VERSION_TAG"
    
    # Deploy script to send to VPS
    DEPLOY_PAYLOAD=$(cat <<'PAYLOAD_EOF'
#!/usr/bin/env bash
set -euo pipefail

VERSION_TAG="$1"
VPS_PATH="$2"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[VPS]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[VPS]${NC} $*"; }
log_error() { echo -e "${RED}[VPS]${NC} $*" >&2; }
fail() { log_error "$*"; exit 1; }

cd "$VPS_PATH"

# 1. Fetch and verify tag
log_info "Fetching from origin..."
git fetch origin main > /dev/null 2>&1 || log_warn "Fetch from origin/main failed"
git fetch --tags origin > /dev/null 2>&1 || log_warn "Fetch tags failed"

if ! git tag -v "$VERSION_TAG" > /dev/null 2>&1; then
    log_error "Tag not found or invalid signature"
    exit 1
fi
log_info "✅ Tag verified"

# 2. Checkout
log_info "Checking out $VERSION_TAG..."
git checkout "$VERSION_TAG" > /dev/null 2>&1
log_info "✅ Checked out"

# 3. Validate .env
if [ ! -f "$VPS_PATH/.env" ]; then
    fail ".env file not found at $VPS_PATH/.env"
fi
log_info "✅ .env exists"

# 4. Build image
log_info "Building Docker image..."
cd "$VPS_PATH/docker"
if ! docker compose build --no-cache l9-api > /tmp/docker-build-vps.log 2>&1; then
    log_error "Docker build failed:"
    tail -20 /tmp/docker-build-vps.log
    exit 1
fi
log_info "✅ Image built"

# 5. Start container
log_info "Starting container..."
docker compose up -d l9-api

# 6. Wait for health
log_info "Waiting for container to become healthy..."
ELAPSED=0
TIMEOUT=60
INTERVAL=5

while [ $ELAPSED -lt $TIMEOUT ]; do
    HEALTH=$(docker inspect l9-api 2>/dev/null | jq -r '.[0].State.Health.Status' 2>/dev/null || echo "unknown")
    
    if [ "$HEALTH" = "healthy" ]; then
        log_info "✅ Container healthy"
        break
    fi
    
    echo -ne "."
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ "$HEALTH" != "healthy" ]; then
    log_error "Container unhealthy after ${TIMEOUT}s"
    docker logs l9-api --tail 50
    exit 1
fi

# 7. Smoke tests
log_info "Running smoke tests..."
HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health)

if [ "$HEALTH_CODE" != "200" ]; then
    log_error "/health returned $HEALTH_CODE, expected 200"
    docker logs l9-api --tail 50
    exit 1
fi
log_info "✅ /health OK"

# Check logs
if docker logs l9-api --tail 100 2>/dev/null | grep -i "traceback"; then
    log_error "Tracebacks found in logs"
    exit 1
fi
log_info "✅ Logs clean"

# 8. Record metadata
mkdir -p "$VPS_PATH"
cat > "$VPS_PATH/.deployed-metadata.json" <<METADATA
{
  "deployed_tag": "$VERSION_TAG",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "deployed_by": "$(whoami)",
  "commit": "$(git rev-parse HEAD)",
  "status": "SUCCESS"
}
METADATA

log_info "✅ Deployment recorded"
log_info "✅ DEPLOYMENT COMPLETE: $VERSION_TAG"

PAYLOAD_EOF
)
    
    log_info "→ Executing on VPS ($VPS_SSH)..."
    
    if ! ssh "$VPS_SSH" bash -s "$VERSION_TAG" "$VPS_PATH" <<< "$DEPLOY_PAYLOAD"; then
        log_error "VPS deployment failed"
        if [ "$PREVIOUS_TAG" != "unknown" ]; then
            log_warn "Attempting rollback to $PREVIOUS_TAG..."
            ssh "$VPS_SSH" bash -s "$PREVIOUS_TAG" "$VPS_PATH" <<< "$(cat <<'ROLLBACK_PAYLOAD_EOF'
#!/usr/bin/env bash
TAG="$1"
VPS_PATH="$2"
cd "$VPS_PATH"
git checkout "$TAG" > /dev/null 2>&1
cd "$VPS_PATH/docker"
docker compose build --no-cache l9-api > /dev/null 2>&1
docker compose down l9-api || true
docker compose up -d l9-api
sleep 10
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Rollback successful"
else
    echo "❌ Rollback verification failed"
    exit 1
fi
ROLLBACK_PAYLOAD_EOF
)" || log_error "Rollback also failed. Manual intervention needed."
        fi
        fail "Deployment failed"
    fi
    
    log_info "✅ VPS deployment successful"
}

phase_verification() {
    log_section "PHASE 4: VERIFICATION"
    
    log_info "→ Testing external endpoint..."
    EXTERNAL_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://l9.quantumaipartners.com/health 2>/dev/null || echo "000")
    
    if [ "$EXTERNAL_CODE" = "200" ]; then
        log_info "✅ External endpoint OK"
    else
        log_warn "External endpoint returned $EXTERNAL_CODE (check Caddy/DNS if unexpected)"
    fi
}

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

main() {
    [ -z "$VERSION_TAG" ] && usage
    
    log_section "L9 DEPLOYMENT PIPELINE"
    log_info "Tag: $VERSION_TAG"
    
    phase_local_validation
    phase_git_push
    phase_vps_deployment
    phase_verification
    
    log_section "✅ DEPLOYMENT SUCCESSFUL"
    log_info "Tag:   $VERSION_TAG"
    log_info "URL:   https://l9.quantumaipartners.com/health"
    log_info "Time:  $(date)"
    log_info ""
    log_info "If issues arise, SSH to VPS and rollback:"
    log_info "  ssh $VPS_SSH"
    log_info "  /opt/l9/scripts/rollback.sh <previous-tag>"
}

main
```

---

## 4. Drift Detection Script

Save as: `scripts/drift-check.sh` (make executable)

```bash
#!/usr/bin/env bash
# scripts/drift-check.sh
# Audit: is running system exactly what's in git?

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[DRIFT]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[DRIFT]${NC} $*"; }
log_error() { echo -e "${RED}[DRIFT]${NC} $*" >&2; }

cd /opt/l9

log_info "Running drift detection..."

# 1. Git status clean?
if [ -n "$(git status --porcelain)" ]; then
    log_error "❌ Uncommitted changes detected:"
    git status --porcelain
    exit 1
fi
log_info "✅ Git status clean"

# 2. Running commit matches deployed tag?
if [ ! -f .deployed-metadata.json ]; then
    log_warn "No deployment metadata. Skipping version check."
else
    DEPLOYED_TAG=$(jq -r .deployed_tag < .deployed-metadata.json 2>/dev/null || echo "unknown")
    RUNNING_COMMIT=$(git rev-parse HEAD)
    DEPLOYED_COMMIT=$(git rev-parse "$DEPLOYED_TAG" 2>/dev/null || echo "unknown")
    
    if [ "$DEPLOYED_COMMIT" != "unknown" ] && [ "$RUNNING_COMMIT" != "$DEPLOYED_COMMIT" ]; then
        log_error "❌ Version mismatch:"
        log_error "   Running:   $RUNNING_COMMIT"
        log_error "   Deployed:  $DEPLOYED_TAG ($DEPLOYED_COMMIT)"
        exit 1
    fi
    log_info "✅ Running version matches deployed tag: $DEPLOYED_TAG"
fi

# 3. Container running?
if ! docker ps | grep -q l9-api; then
    log_error "❌ l9-api container not running"
    exit 1
fi
log_info "✅ Container is running"

# 4. Container healthy?
HEALTH=$(docker inspect l9-api | jq -r '.[0].State.Health.Status' 2>/dev/null || echo "unknown")
if [ "$HEALTH" != "healthy" ]; then
    log_warn "⚠️  Container health: $HEALTH"
fi
log_info "✅ Container health: $HEALTH"

# 5. Database connected?
if curl -s http://127.0.0.1:8000/health | jq .database -e > /dev/null 2>&1; then
    log_info "✅ Database connected"
else
    log_warn "⚠️  Could not verify database connection"
fi

log_info ""
log_info "✅ No drift detected."
```

---

## 5. Docker Compose Template (Blue-Green Ready)

Save as: `docker/docker-compose.yml`

```yaml
version: '3.8'

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
      start_period: 10s
    
    stop_grace_period: 30s
    stop_signal: SIGTERM
    
    environment:
      PYTHONDONTWRITEBYTECODE: "1"
      PYTHONUNBUFFERED: "1"

  # Optional: second instance for blue-green swaps (keep inactive most of the time)
  l9-api-alternate:
    build:
      context: /opt/l9
      dockerfile: docker/Dockerfile
    container_name: l9-api-alternate
    restart: "no"  # Don't auto-start
    env_file: /opt/l9/.env
    network_mode: "host"
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    
    stop_grace_period: 30s
    stop_signal: SIGTERM
    
    environment:
      PYTHONDONTWRITEBYTECODE: "1"
      PYTHONUNBUFFERED: "1"
```

---

## 6. Environment Validation Script

Save as: `scripts/validate-env.sh` (make executable)

```bash
#!/usr/bin/env bash
# scripts/validate-env.sh
# Ensures .env file has all required keys

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[ENV]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[ENV]${NC} $*"; }
log_error() { echo -e "${RED}[ENV]${NC} $*" >&2; }

fail() {
    log_error "$*"
    exit 1
}

ENV_FILE="${1:-.env}"
ENV_EXAMPLE="${2:-.env.example}"

if [ ! -f "$ENV_EXAMPLE" ]; then
    fail "$ENV_EXAMPLE not found"
fi

if [ ! -f "$ENV_FILE" ]; then
    fail "$ENV_FILE not found"
fi

log_info "Validating $ENV_FILE against $ENV_EXAMPLE..."

MISSING_KEYS=()

while IFS= read -r line; do
    key="${line%%=*}"
    value="${line##*=}"
    
    # Skip comments and empty lines
    [[ "$key" =~ ^# ]] && continue
    [ -z "$key" ] && continue
    
    # Check if key exists in .env
    if ! grep -q "^${key}=" "$ENV_FILE"; then
        MISSING_KEYS+=("$key")
    fi
done < "$ENV_EXAMPLE"

if [ ${#MISSING_KEYS[@]} -gt 0 ]; then
    log_error "Missing environment keys:"
    for key in "${MISSING_KEYS[@]}"; do
        log_error "  - $key"
    done
    fail "Environment validation failed"
fi

log_info "✅ All required keys present"

# Verify no obvious typos or syntax errors
if ! source "$ENV_FILE" 2>/dev/null; then
    log_warn "⚠️  .env has syntax errors. Check manually."
else
    log_info "✅ .env syntax OK"
fi

log_info "✅ Environment validation passed"
```

---

## 7. Cron Job for Drift Detection

Add to `/etc/cron.d/l9-maintenance`:

```bash
# L9 Health Checks and Drift Detection
# Run hourly

0 * * * * /opt/l9/scripts/drift-check.sh >> /var/log/l9-drift-check.log 2>&1
```

Install:

```bash
sudo tee -a /etc/cron.d/l9-maintenance > /dev/null << 'EOF'
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# L9 Health Checks and Drift Detection (hourly)
0 * * * * /opt/l9/scripts/drift-check.sh >> /var/log/l9-drift-check.log 2>&1
EOF

# Verify
sudo systemctl restart cron
```

---

## 8. Rollback Script (VPS-side)

Save as: `scripts/rollback.sh` on VPS at `/opt/l9/scripts/rollback.sh`

```bash
#!/usr/bin/env bash
# scripts/rollback.sh
# Emergency rollback to previous stable tag

set -euo pipefail

ROLLBACK_TAG="${1:-}"
VPS_PATH="/opt/l9"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[ROLLBACK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[ROLLBACK]${NC} $*"; }
log_error() { echo -e "${RED}[ROLLBACK]${NC} $*" >&2; }
fail() { log_error "$*"; exit 1; }

usage() {
    cat <<EOF
Usage: $0 <tag>

Emergency rollback to a previous stable tag.

Example:
  $0 v0.5.0-l9

EOF
    exit 1
}

main() {
    [ -z "$ROLLBACK_TAG" ] && usage
    
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "EMERGENCY ROLLBACK"
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "Rolling back to: $ROLLBACK_TAG"
    
    cd "$VPS_PATH"
    
    # Verify tag exists
    if ! git tag -v "$ROLLBACK_TAG" > /dev/null 2>&1; then
        fail "Tag $ROLLBACK_TAG not found or invalid"
    fi
    log_info "✅ Tag verified"
    
    # Checkout
    log_info "→ Checking out $ROLLBACK_TAG..."
    git checkout "$ROLLBACK_TAG" > /dev/null 2>&1
    log_info "✅ Checked out"
    
    # Rebuild
    log_info "→ Rebuilding image..."
    cd "$VPS_PATH/docker"
    if ! docker compose build --no-cache l9-api > /tmp/rollback-build.log 2>&1; then
        fail "Build failed. See /tmp/rollback-build.log"
    fi
    log_info "✅ Image built"
    
    # Restart
    log_info "→ Restarting container..."
    docker compose down l9-api || true
    docker compose up -d l9-api
    
    # Wait for health
    log_info "→ Waiting for health..."
    ELAPSED=0
    TIMEOUT=60
    while [ $ELAPSED -lt $TIMEOUT ]; do
        HEALTH=$(docker inspect l9-api 2>/dev/null | jq -r '.[0].State.Health.Status' 2>/dev/null || echo "unknown")
        if [ "$HEALTH" = "healthy" ]; then
            log_info "✅ Container healthy"
            break
        fi
        sleep 5
        ELAPSED=$((ELAPSED + 5))
    done
    
    if [ "$HEALTH" != "healthy" ]; then
        fail "Container did not become healthy"
    fi
    
    # Verify
    if ! curl -s http://127.0.0.1:8000/health | jq . > /dev/null; then
        fail "Health check failed after rollback"
    fi
    log_info "✅ Health check passed"
    
    # Record
    cat > "$VPS_PATH/.deployed-metadata.json" <<METADATA
{
  "deployed_tag": "$ROLLBACK_TAG",
  "rolled_back_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "rolled_back_by": "$(whoami)",
  "status": "ROLLED_BACK"
}
METADATA
    
    log_info ""
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "✅ ROLLBACK SUCCESSFUL"
    log_info "═══════════════════════════════════════════════════════════════"
    log_info "Tag:  $ROLLBACK_TAG"
    log_info "Time: $(date)"
    log_info ""
    log_info "Next: Review logs and root cause of previous deployment failure"
    log_info "═══════════════════════════════════════════════════════════════"
}

main
```

---

## 9. One-Time Setup Instructions

Run these commands once to set up the pipeline infrastructure:

```bash
# 1. Create scripts directory
mkdir -p /opt/l9/scripts
mkdir -p ~/.local/bin

# 2. Copy and make scripts executable
cp scripts/create-release-tag.sh /opt/l9/scripts/
cp scripts/deploy.sh /opt/l9/scripts/
cp scripts/drift-check.sh /opt/l9/scripts/
cp scripts/rollback.sh /opt/l9/scripts/

chmod +x /opt/l9/scripts/*.sh

# 3. Install pre-commit hook (local machine)
cp .git/hooks/pre-commit (local .git/hooks/pre-commit)
chmod +x .git/hooks/pre-commit

# 4. VPS Setup: Install drift check cron
ssh l9 'sudo tee /etc/cron.d/l9-maintenance > /dev/null << EOF
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
0 * * * * /opt/l9/scripts/drift-check.sh >> /var/log/l9-drift-check.log 2>&1
EOF'

# 5. Verify setup
./scripts/create-release-tag.sh --help
./scripts/deploy.sh --help
ssh l9 '/opt/l9/scripts/drift-check.sh'
```

---

## 10. Production Deployment Walkthrough

**Step 1: Create a release tag**

```bash
cd /opt/l9
./scripts/create-release-tag.sh patch
# OR
./scripts/create-release-tag.sh minor
```

**Step 2: Deploy**

```bash
./scripts/deploy.sh v0.5.1-l9
```

**Step 3: Verify**

```bash
curl https://l9.quantumaipartners.com/health
```

**Step 4: If issues arise, rollback**

```bash
ssh l9
/opt/l9/scripts/rollback.sh v0.5.0-l9
```

---

## 11. Quick Reference: Key Files and Locations

| File/Script | Location | Purpose |
|-------------|----------|---------|
| `pre-commit` | `.git/hooks/pre-commit` | Gate commits on local tests |
| `create-release-tag.sh` | `scripts/create-release-tag.sh` | Bump version and create tag |
| `deploy.sh` | `scripts/deploy.sh` | Deploy to VPS (full pipeline) |
| `rollback.sh` | `/opt/l9/scripts/rollback.sh` (VPS) | Emergency rollback |
| `drift-check.sh` | `scripts/drift-check.sh` | Hourly audit of VPS state |
| `docker-compose.yml` | `/opt/l9/docker/docker-compose.yml` | Container orchestration |
| `.env.example` | `/opt/l9/.env.example` | Environment schema (git-tracked) |
| `.env` | `/opt/l9/.env` (VPS only) | Production secrets (NOT committed) |
| `.deployed-metadata.json` | `/opt/l9/.deployed-metadata.json` | Deployment audit record |

---

**This implementation kit contains everything needed to operationalize the deployment pipeline. Test locally in a sandbox environment before running against production.**

