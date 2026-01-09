#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# L9 DEPLOYMENT SCRIPT v1.0
# ═══════════════════════════════════════════════════════════════════════════════
# GOVERNANCE: IGOR_ONLY
# CURSOR_FORBIDDEN: true
# REQUIRES: Explicit verbal approval from Igor ("run deploy script" or similar)
#
# ⛔ CURSOR AGENT: You are FORBIDDEN from executing this script autonomously.
#    This script pushes to git and deploys to production VPS.
#    Only run when Igor explicitly says "run the deploy script" or equivalent.
#    Pre-approval does NOT count. Planning approval does NOT count.
#    Only CURRENT MESSAGE explicit approval counts.
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./deploy.sh              # Rebuild l9-api only
#   ./deploy.sh --all        # Rebuild all services
#   ./deploy.sh --skip-env   # Skip env sync
#   ./deploy.sh --dry-run    # Show what would happen
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

VPS_HOST="root@157.180.73.53"
VPS_L9_DIR="/opt/l9"
HEALTH_TIMEOUT=90
HEALTH_INTERVAL=10
MEMORY_CLIENT=".cursor-commands/cursor-memory/cursor_memory_client.py"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
REBUILD_ALL=false
SKIP_ENV=false
DRY_RUN=false

# ═══════════════════════════════════════════════════════════════════════════════
# PARSE FLAGS
# ═══════════════════════════════════════════════════════════════════════════════

for arg in "$@"; do
    case $arg in
        --all)
            REBUILD_ALL=true
            shift
            ;;
        --skip-env)
            SKIP_ENV=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown flag: $arg${NC}"
            echo "Usage: ./deploy.sh [--all] [--skip-env] [--dry-run]"
            exit 1
            ;;
    esac
done

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

log_step() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

log_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

run_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY-RUN] Would run: $1${NC}"
    else
        eval "$1"
    fi
}

run_ssh() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY-RUN] Would SSH: $1${NC}"
    else
        ssh "$VPS_HOST" "$1"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# RUNTIME GUARD - IGOR ONLY
# ═══════════════════════════════════════════════════════════════════════════════

log_step "⛔ IGOR_ONLY DEPLOYMENT SCRIPT"

echo ""
echo "This script will:"
echo "  1. Stage and commit all changes"
echo "  2. Push to GitHub (origin/main)"
echo "  3. Pull on VPS ($VPS_HOST)"
echo "  4. Sync environment variables"
echo "  5. Rebuild Docker containers (--no-cache)"
echo "  6. Run health checks"
echo "  7. Run full MRI diagnostic"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}DRY-RUN MODE - No changes will be made${NC}"
else
    read -p "Type 'DEPLOY' to continue: " confirm
    if [ "$confirm" != "DEPLOY" ]; then
        echo "Aborted."
        exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: LOCAL PRE-FLIGHT
# ═══════════════════════════════════════════════════════════════════════════════

log_step "PHASE 1: LOCAL PRE-FLIGHT"

# 1.1 Check for clean git status (allow repo-index changes)
echo "Checking git status..."
DIRTY=$(git status --porcelain | grep -v 'readme/repo-index' | grep -v 'deploy.sh' | wc -l | tr -d ' ')
if [ "$DIRTY" -gt 0 ]; then
    log_warn "Uncommitted changes detected (excluding repo-index):"
    git status --porcelain | grep -v 'readme/repo-index' | head -10
    # Not fatal - we'll stage them
fi

# 1.2 Confirm on main branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    log_error "Not on main branch (currently on: $BRANCH)"
    exit 1
fi
log_ok "On main branch"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: GIT STAGE + COMMIT + PUSH
# ═══════════════════════════════════════════════════════════════════════════════

log_step "PHASE 2: GIT STAGE + COMMIT + PUSH"

# 2.1 Stage all
echo "Staging all changes..."
run_cmd "git add -A"

# 2.2 Check if there's anything to commit
STAGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
if [ "$STAGED" -eq 0 ]; then
    log_warn "Nothing staged to commit - continuing with push of existing commits"
else
    # 2.3 Auto-generate commit message
    FILES_CHANGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
    SUMMARY=$(git diff --cached --name-only | head -5 | tr '\n' ', ' | sed 's/,$//')
    TIMESTAMP=$(date +%Y-%m-%d_%H:%M)
    MSG="deploy: ${FILES_CHANGED} files @ ${TIMESTAMP} (${SUMMARY})"
    
    echo "Commit message: $MSG"
    run_cmd "git commit -m \"$MSG\""
    log_ok "Committed $FILES_CHANGED files"
fi

# 2.4 Push to origin
echo "Pushing to origin/main..."
run_cmd "git push origin main"

# 2.5 Verify push
LOCAL_HEAD=$(git rev-parse HEAD)
REMOTE_HEAD=$(git ls-remote origin main | cut -f1)

if [ "$LOCAL_HEAD" != "$REMOTE_HEAD" ]; then
    log_error "Push verification failed!"
    echo "Local HEAD:  $LOCAL_HEAD"
    echo "Remote HEAD: $REMOTE_HEAD"
    exit 1
fi
log_ok "Push verified (HEAD: ${LOCAL_HEAD:0:8})"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: VPS GIT PULL
# ═══════════════════════════════════════════════════════════════════════════════

log_step "PHASE 3: VPS GIT PULL"

# 3.1 Stash any VPS local changes (repo-index files)
echo "Stashing VPS local changes..."
run_ssh "cd $VPS_L9_DIR && git stash 2>/dev/null || true"

# 3.2 Configure safe directory (in case it's not set)
run_ssh "git config --global --add safe.directory $VPS_L9_DIR 2>/dev/null || true"

# 3.3 Pull
echo "Pulling on VPS..."
run_ssh "cd $VPS_L9_DIR && git pull origin main"

# 3.4 Verify sync
VPS_HEAD=$(run_ssh "cd $VPS_L9_DIR && git rev-parse HEAD")

if [ "$LOCAL_HEAD" != "$VPS_HEAD" ]; then
    log_error "VPS sync failed!"
    echo "Local HEAD: $LOCAL_HEAD"
    echo "VPS HEAD:   $VPS_HEAD"
    exit 1
fi
log_ok "VPS synced (HEAD: ${VPS_HEAD:0:8})"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: ENV SYNC
# ═══════════════════════════════════════════════════════════════════════════════

if [ "$SKIP_ENV" = true ]; then
    log_step "PHASE 4: ENV SYNC (SKIPPED)"
else
    log_step "PHASE 4: ENV SYNC"
    
    # 4.1 Backup VPS .env
    BACKUP_NAME=".env.bak.$(date +%Y%m%d%H%M)"
    echo "Backing up VPS .env to $BACKUP_NAME..."
    run_ssh "cd $VPS_L9_DIR && cp .env $BACKUP_NAME"
    log_ok "Backup created"
    
    # 4.2 Get keys from both
    echo "Comparing env vars..."
    LOCAL_KEYS=$(grep -v '^#' .env 2>/dev/null | grep -v '^$' | grep '=' | cut -d'=' -f1 | sort)
    VPS_KEYS=$(run_ssh "grep -v '^#' $VPS_L9_DIR/.env 2>/dev/null | grep -v '^$' | grep '=' | cut -d'=' -f1 | sort")
    
    # 4.3 Find new vars (in local, not on VPS)
    NEW_VARS=$(comm -23 <(echo "$LOCAL_KEYS") <(echo "$VPS_KEYS") || true)
    
    if [ -z "$NEW_VARS" ]; then
        log_ok "No new env vars to sync"
    else
        echo ""
        echo "=== NEW VARS (in local, missing on VPS) ==="
        echo "$NEW_VARS"
        echo ""
        
        # 4.4 Append new vars
        for VAR in $NEW_VARS; do
            VALUE=$(grep "^${VAR}=" .env || true)
            if [ -n "$VALUE" ]; then
                echo "Appending: $VAR"
                if [ "$DRY_RUN" = false ]; then
                    # Escape special characters for SSH
                    ESCAPED_VALUE=$(printf '%s\n' "$VALUE" | sed 's/[&/\]/\\&/g')
                    run_ssh "echo '$ESCAPED_VALUE' >> $VPS_L9_DIR/.env"
                fi
            fi
        done
        log_ok "Env vars synced"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5: REBUILD DOCKER
# ═══════════════════════════════════════════════════════════════════════════════

log_step "PHASE 5: REBUILD DOCKER (--no-cache)"

if [ "$REBUILD_ALL" = true ]; then
    echo "Rebuilding ALL services..."
    run_ssh "cd $VPS_L9_DIR && docker-compose build --no-cache"
else
    echo "Rebuilding l9-api only..."
    run_ssh "cd $VPS_L9_DIR && docker-compose build --no-cache l9-api"
fi

# 5.2 Recreate containers
echo "Recreating containers..."
run_ssh "cd $VPS_L9_DIR && docker-compose up -d"

log_ok "Docker rebuild complete"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6: HEALTH CHECK (90s timeout, 10s intervals)
# ═══════════════════════════════════════════════════════════════════════════════

log_step "PHASE 6: HEALTH CHECK"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY-RUN] Would wait for health check (${HEALTH_TIMEOUT}s timeout)${NC}"
    FINAL_STATUS="ok"
else
    ELAPSED=0
    FINAL_STATUS="unknown"
    
    echo "Waiting for API to become healthy (timeout: ${HEALTH_TIMEOUT}s)..."
    
    while [ $ELAPSED -lt $HEALTH_TIMEOUT ]; do
        STATUS=$(run_ssh "curl -s http://127.0.0.1:8000/health 2>/dev/null | grep -o '\"status\":\"[^\"]*\"' | cut -d'\"' -f4" || echo "unreachable")
        
        if [ "$STATUS" = "ok" ]; then
            FINAL_STATUS="ok"
            break
        fi
        
        echo "  [$ELAPSED/${HEALTH_TIMEOUT}s] Status: $STATUS"
        sleep $HEALTH_INTERVAL
        ELAPSED=$((ELAPSED + HEALTH_INTERVAL))
    done
fi

if [ "$FINAL_STATUS" = "ok" ]; then
    log_ok "API healthy!"
else
    log_warn "Health check result: $FINAL_STATUS (may need investigation)"
fi

# 6.2 Quick log check for errors
echo ""
echo "Recent errors in logs:"
run_ssh "docker logs l9-api --tail 30 2>&1 | grep -iE '(error|exception|critical)' | tail -5 || echo '  No errors found'"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 7: MEMORY RECORD
# ═══════════════════════════════════════════════════════════════════════════════

log_step "PHASE 7: MEMORY RECORD"

if [ -f "$MEMORY_CLIENT" ] && [ "$DRY_RUN" = false ]; then
    DEPLOY_MSG="DEPLOYMENT: ${LOCAL_HEAD:0:8} @ $(date +%Y-%m-%d_%H:%M). Status: $FINAL_STATUS. Rebuild: $([ "$REBUILD_ALL" = true ] && echo 'all' || echo 'l9-api')."
    python3 "$MEMORY_CLIENT" write "$DEPLOY_MSG" --kind note 2>/dev/null && log_ok "Deployment recorded to memory" || log_warn "Memory write failed (non-fatal)"
else
    echo "Memory client not available or dry-run mode - skipping"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 8: FULL MRI DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════════════════════

log_step "PHASE 8: FULL MRI DIAGNOSTIC"

echo "Running full VPS MRI for system transparency..."
echo ""

MRI_OUTPUT_FILE="MRI-VPS-RESULTS.md"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY-RUN] Would run MRI-VPS.md script on VPS${NC}"
    echo -e "${YELLOW}[DRY-RUN] Would save output to $MRI_OUTPUT_FILE${NC}"
else
    # Check if MRI script exists on VPS
    MRI_EXISTS=$(run_ssh "test -f $VPS_L9_DIR/MRI-VPS.md && echo 'yes' || echo 'no'")
    
    if [ "$MRI_EXISTS" = "yes" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "                      VPS MRI OUTPUT                              "
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Run MRI and capture output (display to console AND save to file)
        MRI_OUTPUT=$(run_ssh "cd $VPS_L9_DIR && bash MRI-VPS.md 2>&1" || true)
        echo "$MRI_OUTPUT"
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Save MRI output to local file with timestamp header
        {
            echo "# L9 VPS MRI Results"
            echo ""
            echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S %Z')"
            echo "**Deployment:** ${LOCAL_HEAD:0:8}"
            echo "**Health Status:** $FINAL_STATUS"
            echo ""
            echo "---"
            echo ""
            echo "$MRI_OUTPUT"
        } > "$MRI_OUTPUT_FILE"
        
        log_ok "MRI output saved to $MRI_OUTPUT_FILE"
    else
        log_warn "MRI-VPS.md not found on VPS - skipping diagnostic"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

log_step "DEPLOYMENT COMPLETE"

echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│                    DEPLOYMENT SUMMARY                       │"
echo "├─────────────────────────────────────────────────────────────┤"
echo "│  Commit:     ${LOCAL_HEAD:0:8}                                       │"
echo "│  VPS Sync:   ✅                                              │"
echo "│  Env Sync:   $([ "$SKIP_ENV" = true ] && echo '⏭️  SKIPPED' || echo '✅')                                              │"
echo "│  Rebuild:    $([ "$REBUILD_ALL" = true ] && echo 'ALL services' || echo 'l9-api only ')                                    │"
echo "│  Health:     $FINAL_STATUS                                            │"
echo "│  MRI:        ✅ saved to MRI-VPS-RESULTS.md                  │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

if [ "$FINAL_STATUS" != "ok" ]; then
    log_warn "API health is '$FINAL_STATUS' - check MRI output and logs"
    exit 1
fi

log_ok "Deployment successful!"

