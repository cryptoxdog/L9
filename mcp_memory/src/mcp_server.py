"""
MCP (Model Context Protocol) Server Implementation.
"""

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
    return [
        MCPTool(
            name="save_memory",
            description="Save a memory to the database with automatic embedding",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Memory content"},
                    "kind": {
                        "type": "string",
                        "enum": ["preference", "fact", "context", "error", "success"],
                    },
                    "scope": {"type": "string", "enum": ["user", "project", "global"]},
                    "duration": {"type": "string", "enum": ["short", "medium", "long"]},
                    "user_id": {"type": "string"},
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "kernel:identity",
                                "kernel:cognitive",
                                "kernel:behavioral",
                                "kernel:execution",
                                "kernel:safety",
                                "agent:l-cto",
                                "agent:codegen",
                                "memory:substrate",
                                "memory:packet",
                                "orchestration:routing",
                                "orchestration:planning",
                                "tool:registry",
                                "tool:approval",
                                "api:routes",
                                "api:webhook",
                                "infra:docker",
                                "infra:vps",
                                "infra:database",
                                "gmp:phase",
                                "gmp:audit",
                                "debug:error",
                                "debug:fix",
                                "igor:preference",
                                "igor:context"
                            ]
                        },
                        "description": "L9 hierarchical memory categories (domain:specificity)"
                    },
                    "importance": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["content", "kind", "duration", "user_id"],
            },
        ),
        MCPTool(
            name="search_memory",
            description="Search memories using semantic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "user_id": {"type": "string"},
                    "scopes": {"type": "array", "items": {"type": "string"}},
                    "kinds": {"type": "array", "items": {"type": "string"}},
                    "top_k": {"type": "integer", "default": 5},
                    "threshold": {"type": "number", "default": 0.7},
                    "duration": {
                        "type": "string",
                        "enum": ["short", "medium", "long", "all"],
                    },
                },
                "required": ["query", "user_id"],
            },
        ),
        MCPTool(
            name="get_memory_stats",
            description="Get statistics about stored memories",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "duration": {
                        "type": "string",
                        "enum": ["short", "medium", "long", "all"],
                    },
                },
                "required": [],
            },
        ),
        MCPTool(
            name="delete_expired_memories",
            description="Cleanup expired memories",
            inputSchema={
                "type": "object",
                "properties": {"dry_run": {"type": "boolean", "default": True}},
                "required": [],
            },
        ),
        MCPTool(
            name="compound_memories",
            description="Merge highly similar memories",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "threshold": {"type": "number", "default": 0.92},
                },
                "required": ["user_id"],
            },
        ),
        MCPTool(
            name="apply_decay",
            description="Apply importance decay to unused memories",
            inputSchema={
                "type": "object",
                "properties": {"dry_run": {"type": "boolean", "default": True}},
                "required": [],
            },
        ),
        # =============================================================================
        # 10x Memory Upgrade Tools
        # =============================================================================
        MCPTool(
            name="get_context",
            description="Auto-retrieve relevant memories for context injection before a task. Returns top memories matching the task description plus recent context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "What you're about to work on - memories matching this will be retrieved",
                    },
                    "user_id": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5},
                    "include_recent": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include memories from last 24h session context",
                    },
                    "kinds": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by memory kinds (preference, fact, context, error, success)",
                    },
                },
                "required": ["task_description", "user_id"],
            },
        ),
        MCPTool(
            name="extract_session_learnings",
            description="Extract and store learnings from a completed session. Call at session end to capture what was learned.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "session_summary": {
                        "type": "string",
                        "description": "Brief summary of what happened this session",
                    },
                    "key_decisions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Key decisions made during session",
                    },
                    "errors_encountered": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Errors that occurred and how they were fixed",
                    },
                    "successes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "What worked well this session",
                    },
                },
                "required": ["user_id", "session_id", "session_summary"],
            },
        ),
        MCPTool(
            name="get_proactive_suggestions",
            description="Get proactive memory suggestions based on current context. Surfaces relevant past experiences, error fixes, and preferences.",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_context": {
                        "type": "string",
                        "description": "What you're currently working on",
                    },
                    "user_id": {"type": "string"},
                    "include_error_fixes": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include past error/fix pairs that might be relevant",
                    },
                    "include_preferences": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include user preferences relevant to this context",
                    },
                    "top_k": {"type": "integer", "default": 3},
                },
                "required": ["current_context", "user_id"],
            },
        ),
        MCPTool(
            name="query_temporal",
            description="Query memory changes over time. Answer 'what changed since X' or 'show timeline of Y'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "since": {
                        "type": "string",
                        "description": "ISO datetime - get changes since this time",
                    },
                    "until": {
                        "type": "string",
                        "description": "ISO datetime - get changes until this time",
                    },
                    "kinds": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by memory kinds",
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["changes", "timeline", "diff"],
                        "default": "changes",
                        "description": "Type of temporal query",
                    },
                },
                "required": ["user_id"],
            },
        ),
        MCPTool(
            name="save_memory_with_confidence",
            description="Save a memory with explicit confidence scoring and relationship linking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Memory content"},
                    "kind": {
                        "type": "string",
                        "enum": ["preference", "fact", "context", "error", "success", "learning", "decision"],
                    },
                    "scope": {"type": "string", "enum": ["user", "project", "global"]},
                    "duration": {"type": "string", "enum": ["short", "medium", "long"]},
                    "user_id": {"type": "string"},
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 1.0,
                        "description": "How confident are we in this memory (0-1)",
                    },
                    "source": {
                        "type": "string",
                        "default": "cursor",
                        "description": "Source of this memory (cursor, user, inferred)",
                    },
                    "related_memory_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "IDs of related memories to link",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "importance": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["content", "kind", "duration", "user_id"],
            },
        ),
    ]


async def handle_tool_call(tool: MCPToolCall, user_id: str, caller: Any = None) -> Dict[str, Any]:
    """Handle MCP tool call with caller-enforced governance.
    
    Args:
        tool: The tool call request
        user_id: Shared user_id (L_CTO_USER_ID)
        caller: CallerIdentity with caller_id, creator, source (L or C)
    
    See: mcp_memory/memory-setup-instructions.md for governance spec.
    """
    # Extract caller metadata for enforcement
    caller_id = caller.caller_id if caller else "unknown"
    creator = caller.creator if caller else "unknown"
    source = caller.source if caller else "unknown"
    
    if tool.name == "save_memory":
        from src.routes.memory import save_memory_handler

        return await save_memory_handler(
            user_id=user_id,
            content=tool.arguments.get("content"),
            kind=tool.arguments.get("kind"),
            scope=tool.arguments.get("scope", "user"),
            duration=tool.arguments.get("duration"),
            tags=tool.arguments.get("tags", []),
            importance=tool.arguments.get("importance", 1.0),
            caller_id=caller_id,
            creator=creator,
            source=source,
        )
    elif tool.name == "search_memory":
        from src.routes.memory import search_memory_handler

        return await search_memory_handler(
            user_id=user_id,
            query=tool.arguments.get("query"),
            scopes=tool.arguments.get("scopes", ["user", "project", "global"]),
            kinds=tool.arguments.get("kinds"),
            top_k=tool.arguments.get("top_k", 5),
            threshold=tool.arguments.get("threshold", 0.7),
            duration=tool.arguments.get("duration", "all"),
        )
    elif tool.name == "get_memory_stats":
        from src.routes.memory import get_memory_stats

        return await get_memory_stats(
            user_id=tool.arguments.get("user_id"),
            duration=tool.arguments.get("duration", "all"),
        )
    elif tool.name == "delete_expired_memories":
        from src.routes.memory import delete_expired_memories

        return await delete_expired_memories(
            dry_run=tool.arguments.get("dry_run", True)
        )
    elif tool.name == "compound_memories":
        from src.routes.memory import compound_similar_memories

        return await compound_similar_memories(
            user_id=tool.arguments.get("user_id"),
            threshold=tool.arguments.get("threshold", 0.92),
        )
    elif tool.name == "apply_decay":
        from src.routes.memory import apply_importance_decay

        return await apply_importance_decay(dry_run=tool.arguments.get("dry_run", True))
    # =============================================================================
    # 10x Memory Upgrade Tool Handlers
    # =============================================================================
    elif tool.name == "get_context":
        from src.routes.memory import get_context_injection

        return await get_context_injection(
            task_description=tool.arguments.get("task_description"),
            user_id=user_id,
            top_k=tool.arguments.get("top_k", 5),
            include_recent=tool.arguments.get("include_recent", True),
            kinds=tool.arguments.get("kinds"),
        )
    elif tool.name == "extract_session_learnings":
        from src.routes.memory import extract_session_learnings

        return await extract_session_learnings(
            user_id=user_id,
            session_id=tool.arguments.get("session_id"),
            session_summary=tool.arguments.get("session_summary"),
            key_decisions=tool.arguments.get("key_decisions"),
            errors_encountered=tool.arguments.get("errors_encountered"),
            successes=tool.arguments.get("successes"),
        )
    elif tool.name == "get_proactive_suggestions":
        from src.routes.memory import get_proactive_suggestions

        return await get_proactive_suggestions(
            current_context=tool.arguments.get("current_context"),
            user_id=user_id,
            include_error_fixes=tool.arguments.get("include_error_fixes", True),
            include_preferences=tool.arguments.get("include_preferences", True),
            top_k=tool.arguments.get("top_k", 3),
        )
    elif tool.name == "query_temporal":
        from src.routes.memory import query_temporal

        return await query_temporal(
            user_id=user_id,
            since=tool.arguments.get("since"),
            until=tool.arguments.get("until"),
            kinds=tool.arguments.get("kinds"),
            operation=tool.arguments.get("operation", "changes"),
        )
    elif tool.name == "save_memory_with_confidence":
        from src.routes.memory import save_memory_with_confidence

        return await save_memory_with_confidence(
            user_id=user_id,
            content=tool.arguments.get("content"),
            kind=tool.arguments.get("kind"),
            scope=tool.arguments.get("scope", "user"),
            duration=tool.arguments.get("duration"),
            confidence=tool.arguments.get("confidence", 1.0),
            # Source is enforced server-side, not from client
            source=source,  # From caller identity, not payload
            related_memory_ids=tool.arguments.get("related_memory_ids"),
            tags=tool.arguments.get("tags", []),
            importance=tool.arguments.get("importance", 1.0),
            caller_id=caller_id,
            creator=creator,
        )
    else:
        raise ValueError(f"Unknown tool: {tool.name}")
