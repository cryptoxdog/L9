# L9 VPS MRI - Ultra Diagnostic
echo "╔════════════════════════════════════════════════════════════════╗" && \
echo "║      L9 VPS MRI - COMPLETE SYSTEM DIAGNOSTIC                   ║" && \
echo "╚════════════════════════════════════════════════════════════════╝" && \
echo "Generated: $(date)" && echo "" && \
echo "━━━ A1. SYSTEM IDENTITY ━━━" && \
hostname && echo "User: $(whoami)" && uname -a && \
ip addr show | grep "inet " | grep -v "127.0.0.1" && echo "" && \
echo "━━━ A2. PUBLIC IP & DNS ━━━" && \
echo "Public IP: $(curl -s ifconfig.me)" && \
getent hosts l9.quantumaipartners.com 2>/dev/null || echo "DNS not configured" && echo "" && \
echo "━━━ A3. ALL LISTENING PORTS ━━━" && \
sudo ss -tlnp 2>/dev/null | head -25 && echo "" && \
echo "━━━ A4. KEY PORTS CHECK ━━━" && \
ss -tlnp | grep -E "5432|6379|7474|7687|8000" || echo "Some ports not listening" && echo "" && \
echo "━━━ A5. DISK SPACE ━━━" && \
df -h / /opt/l9 2>/dev/null && echo "" && \
echo "━━━ A6. L9 INSTALLATION ━━━" && \
ls -la /opt/l9/ 2>/dev/null | head -20 || echo "/opt/l9 does not exist" && echo "" && \
echo "━━━ B1. CADDY STATUS ━━━" && \
sudo systemctl status caddy --no-pager 2>/dev/null | head -5 || echo "Caddy not installed" && echo "" && \
echo "━━━ B2. CADDY CONFIG ━━━" && \
cat /etc/caddy/Caddyfile 2>/dev/null | head -20 || echo "No Caddyfile found" && echo "" && \
echo "━━━ C1. DOCKER CONTAINERS ━━━" && \
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null && echo "" && \
echo "━━━ C2. DOCKER COMPOSE STATUS ━━━" && \
cd /opt/l9 && docker compose ps 2>/dev/null && echo "" && \
echo "━━━ C3. L9-API LOGS (last 40) ━━━" && \
docker logs l9-api --tail 40 2>/dev/null || echo "No l9-api container" && echo "" && \
echo "━━━ C4. L9-POSTGRES STATUS ━━━" && \
docker logs l9-postgres --tail 15 2>/dev/null || echo "No l9-postgres container" && echo "" && \
echo "━━━ C5. POSTGRES CONNECTION TEST ━━━" && \
docker exec l9-postgres pg_isready -U postgres 2>/dev/null || echo "PostgreSQL not ready" && echo "" && \
echo "━━━ C6. REDIS STATUS ━━━" && \
docker exec l9-redis redis-cli ping 2>/dev/null || echo "Redis not responding" && echo "" && \
echo "━━━ C7. NEO4J STATUS ━━━" && \
curl -s http://127.0.0.1:7474 2>/dev/null | head -1 || echo "Neo4j not responding" && echo "" && \
echo "━━━ D1. PYTHON/UVICORN PROCESSES ━━━" && \
ps aux | grep -E "python|uvicorn" | grep -v grep || echo "No Python/Uvicorn processes" && echo "" && \
echo "━━━ E1. HEALTH CHECK - LOCAL ━━━" && \
curl -fsS http://127.0.0.1:8000/health 2>&1 || echo "❌ API NOT RESPONDING" && echo "" && \
echo "━━━ E2. HEALTH CHECK - PUBLIC ━━━" && \
curl -kfsS https://l9.quantumaipartners.com/health 2>&1 || echo "❌ PUBLIC ENDPOINT FAIL" && echo "" && \
echo "━━━ F1. DOCKER-COMPOSE.YML (first 60 lines) ━━━" && \
head -60 /opt/l9/docker-compose.yml 2>/dev/null || echo "No docker-compose.yml" && echo "" && \
echo "━━━ F2. .ENV (SANITIZED) ━━━" && \
cat /opt/l9/.env 2>/dev/null | sed 's/=.*/=<REDACTED>/' | head -25 || echo "No .env" && echo "" && \
echo "╔════════════════════════════════════════════════════════════════╗" && \
echo "║               MRI DIAGNOSTIC COMPLETE                          ║" && \
echo "╚════════════════════════════════════════════════════════════════╝"