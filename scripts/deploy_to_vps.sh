#!/usr/bin/env bash
# =============================================================================
# L9 VPS Deployment Script
# Version: 1.0.0
#
# Deploys L9 to VPS with:
# - Pre-flight checks
# - Backup of current version
# - Code sync via rsync
# - Docker rebuild and restart
# - Post-deploy verification
#
# Usage: ./scripts/deploy_to_vps.sh
# =============================================================================

set -euo pipefail

# Configuration
VPS_HOST="157.180.73.53"
VPS_USER="root"
VPS_PATH="/root/L9"
BACKUP_PATH="/root/L9_backups"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[✓]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[✗]${NC} $*"; }

# Resolve script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  L9 VPS Deployment${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# =============================================================================
# Pre-Flight Checks
# =============================================================================

log_info "Running pre-flight checks..."

# Check SSH connectivity
log_info "Testing SSH connection to $VPS_HOST..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$VPS_USER@$VPS_HOST" "echo 'SSH OK'" &>/dev/null; then
    log_error "Cannot connect to VPS via SSH"
    log_error "Ensure your SSH key is configured and VPS is reachable"
    exit 1
fi
log_success "SSH connection OK"

# Check local smoke test passed
log_info "Running local smoke test..."
if ! ./scripts/precommit_docker_smoke.sh; then
    log_error "Local smoke test failed - fix issues before deploying"
    exit 1
fi
log_success "Local smoke test passed"

# =============================================================================
# Create Backup on VPS
# =============================================================================

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
log_info "Creating backup on VPS ($TIMESTAMP)..."

ssh "$VPS_USER@$VPS_HOST" bash <<EOF
    set -e
    mkdir -p $BACKUP_PATH
    if [ -d "$VPS_PATH" ]; then
        cp -r "$VPS_PATH" "$BACKUP_PATH/L9_$TIMESTAMP"
        # Keep only last 5 backups
        ls -dt $BACKUP_PATH/L9_* | tail -n +6 | xargs rm -rf 2>/dev/null || true
        echo "Backup created: L9_$TIMESTAMP"
    else
        echo "No existing deployment to backup"
    fi
EOF
log_success "Backup complete"

# =============================================================================
# Sync Code to VPS
# =============================================================================

log_info "Syncing code to VPS..."

rsync -avz --delete \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.env' \
    --exclude='.env.local' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='.mypy_cache' \
    --exclude='.ruff_cache' \
    --exclude='postgres_data' \
    --exclude='*.log' \
    "$PROJECT_ROOT/" "$VPS_USER@$VPS_HOST:$VPS_PATH/"

log_success "Code synced"

# =============================================================================
# Rebuild and Restart on VPS
# =============================================================================

log_info "Rebuilding and restarting Docker stack on VPS..."

ssh "$VPS_USER@$VPS_HOST" bash <<EOF
    set -e
    cd $VPS_PATH
    
    echo "Pulling latest base images..."
    docker compose pull --quiet
    
    echo "Building images..."
    docker compose build --quiet
    
    echo "Stopping current stack..."
    docker compose down --remove-orphans
    
    echo "Starting new stack..."
    docker compose up -d
    
    echo "Waiting for services to be healthy..."
    sleep 10
    
    echo "Service status:"
    docker compose ps
EOF

log_success "Stack restarted"

# =============================================================================
# Post-Deploy Verification
# =============================================================================

log_info "Running post-deploy verification..."

# Wait a bit for services to fully initialize
sleep 5

# Check health endpoint
HEALTH_STATUS=$(ssh "$VPS_USER@$VPS_HOST" "curl -sf http://localhost:8000/health" 2>/dev/null || echo "FAILED")

if [[ "$HEALTH_STATUS" == *"ok"* ]]; then
    log_success "Health check passed"
else
    log_error "Health check failed!"
    log_error "Response: $HEALTH_STATUS"
    log_warn "Consider running: make rollback"
    exit 1
fi

# Check other endpoints
for endpoint in "/" "/os/health" "/agent/health" "/docs"; do
    STATUS=$(ssh "$VPS_USER@$VPS_HOST" "curl -sf -o /dev/null -w '%{http_code}' http://localhost:8000$endpoint" 2>/dev/null || echo "000")
    if [[ "$STATUS" == "200" ]]; then
        log_success "$endpoint → $STATUS"
    else
        log_warn "$endpoint → $STATUS"
    fi
done

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  VPS: $VPS_USER@$VPS_HOST"
echo "  Path: $VPS_PATH"
echo "  Backup: $BACKUP_PATH/L9_$TIMESTAMP"
echo ""
echo "  Commands:"
echo "    make vps-logs    - View logs"
echo "    make vps-status  - Check status"
echo "    make rollback    - Rollback if needed"
echo ""

