#!/bin/bash
# =============================================================================
# L9 Memory Substrate - Startup Script
# Version: 1.0.0
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting L9 Memory Substrate..."
echo "   Project root: $PROJECT_ROOT"

# Check for .env file
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "⚠️  No .env file found. Creating from defaults..."
    cat > "$SCRIPT_DIR/.env" << 'EOF'
# L9 Memory Substrate Environment
POSTGRES_USER=l9_user
POSTGRES_PASSWORD=l9_secure_password
POSTGRES_DB=l9_memory
POSTGRES_PORT=5432
API_PORT=8080
EMBEDDING_MODEL=text-embedding-3-large
# Set OPENAI_API_KEY for real embeddings, leave empty for stub
OPENAI_API_KEY=
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
EOF
    echo "✅ Created .env file with defaults"
fi

# Navigate to deploy directory
cd "$SCRIPT_DIR"

# Start services
echo "📦 Starting Docker Compose services..."
docker compose -f docker-compose.memory_substrate_v1.0.0.yaml up -d

# Wait for services
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check health
echo "🔍 Checking service health..."
if curl -s http://localhost:${API_PORT:-8080}/health > /dev/null 2>&1; then
    echo "✅ Memory Substrate API is healthy"
else
    echo "⚠️  API not responding yet. Checking logs..."
    docker compose -f docker-compose.memory_substrate_v1.0.0.yaml logs --tail=20 memory_api
fi

echo ""
echo "==================================="
echo "L9 Memory Substrate Started"
echo "==================================="
echo "API Endpoint: http://localhost:${API_PORT:-8080}"
echo "Health Check: http://localhost:${API_PORT:-8080}/health"
echo "Packet API:   POST http://localhost:${API_PORT:-8080}/api/v1/memory/packet"
echo "Search API:   POST http://localhost:${API_PORT:-8080}/api/v1/memory/semantic/search"
echo ""
echo "To stop: docker compose -f docker-compose.memory_substrate_v1.0.0.yaml down"
echo "==================================="

