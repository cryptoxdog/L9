ss -tlnp | grep -E '9000|8000'
ps aux | grep ssh | grep -v grep

cd /opt/l9

# See top-level structure
ls -la

# See if any deploy-like directory exists
ls -la deploy* 2>/dev/null || echo "no deploy dir"

# Inspect docker-compose to confirm expected paths
grep -n 'dockerfile:' docker-compose.yml
docker compose logs --tail=50
docker ps -a

echo "=== PUBLIC IP ==="
curl -s ifconfig.me; echo

echo "=== DNS ==="
getent hosts l9.quantumaipartners.com

echo "=== BACKEND LISTEN ==="
sudo ss -lntp | grep :8000 || echo "NOT LISTENING"

echo "=== LOCAL HEALTH ==="
curl -fsS http://127.0.0.1:8000/health || echo "BACKEND FAIL"

echo "=== PUBLIC HEALTH ==="
curl -kfsS https://l9.quantumaipartners.com/health || echo "PUBLIC FAIL"

