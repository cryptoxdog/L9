# L9 MCP Memory Server

A standalone MCP-compatible memory server with semantic search capabilities using PostgreSQL + pgvector.

## Overview

The MCP Memory Server provides persistent memory storage for L-CTO and other L9 agents with:

- **Three-tier memory**: short-term (1h), medium-term (24h), long-term (persistent)
- **Semantic search**: Vector similarity search using OpenAI embeddings + pgvector
- **MCP protocol**: Compatible with Cursor and other MCP clients
- **Audit logging**: All operations logged for governance compliance

## Quick Start

### 1. Prerequisites

- PostgreSQL 15+ with pgvector extension
- Python 3.11+
- OpenAI API key

### 2. Installation

```bash
# From L9 root directory
cd /opt/l9

# Install dependencies
pip install -r mcp-memory/requirements-mcp.txt

# Configure environment
cp mcp-memory/.env.example mcp-memory/.env
# Edit .env with your credentials

# Create database and schema
createdb l9memory
python -m mcp-memory.scripts.migrate_db

# Verify setup
python -m mcp-memory.scripts.test_connection
```

### 3. Run

```bash
# Development
uvicorn mcp-memory.main:app --host 127.0.0.1 --port 9001 --reload

# Production (systemd)
sudo cp mcp-memory/mcp-memory.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mcp-memory
sudo systemctl start mcp-memory
```

## API Endpoints

### Health Check

```bash
curl http://127.0.0.1:9001/health
```

### MCP Protocol

```bash
# List tools
curl -H "Authorization: Bearer $MCP_API_KEY" http://127.0.0.1:9001/mcp/tools

# Save memory
curl -X POST http://127.0.0.1:9001/mcp/call \
  -H "Authorization: Bearer $MCP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "saveMemory",
    "arguments": {
      "content": "User prefers dark mode",
      "kind": "preference",
      "scope": "user",
      "duration": "long",
      "userid": "igor"
    }
  }'

# Search memory
curl -X POST http://127.0.0.1:9001/mcp/call \
  -H "Authorization: Bearer $MCP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "searchMemory",
    "arguments": {
      "query": "UI preferences",
      "userid": "igor",
      "topk": 5
    }
  }'
```

### REST API

```bash
# Save memory
curl -X POST http://127.0.0.1:9001/memory/save \
  -H "Content-Type: application/json" \
  -d '{
    "content": "L9 uses Slack for messaging",
    "kind": "fact",
    "scope": "project",
    "duration": "long",
    "userid": "system"
  }'

# Search memory
curl -X POST http://127.0.0.1:9001/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "messaging integration",
    "userid": "system"
  }'

# Get stats
curl http://127.0.0.1:9001/memory/stats
```

## Cursor MCP Configuration

Add to your Cursor MCP config (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "l9-memory": {
      "url": "http://127.0.0.1:9001",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `saveMemory` | Store memory with auto-embedding |
| `searchMemory` | Semantic search across memories |
| `getMemoryStats` | Memory statistics |
| `deleteExpiredMemories` | Cleanup expired entries |

## Memory Kinds

- `preference` - User preferences and settings
- `fact` - Known facts and information
- `context` - Session/project context
- `error` - Error patterns and fixes
- `success` - Successful approaches

## Memory Scopes

- `user` - User-specific memories
- `project` - Project-scoped memories
- `global` - System-wide memories

## Architecture

```
mcp-memory/
├── __init__.py          # Package init
├── config.py            # Settings via pydantic-settings
├── db.py                # asyncpg connection pool
├── embeddings.py        # OpenAI embedding generation
├── models.py            # Pydantic request/response models
├── mcpserver.py         # MCP protocol handler
├── main.py              # FastAPI app entrypoint
├── routes/
│   ├── __init__.py      # Router aggregation
│   ├── health.py        # Health check endpoint
│   └── memory.py        # Memory CRUD + search
├── schema/
│   └── init.sql         # PostgreSQL schema
├── scripts/
│   ├── migrate_db.py    # Schema migration
│   ├── test_connection.py # Connection test
│   └── install.sh       # Full installation script
├── requirements-mcp.txt # Dependencies
├── .env.example         # Environment template
├── mcp-memory.service   # Systemd service file
└── README.md            # This file
```

## Database Schema

Three memory tables with vector indexes:

- `memory.shortterm` - Auto-expiring (1h default)
- `memory.mediumterm` - Auto-expiring (24h default)
- `memory.longterm` - Persistent with scope/tags

Plus `memory.auditlog` for operation tracking.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_DSN` | required | PostgreSQL connection string |
| `OPENAI_API_KEY` | required | OpenAI API key |
| `MCP_API_KEY` | required | Server authentication key |
| `MCP_HOST` | 127.0.0.1 | Bind address |
| `MCP_PORT` | 9001 | Bind port |
| `OPENAI_EMBED_MODEL` | text-embedding-3-small | Embedding model |
| `MEMORY_SHORTTERM_HOURS` | 1 | Short-term TTL |
| `MEMORY_MEDIUMTERM_HOURS` | 24 | Medium-term TTL |
| `VECTOR_SEARCH_THRESHOLD` | 0.7 | Minimum similarity |
| `VECTOR_SEARCH_TOP_K` | 10 | Max results |

## License

Part of L9 Secure AI OS. Internal use only.

