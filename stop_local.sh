#!/bin/bash
# =============================================================================
# L9 Local Stop Script
# =============================================================================

cd "$(dirname "$0")"

echo "🛑 Stopping L9 Local Environment..."

# Stop dashboard
pkill -f "local_dashboard/app.py" 2>/dev/null && echo "✅ Dashboard stopped" || echo "Dashboard not running"

# Stop Mac Agent Runner (if running)
pkill -f "mac_agent.runner" 2>/dev/null && echo "✅ Mac Agent stopped" || echo "Mac Agent not running"

# Docker containers stay running (comment out to stop them too)
# docker compose down

echo ""
echo "✅ Local services stopped. Docker containers still running."
echo "   To stop Docker: docker compose down"

