#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# L9 VPS RELEASE GATE
# ═══════════════════════════════════════════════════════════════════════════════
# Idempotent release-gate script. Stops on first failure.
# Usage: sudo bash /opt/l9/ops/vps_release_gate.sh
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG (edit these for your environment)
# ─────────────────────────────────────────────────────────────────────────────
REPO_DIR="/opt/l9"
SERVICE_API="l9"
SERVICE_AGENT="l9-agent"
API_PORT="8000"
HEALTH_ENDPOINT="/health"
OPENAPI_ENDPOINT="/openapi.json"

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
PASS_COUNT=0
FAIL_COUNT=0
BLOCKERS=""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

gate_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS_COUNT++))
}

gate_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL_COUNT++))
    BLOCKERS="${BLOCKERS}\n  - $1"
    echo -e "${RED}STOPPING: Gate failure${NC}"
    exit 1
}

gate_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

separator() {
    echo ""
    echo "─────────────────────────────────────────────────────────────"
    echo "$1"
    echo "─────────────────────────────────────────────────────────────"
}

# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  L9 VPS RELEASE GATE"
echo "  $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "═══════════════════════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────────────────────
separator "GATE 1: REPO SYNC"
# ─────────────────────────────────────────────────────────────────────────────
cd "$REPO_DIR" || gate_fail "cd $REPO_DIR"

git fetch --all --prune || gate_fail "git fetch"
git pull --ff-only origin main || gate_fail "git pull --ff-only"

COMMIT=$(git rev-parse --short HEAD)
BRANCH=$(git branch --show-current)
echo "  Commit: $COMMIT"
echo "  Branch: $BRANCH"

if [[ "$BRANCH" == "main" ]]; then
    gate_pass "repo-sync (main @ $COMMIT)"
else
    gate_fail "repo-sync (expected main, got $BRANCH)"
fi

# ─────────────────────────────────────────────────────────────────────────────
separator "GATE 2: VENV VERIFICATION"
# ─────────────────────────────────────────────────────────────────────────────
if [[ -f "$REPO_DIR/venv/bin/activate" ]]; then
    source "$REPO_DIR/venv/bin/activate"
else
    gate_fail "venv not found at $REPO_DIR/venv"
fi

PY_PATH=$(which python)
PY_VER=$(python --version 2>&1)

echo "  Python: $PY_VER"
echo "  Path: $PY_PATH"

if [[ "$PY_PATH" == "$REPO_DIR/venv"* ]]; then
    gate_pass "venv-path"
else
    gate_fail "venv-path (python not in $REPO_DIR/venv)"
fi

if [[ "$PY_VER" == *"3.12"* ]] || [[ "$PY_VER" == *"3.11"* ]]; then
    gate_pass "python-version ($PY_VER)"
else
    gate_fail "python-version (expected 3.11+, got $PY_VER)"
fi

# ─────────────────────────────────────────────────────────────────────────────
separator "GATE 3: PIP INSTALL"
# ─────────────────────────────────────────────────────────────────────────────
python -m pip install -e . --quiet --disable-pip-version-check || gate_fail "pip install -e ."
gate_pass "pip-install"

python -m pip check || gate_fail "pip check"
gate_pass "pip-check (no broken deps)"

# ─────────────────────────────────────────────────────────────────────────────
separator "GATE 4: COMPILEALL"
# ─────────────────────────────────────────────────────────────────────────────
COMPILE_OUT=$(python -m compileall -q -x "venv|node_modules|__pycache__|\.git|_l9_GHOST" . 2>&1)
if [[ -z "$COMPILE_OUT" ]]; then
    gate_pass "compileall (clean)"
else
    echo "$COMPILE_OUT"
    gate_fail "compileall (syntax errors)"
fi

# ─────────────────────────────────────────────────────────────────────────────
separator "GATE 5: SMOKE TESTS"
# ─────────────────────────────────────────────────────────────────────────────
if [[ -f "$REPO_DIR/tests/smoke_test_root.py" ]]; then
    python "$REPO_DIR/tests/smoke_test_root.py" || gate_fail "smoke_test_root.py"
    gate_pass "smoke_test_root.py"
else
    gate_warn "smoke_test_root.py not found, skipping"
fi

if [[ -f "$REPO_DIR/tests/smoke_email.py" ]]; then
    python "$REPO_DIR/tests/smoke_email.py" || gate_fail "smoke_email.py"
    gate_pass "smoke_email.py"
else
    gate_warn "smoke_email.py not found, skipping"
fi

# ─────────────────────────────────────────────────────────────────────────────
separator "GATE 6: SYSTEMD RESTART"
# ─────────────────────────────────────────────────────────────────────────────
systemctl daemon-reload || gate_fail "daemon-reload"
gate_pass "daemon-reload"

systemctl restart "$SERVICE_API" || gate_fail "restart $SERVICE_API"
gate_pass "restart $SERVICE_API"

if systemctl list-units --type=service --all | grep -q "$SERVICE_AGENT"; then
    systemctl restart "$SERVICE_AGENT" || gate_fail "restart $SERVICE_AGENT"
    gate_pass "restart $SERVICE_AGENT"
else
    gate_warn "$SERVICE_AGENT service not found, skipping"
fi

# Wait for services to stabilize
sleep 3

# ─────────────────────────────────────────────────────────────────────────────
separator "GATE 7: SERVICE HEALTH"
# ─────────────────────────────────────────────────────────────────────────────
API_STATUS=$(systemctl is-active "$SERVICE_API" 2>/dev/null || echo "inactive")
echo "  $SERVICE_API: $API_STATUS"

if [[ "$API_STATUS" == "active" ]]; then
    gate_pass "$SERVICE_API running"
else
    journalctl -u "$SERVICE_API" -n 20 --no-pager
    gate_fail "$SERVICE_API not running"
fi

if systemctl list-units --type=service --all | grep -q "$SERVICE_AGENT"; then
    AGENT_STATUS=$(systemctl is-active "$SERVICE_AGENT" 2>/dev/null || echo "inactive")
    echo "  $SERVICE_AGENT: $AGENT_STATUS"
    if [[ "$AGENT_STATUS" == "active" ]]; then
        gate_pass "$SERVICE_AGENT running"
    else
        gate_warn "$SERVICE_AGENT not running (non-blocking)"
    fi
fi

# Check for import errors in recent logs
IMPORT_ERRORS=$(journalctl -u "$SERVICE_API" -n 100 --no-pager 2>/dev/null | grep -i "importerror\|modulenotfounderror" | head -3 || true)
if [[ -z "$IMPORT_ERRORS" ]]; then
    gate_pass "no import errors in logs"
else
    echo "  Import errors found:"
    echo "$IMPORT_ERRORS"
    gate_fail "import errors in logs"
fi

# ─────────────────────────────────────────────────────────────────────────────
separator "GATE 8: API LIVENESS"
# ─────────────────────────────────────────────────────────────────────────────
HEALTH_URL="http://127.0.0.1:${API_PORT}${HEALTH_ENDPOINT}"
OPENAPI_URL="http://127.0.0.1:${API_PORT}${OPENAPI_ENDPOINT}"

HEALTH_RESP=$(curl -sS --max-time 5 "$HEALTH_URL" 2>/dev/null || echo "CURL_FAILED")
echo "  Health response: $HEALTH_RESP"

if [[ "$HEALTH_RESP" == *"healthy"* ]] || [[ "$HEALTH_RESP" == *"ok"* ]] || [[ "$HEALTH_RESP" == *"status"* ]]; then
    gate_pass "health endpoint"
else
    gate_fail "health endpoint (bad response)"
fi

OPENAPI_RESP=$(curl -sS --max-time 5 "$OPENAPI_URL" 2>/dev/null || echo "CURL_FAILED")
if [[ "$OPENAPI_RESP" == "CURL_FAILED" ]]; then
    gate_fail "openapi endpoint (curl failed)"
fi

OPENAPI_PATHS=$(echo "$OPENAPI_RESP" | python -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('paths',{})))" 2>/dev/null || echo "0")
echo "  OpenAPI paths: $OPENAPI_PATHS"

if [[ "$OPENAPI_PATHS" -gt 0 ]]; then
    gate_pass "openapi paths ($OPENAPI_PATHS routes)"
else
    gate_fail "openapi paths (0 routes)"
fi

# ─────────────────────────────────────────────────────────────────────────────
separator "GATE 9: JOURNAL TAIL"
# ─────────────────────────────────────────────────────────────────────────────
echo "  Last 10 log entries:"
journalctl -u "$SERVICE_API" -n 10 --no-pager 2>/dev/null | tail -10 || true
gate_pass "journal tail (info only)"

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL VERDICT
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  RELEASE GATE VERDICT"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "  PASSED: $PASS_COUNT"
echo "  FAILED: $FAIL_COUNT"
echo "  COMMIT: $COMMIT"
echo ""

if [[ $FAIL_COUNT -eq 0 ]]; then
    echo -e "  ${GREEN}RELEASE_STATUS: PASS${NC}"
    echo "  BLOCKERS: NONE"
    echo -e "  ${GREEN}SAFE_TO_PROCEED: YES${NC}"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    exit 0
else
    echo -e "  ${RED}RELEASE_STATUS: FAIL${NC}"
    echo -e "  BLOCKERS:$BLOCKERS"
    echo -e "  ${RED}SAFE_TO_PROCEED: NO${NC}"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    exit 1
fi
