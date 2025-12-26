# Exit venv (optional, but clean)
deactivate 2>/dev/null || true

# Go to docker directory
cd /opt/l9/docker

# Update .env first (add missing credentials)
cat >> /opt/l9/.env << 'EOF'

# === Redis ===
REDIS_URL=redis://127.0.0.1:6379/0
REDIS_ENABLED=true

# === Neo4j ===
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=neo4j

# === pgVector ===
PGVECTOR_ENABLED=true
VECTOR_DIMENSIONS=1536
EOF

# Stop old stuff
docker compose down -v 2>/dev/null || true

# BUILD (this will use Dockerfile, NOT venv)
docker compose build --no-cache 2>&1 | tail -150

# START
docker compose up -d

# WAIT
sleep 10

# CHECK LOGS
docker compose logs l9-api --tail 50

# TEST
curl http://127.0.0.1:8000/health
