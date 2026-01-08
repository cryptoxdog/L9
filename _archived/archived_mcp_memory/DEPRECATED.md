# ⚠️ DEPRECATED: MCP Memory Server

**Deprecated:** 2026-01-07  
**Reason:** MCP SSE endpoint was never implemented. Cursor memory access works via REST API.

## What This Was

A standalone MCP (Model Context Protocol) server that would have provided:
- `saveMemory` tool
- `searchMemory` tool  
- `getMemoryStats` tool
- `deleteExpiredMemories` tool

## Why It's Deprecated

1. **Never implemented**: The `/mcp/sse` endpoint was never added to the L9 API
2. **Duplication**: `cursor_memory_client.py` already provides full memory access via REST
3. **Unnecessary complexity**: Two memory interfaces = two things to maintain

## Current Memory Access

Use the REST-based memory client instead:

```bash
# Search memory
python3 .cursor-commands/cursor-memory/cursor_memory_client.py search "query"

# Write to memory
python3 .cursor-commands/cursor-memory/cursor_memory_client.py write "content" --kind lesson

# Check health
python3 .cursor-commands/cursor-memory/cursor_memory_client.py health

# Get stats
python3 .cursor-commands/cursor-memory/cursor_memory_client.py stats
```

## Files Cleaned Up

- `~/.cursor/mcp.json`: Removed `l9-memory` server entry
- `runtime/mcp_client.py`: Deprecated l9-memory registration code
- `core/worldmodel/service.py`: Commented out MCP-Memory external system

## Do Not Restore

This code should NOT be restored. If MCP integration is needed in the future, 
it should be a thin adapter over the existing REST API, not a separate server.

