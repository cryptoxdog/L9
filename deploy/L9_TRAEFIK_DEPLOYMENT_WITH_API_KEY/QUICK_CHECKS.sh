#!/bin/bash
# Quick checks for common issues

echo "🔍 Quick Diagnostic Checks"
echo "=========================="
echo ""

# Check 1: Environment Variables
echo "1️⃣  Environment Variables:"
docker exec l9-runtime env | grep -E "(SUPABASE|REDIS|API)" | sort || echo "❌ Cannot check - container not accessible"
echo ""

# Check 2: Internal Health Endpoint
echo "2️⃣  Internal Health Endpoint:"
docker exec l9-runtime curl -s http://localhost:8000/health || echo "❌ Health endpoint not responding"
echo ""

# Check 3: External Health Endpoint
echo "3️⃣  External Health Endpoint:"
curl -s -H "X-API-Key: 16a2376cfc93bc9acc2bb78c8c0a53ade7c1ef26ab0842a0140bfa7ac67508ba" https://quantumaipartners.com/health || echo "❌ External endpoint not responding"
echo ""

# Check 4: Application Logs (last 10 lines)
echo "4️⃣  Recent Application Logs:"
docker compose logs --tail=10 l9-runtime 2>/dev/null || docker-compose logs --tail=10 l9-runtime
echo ""

# Check 5: Is main.py accessible?
echo "5️⃣  Application Files:"
docker exec l9-runtime ls -la /app/main.py 2>/dev/null && echo "✅ main.py exists" || echo "❌ main.py not found"
echo ""

# Check 6: Is uvicorn running?
echo "6️⃣  Uvicorn Process:"
docker exec l9-runtime ps aux | grep uvicorn | grep -v grep && echo "✅ Uvicorn is running" || echo "❌ Uvicorn not running"
echo ""

echo "Done! Review output above for issues."

