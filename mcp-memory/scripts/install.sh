#!/bin/bash
#
# L9 MCP Memory Server - Installation Script
#
# Usage:
#   chmod +x mcp-memory/scripts/install.sh
#   ./mcp-memory/scripts/install.sh
#
# This script:
# 1. Creates l9memory database
# 2. Runs schema migration
# 3. Sets up systemd service
# 4. Starts the service

set -euo pipefail

echo "=== L9 MCP Memory Server Installation ==="

# Check required environment
if [ -z "${MEMORY_DSN:-}" ]; then
    echo "ERROR: MEMORY_DSN environment variable not set"
    echo "Example: export MEMORY_DSN='postgresql://user:pass@localhost:5432/l9memory'"
    exit 1
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "ERROR: OPENAI_API_KEY environment variable not set"
    exit 1
fi

if [ -z "${MCP_API_KEY:-}" ]; then
    echo "ERROR: MCP_API_KEY environment variable not set"
    echo "Generate one with: openssl rand -hex 32"
    exit 1
fi

# 1. Create database if needed
echo ""
echo "Step 1: Database setup"
DB_NAME=$(echo $MEMORY_DSN | sed -n 's/.*\/\([^?]*\).*/\1/p')
BASE_DSN=$(echo $MEMORY_DSN | sed "s/$DB_NAME/postgres/")

echo "  Creating database '$DB_NAME' if it doesn't exist..."
psql "$BASE_DSN" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    psql "$BASE_DSN" -c "CREATE DATABASE $DB_NAME"
echo "  ✓ Database ready"

# 2. Run schema migration
echo ""
echo "Step 2: Schema migration"
cd "$(dirname "$0")/../.."
python -m mcp-memory.scripts.migrate_db
echo "  ✓ Schema applied"

# 3. Test connection
echo ""
echo "Step 3: Connection test"
python -m mcp-memory.scripts.test_connection
echo "  ✓ Connection verified"

# 4. Setup systemd (optional, skip if not root)
if [ "$(id -u)" = "0" ]; then
    echo ""
    echo "Step 4: Systemd service setup"
    
    SERVICE_FILE="/etc/systemd/system/mcp-memory.service"
    
    if [ ! -f "$SERVICE_FILE" ]; then
        cat > "$SERVICE_FILE" << EOF
[Unit]
Description=L9 MCP Memory Server
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/l9
Environment=MEMORY_DSN=${MEMORY_DSN}
Environment=OPENAI_API_KEY=${OPENAI_API_KEY}
Environment=MCP_API_KEY=${MCP_API_KEY}
Environment=MCP_HOST=127.0.0.1
Environment=MCP_PORT=9001
ExecStart=/opt/l9/.venv/bin/uvicorn mcp-memory.main:app --host 127.0.0.1 --port 9001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
        systemctl daemon-reload
        systemctl enable mcp-memory
        echo "  ✓ Systemd service installed"
    else
        echo "  Service file already exists"
    fi
    
    # Start service
    systemctl restart mcp-memory
    sleep 2
    if systemctl is-active --quiet mcp-memory; then
        echo "  ✓ Service started successfully"
    else
        echo "  ✗ Service failed to start. Check: journalctl -u mcp-memory -f"
        exit 1
    fi
else
    echo ""
    echo "Step 4: Systemd (skipped - not running as root)"
    echo "  To run manually:"
    echo "    uvicorn mcp-memory.main:app --host 127.0.0.1 --port 9001"
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "MCP Memory Server running at: http://127.0.0.1:9001"
echo "Health check: curl http://127.0.0.1:9001/health"
echo ""
echo "Add to Cursor MCP config:"
echo '  "l9-memory": {'
echo '    "url": "http://127.0.0.1:9001",'
echo '    "headers": {'
echo "      \"Authorization\": \"Bearer \${MCP_API_KEY}\""
echo '    }'
echo '  }'

