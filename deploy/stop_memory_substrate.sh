#!/bin/bash
# =============================================================================
# L9 Memory Substrate - Stop Script
# Version: 1.0.0
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 Stopping L9 Memory Substrate..."

cd "$SCRIPT_DIR"
docker compose -f docker-compose.memory_substrate_v1.0.0.yaml down

echo "✅ Memory Substrate stopped"

