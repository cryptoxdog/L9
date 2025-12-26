#!/bin/bash
set -e

echo "╔═══════════════════════════════════════════╗"
echo "║      L9 FULL DIAGNOSTIC SUITE             ║"
echo "╚═══════════════════════════════════════════╝"

echo ""
echo "=== DOCKER COMPOSE SERVICES ==="
cd /opt/l9 && cat docker-compose.yml | grep "^  [a-z]" | awk '{print $1}' | tr -d ':'

ls -la /opt/l9/docker/ && \
ls -la /opt/l9/.env 2>/dev/null && echo "ENV exists" || echo "⚠️ NO .env found" && \
head -20 /opt/l9/docker-compose.yml 2>/dev/null || echo "Current docker-compose doesn't exist yet" && \
which docker && \
docker --version && \
sudo systemctl status docker --no-pager

echo ""
echo "=== PORT 5432 STATUS ==="
sudo ss -tlnp | grep 5432 || echo "Port 5432 free"

echo ""
echo "=== POSTGRESQL HOST SERVICE ==="
sudo systemctl status postgresql --no-pager | head -5

echo ""
echo "=== .ENV CHECK ==="
if [ -f /opt/l9/.env ]; then
  echo "✓ .env exists"
  grep "^DB" /opt/l9/.env | head -3
else
  echo "✗ .env missing"
fi

echo ""
echo "=== START L9-API ONLY ==="
cd /opt/l9 && sudo /usr/bin/docker compose up -d l9-api
sleep 8

echo ""
echo "=== CONTAINER LOG (last 30 lines) ==="
sudo /usr/bin/docker logs l9-api 2>&1 | tail -30

cd /opt/l9 \
&& sudo /usr/bin/docker exec -it l9-postgres psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'PgChangeNow123';" \
&& sudo sed -i "s#^MEMORY_DSN=.*#MEMORY_DSN=postgresql://postgres:PgChangeNow123@127.0.0.1:5432/l9memory#" /opt/l9.env \
&& grep '^MEMORY_DSN' /opt/l9.env \
&& sudo /usr/bin/docker compose down \
&& sudo /usr/bin/docker compose up -d \
&& sleep 30 \
&& sudo /usr/bin/docker compose ps \
&& sudo /usr/bin/docker logs l9-api --tail 40 \
&& echo "" \
&& curl -sS 'http://127.0.0.1:8000/health' || echo 'API not up'

echo "=== STEP 1: Verify Dockerfile change ===" && \
sudo grep "CMD" /opt/l9/docker/Dockerfile && \
echo "" && \
echo "=== STEP 2: Docker compose down ===" && \
sudo docker compose -f /opt/l9/docker-compose.yml down && \
echo "" && \
echo "=== STEP 3: Rebuild (no cache) ===" && \
sudo docker compose -f /opt/l9/docker-compose.yml build --no-cache && \
echo "" && \
echo "=== STEP 4: Start services ===" && \
sudo docker compose -f /opt/l9/docker-compose.yml up -d && \
sleep 30 && \
echo "" && \
echo "=== STEP 5: Container status ===" && \
sudo docker compose -f /opt/l9/docker-compose.yml ps && \
echo "" && \
echo "=== STEP 6: Health check ===" && \
curl -sS http://127.0.0.1:8000/health && echo "" && \
echo "" && \
echo "=== STEP 7: API logs (last 30 lines) ===" && \
sudo docker compose -f /opt/l9/docker-compose.yml logs l9-api --tail=30
sudo docker compose logs l9-api --tail=80

echo ""
echo "=== STOP & CLEAN ALL L9 CONTAINERS ==="
sudo /usr/bin/docker compose -f /opt/l9/docker-compose.yml down 2>/dev/null || true