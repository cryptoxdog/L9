#!/bin/bash
# =============================================================================
# L9 Local Startup Script
# =============================================================================
# Starts L + Dashboard for local interaction until VPS/Slack is ready
#
# Usage: ./start_local.sh
# =============================================================================

set -e

cd "$(dirname "$0")"

echo "🚀 Starting L9 Local Environment..."
echo ""

# 1. Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# 2. Start Docker containers (L9 API + Memory + Postgres)
echo "📦 Starting Docker containers..."
docker compose up -d l9-api l9-memory-api postgres

# Wait for health
echo "⏳ Waiting for L9 API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/os/health > /dev/null 2>&1; then
        echo "✅ L9 API is healthy"
        break
    fi
    sleep 1
done

# 3. Start the Dashboard
echo ""
echo "🖥️  Starting Dashboard on http://127.0.0.1:5050 ..."
source venv/bin/activate
L9_API_URL="http://localhost:8000" python local_dashboard/app.py &
DASHBOARD_PID=$!

# Wait for dashboard
sleep 2
if curl -s http://127.0.0.1:5050/api/health > /dev/null 2>&1; then
    echo "✅ Dashboard is running"
else
    echo "⚠️  Dashboard may still be starting..."
fi

# 4. Open in browser
echo ""
echo "🌐 Opening dashboard in browser..."
open http://127.0.0.1:5050

echo ""
echo "=============================================="
echo "🎉 L9 is ACTIVE!"
echo ""
echo "  Dashboard: http://127.0.0.1:5050"
echo "  L9 API:    http://localhost:8000"
echo ""
echo "  To stop: ./stop_local.sh"
echo "=============================================="

# Keep running (dashboard is in background)
wait $DASHBOARD_PID

