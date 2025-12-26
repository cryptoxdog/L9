cd /opt/l9

# Full system MRI
echo "=== GIT STATUS ===" && git log --oneline -5 && echo && git status && echo && \
echo "=== DOCKER COMPOSE CONFIG ===" && docker compose config | head -50 && echo && \
echo "=== RUNNING CONTAINERS ===" && docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" && echo && \
echo "=== POSTGRES DATABASE TEST ===" && docker exec l9-postgres psql -U postgres -d l9_memory -c "SELECT version();" && echo && \
echo "=== NETWORK CONNECTIVITY ===" && docker exec l9-api timeout 3 bash -c "</dev/tcp/l9-postgres/5432" && echo "Port 5432 OPEN" || echo "Port 5432 CLOSED" && echo && \
echo "=== API LOGS (last 30 lines) ===" && docker compose logs l9-api | tail -30
cd /opt/l9

echo "=== 1. FILESYSTEM server.py (repo root) ===" && \
ls -la app/server.py && \
head -50 app/server.py && \
echo "..." && echo "=== END FILESYSTEM ===" && echo && \

echo "=== 2. DOCKER CONTAINER server.py (inside running container) ===" && \
docker exec l9-api cat /app/server.py | head -50 && \
echo "..." && echo "=== END DOCKER ===" && echo && \

echo "=== 3. GIT STAGED/UNSTAGED DIFF ===" && \
git diff app/server.py && echo && \

echo "=== 4. GIT STATUS ===" && \
git status app/server.py && echo && \

echo "=== 5. LAST 3 COMMITS affecting server.py ===" && \
git log --oneline -3 -- app/server.py && echo && \

echo "=== 6. IMPORT LINE COMPARISON ===" && \
echo "Filesystem:" && grep "from app.settings" app/server.py && \
echo "Docker:" && docker exec l9-api grep "from app.settings" /app/server.py && \
echo && \

echo "=== 7. MD5 HASHES (to spot differences) ===" && \
echo "Filesystem:" && md5sum app/server.py && \
echo "Docker:" && docker exec l9-api md5sum /app/server.py

