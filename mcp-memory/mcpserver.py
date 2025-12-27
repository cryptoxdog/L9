from typing import Any, Dict, List

from pydantic import BaseModel


class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


def get_mcp_tools() -> List[MCPTool]:
    """
    Define all tools exposed over MCP to Cursor.
    """
    return [
        MCPTool(
            name="saveMemory",
            description="Save a memory to the database with automatic embedding and categorization",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The memory content to store",
                    },
                    "kind": {
                        "type": "string",
                        "enum": ["preference", "fact", "context", "error", "success"],
                        "description": "Type of memory",
                    },
                    "scope": {
                        "type": "string",
                        "enum": ["user", "project", "global"],
                        "description": "Memory scope",
                    },
                    "duration": {
                        "type": "string",
                        "enum": ["short", "medium", "long"],
                        "description": "Memory duration: short=1h, medium=24h, long=durable",
                    },
                    "userid": {
                        "type": "string",
                        "description": "User identifier",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags",
                    },
                    "importance": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Importance weight 0–1",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata",
                    },
                },
                "required": ["content", "kind", "duration", "userid"],
            },
        ),
        MCPTool(
            name="searchMemory",
            description="Search memories using semantic similarity vector search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to embed",
                    },
                    "userid": {
                        "type": "string",
                        "description": "User identifier for scoping search",
                    },
                    "scopes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["user", "project", "global"],
                        "description": "Memory scopes to search",
                    },
                    "kinds": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by memory kinds",
                    },
                    "topk": {
                        "type": "integer",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 50,
                        "description": "Number of results",
                    },
                    "threshold": {
                        "type": "number",
                        "default": 0.7,
                        "description": "Similarity threshold 0–1",
                    },
                    "duration": {
                        "type": "string",
                        "enum": ["short", "medium", "long", "all"],
                        "default": "all",
                        "description": "Which memory tables to search",
                    },
                },
                "required": ["query", "userid"],
            },
        ),
        MCPTool(
            name="getMemoryStats",
            description="Get statistics about stored memories",
            inputSchema={
                "type": "object",
                "properties": {
                    "userid": {
                        "type": "string",
                        "description": "User identifier (optional; omit for global stats)",
                    },
                    "duration": {
                        "type": "string",
                        "enum": ["short", "medium", "long", "all"],
                        "default": "all",
                    },
                },
                "required": [],
            },
        ),
        MCPTool(
            name="deleteExpiredMemories",
            description="Cleanup expired short and medium-term memories (admin only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "dryrun": {
                        "type": "boolean",
                        "default": True,
                        "description": "If true, only report what would be deleted",
                    }
                },
                "required": [],
            },
        ),
    ]


async def handle_tool_call(tool: MCPToolCall, userid: str) -> Dict[str, Any]:
    """
    Route MCP tool calls to appropriate handlers.
    """
    from .routes.memory import (
        save_memory,
        search_memory,
        get_memory_stats,
        delete_expired_memories,
    )

    if tool.name == "saveMemory":
        return await save_memory(
            userid=userid,
            content=tool.arguments.get("content", ""),
            kind=tool.arguments.get("kind", "context"),
            scope=tool.arguments.get("scope", "user"),
            duration=tool.arguments.get("duration", "long"),
            tags=tool.arguments.get("tags"),
            importance=tool.arguments.get("importance", 1.0),
            metadata=tool.arguments.get("metadata"),
        )
    if tool.name == "searchMemory":
        return await search_memory(
            userid=userid,
            query=tool.arguments.get("query", ""),
            scopes=tool.arguments.get("scopes") or ["user", "project", "global"],
            kinds=tool.arguments.get("kinds"),
            topk=tool.arguments.get("topk", 5),
            threshold=tool.arguments.get("threshold", 0.7),
            duration=tool.arguments.get("duration", "all"),
        )
    if tool.name == "getMemoryStats":
        return await get_memory_stats(
            userid=tool.arguments.get("userid"),
            duration=tool.arguments.get("duration", "all"),
        )
    if tool.name == "deleteExpiredMemories":
        return await delete_expired_memories(
            dryrun=tool.arguments.get("dryrun", True),
        )
    raise ValueError(f"Unknown tool {tool.name}")

