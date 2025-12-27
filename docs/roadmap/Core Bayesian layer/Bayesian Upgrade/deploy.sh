#!/bin/bash
#
# Probabilistic Governance Deployment Script
# Automates deployment to GlobalCommands directory
#
# Usage: bash deploy.sh [--dry-run]
#

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TARGET_DIR="/Users/ib-mac/Dropbox/Cursor Governance/GlobalCommands"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

DRY_RUN=false
if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo -e "${YELLOW}🔍 DRY RUN MODE - No files will be modified${NC}\n"
fi

echo -e "${GREEN}🚀 Probabilistic Governance Deployment${NC}"
echo "================================================"
echo ""

# Pre-flight checks
echo "📋 Pre-flight checks..."

if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}❌ Target directory not found: $TARGET_DIR${NC}"
    exit 1
fi

if [ ! -f "$TARGET_DIR/foundation/logic/rule-registry.json" ]; then
    echo -e "${RED}❌ rule-registry.json not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Pre-flight checks passed${NC}\n"

# Backup
echo "💾 Creating backup..."
if [ "$DRY_RUN" = false ]; then
    BACKUP_FILE="$TARGET_DIR/foundation/logic/rule-registry.json.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$TARGET_DIR/foundation/logic/rule-registry.json" "$BACKUP_FILE"
    echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}\n"
else
    echo -e "${YELLOW}[DRY RUN] Would create backup${NC}\n"
fi

# Deploy foundation components
echo "🔧 Deploying foundation components..."

deploy_file() {
    src="$1"
    dest="$2"
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$(dirname "$dest")"
        cp "$src" "$dest"
        chmod +x "$dest" 2>/dev/null || true
        echo -e "${GREEN}  ✅ $src → $dest${NC}"
    else
        echo -e "${YELLOW}  [DRY RUN] Would deploy: $src → $dest${NC}"
    fi
}

deploy_file \
    "$SCRIPT_DIR/foundation/probabilistic_engine.py" \
    "$TARGET_DIR/foundation/logic/probabilistic_engine.py"

deploy_file \
    "$SCRIPT_DIR/foundation/hybrid_kernel.py" \
    "$TARGET_DIR/foundation/logic/hybrid_kernel.py"

echo ""

# Deploy learning components
echo "🧠 Deploying learning components..."

deploy_file \
    "$SCRIPT_DIR/learning/auto_calibrator.py" \
    "$TARGET_DIR/intelligence/learning/auto_calibrator.py"

deploy_file \
    "$SCRIPT_DIR/learning/feedback_collector.py" \
    "$TARGET_DIR/intelligence/learning/feedback_collector.py"

echo ""

# Deploy models
echo "📊 Deploying decision models..."

mkdir -p "$TARGET_DIR/intelligence/models" 2>/dev/null || true

for model in "$SCRIPT_DIR/models"/*.md; do
    deploy_file \
        "$model" \
        "$TARGET_DIR/intelligence/models/$(basename "$model")"
done

echo ""

# Deploy telemetry
echo "📈 Deploying telemetry/monitoring..."

deploy_file \
    "$SCRIPT_DIR/telemetry/calibration_dashboard.py" \
    "$TARGET_DIR/telemetry/calibration_dashboard.py"

# Create telemetry directories
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$TARGET_DIR/telemetry/logs"
    mkdir -p "$TARGET_DIR/telemetry/reports/calibration"
    echo -e "${GREEN}  ✅ Telemetry directories created${NC}"
else
    echo -e "${YELLOW}  [DRY RUN] Would create telemetry directories${NC}"
fi

echo ""

# Schema update prompt
echo "⚙️  Schema Update Required..."
echo ""
echo "  ⚠️  MANUAL STEP: Update rule-registry.json"
echo ""
echo "  Add these sections to $TARGET_DIR/foundation/logic/rule-registry.json:"
echo ""
echo '  "probabilistic_models": [],'
echo '  "probabilistic_thresholds": { ... },'
echo '  "calibration_parameters": { ... }'
echo ""
echo "  See: schema/rule-registry-v2-schema.json for complete structure"
echo ""
echo "  Or run: python3 scripts/merge_schema.py (if available)"
echo ""

# Test
echo "🧪 Running tests..."

if [ "$DRY_RUN" = false ]; then
    cd "$TARGET_DIR"
    python3 foundation/logic/probabilistic_engine.py > /tmp/prob_test.log 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✅ Probabilistic engine tests passed${NC}"
    else
        echo -e "${RED}  ❌ Tests failed - check /tmp/prob_test.log${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}  [DRY RUN] Would run tests${NC}"
fi

echo ""

# Summary
echo "================================================"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "📋 Next Steps:"
echo "  1. ⚙️  Update rule-registry.json (see prompt above)"
echo "  2. 🧪 Test: python3 foundation/logic/probabilistic_engine.py"
echo "  3. 📊 Monitor: python3 telemetry/calibration_dashboard.py"
echo "  4. 💬 Provide feedback on first 50 decisions"
echo ""
echo "📖 Documentation:"
echo "  • Deployment Guide: Bayesian Upgrade/docs/DEPLOYMENT_GUIDE.md"
echo "  • Integration Guide: Bayesian Upgrade/docs/INTEGRATION_GUIDE.md"
echo "  • Quick Reference: Bayesian Upgrade/docs/QUICK_REFERENCE.md"
echo ""
echo -e "${GREEN}System ready for probabilistic governance! 🎉${NC}"

