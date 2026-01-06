"""
TOOL AUDIT WIRING GUIDE
========================

How to integrate memory audit logging into ToolGateway.
This enables automatic recording of all tool invocations to memory.

LOCATION: core/tools/gateway.py - ToolGateway class
"""

# ============================================================================
# STEP 1: Add imports at top of gateway.py
# ============================================================================

from core.memory.segments import MemorySegment
from core.memory.memory_api import MemoryAPI


# ============================================================================
# STEP 2: Modify ToolGateway.__init__() to accept memory_api
# ============================================================================

# BEFORE:
# def __init__(self, tool_registry, logger=None):
#     self.registry = tool_registry
#     self.logger = logger or logging.getLogger(__name__)

# AFTER:
# def __init__(self, tool_registry, memory_api=None, logger=None):
#     self.registry = tool_registry
#     self.memory_api = memory_api  # Optional memory subsystem
#     self.logger = logger or logging.getLogger(__name__)


# ============================================================================
# STEP 3: Add _log_to_memory_audit() method to ToolGateway class
# ============================================================================

async def _log_to_memory_audit(
    self,
    call_id: str,
    tool_id: str,
    agent_id: str,
    task_id: str,
    status: str,
    duration_ms: int,
    error_code: str = None
) -> None:
    """
    Auto-log tool call to memory audit segment.
    
    Called after every tool invocation (success or failure).
    Writes to memory substrate without blocking tool execution.
    
    Args:
        call_id: Unique call identifier
        tool_id: Which tool was invoked
        agent_id: Which agent invoked it
        task_id: Associated task
        status: "success" or "failure"
        duration_ms: Execution time
        error_code: Optional error code if failed
    """
    if not self.memory_api:
        return  # Memory not available
    
    try:
        # Write audit log to memory
        await self.memory_api.write(
            segment=MemorySegment.TOOL_AUDIT,
            content={
                "call_id": call_id,
                "tool_id": tool_id,
                "agent_id": agent_id,
                "task_id": task_id,
                "status": status,
                "duration_ms": duration_ms,
                "error_code": error_code,
                "timestamp": datetime.utcnow().isoformat()
            },
            agent_id=agent_id,
            ttl_hours=24  # Keep audit logs for 24 hours
        )
    
    except Exception as e:
        self.logger.warning(f"Failed to log tool audit: {e}")
        # Don't fail the tool call if audit logging fails


# ============================================================================
# STEP 4: Wire audit logging into invoke_tool() method
# ============================================================================

# In invoke_tool(), after tool execution, add:
#
#     try:
#         result = await self.registry.invoke(tool_id, args)
#         
#         # NEW: Log to memory audit
#         await self._log_to_memory_audit(
#             call_id=call_id,
#             tool_id=tool_id,
#             agent_id=context.agent_id,
#             task_id=context.task_id,
#             status="success",
#             duration_ms=duration_ms,
#             error_code=None
#         )
#         
#         return result
#     
#     except Exception as e:
#         # NEW: Log failure
#         await self._log_to_memory_audit(
#             call_id=call_id,
#             tool_id=tool_id,
#             agent_id=context.agent_id,
#             task_id=context.task_id,
#             status="failure",
#             duration_ms=duration_ms,
#             error_code=str(e)
#         )
#         raise


# ============================================================================
# STEP 5: Example usage - Initialize ToolGateway with memory
# ============================================================================

# In your initialization code (e.g., main.py or app startup):
#
#     from core.memory.bootstrap import initialize_memory_system
#     from core.memory.memory_api import MemoryAPI
#     from core.tools.gateway import ToolGateway
#
#     # Initialize memory
#     postgres_config = {
#         "host": "localhost",
#         "port": 5432,
#         "user": "postgres",
#         "password": "postgres",
#         "database": "l9_memory"
#     }
#     neo4j_config = {
#         "uri": "bolt://localhost:7687",
#         "user": "neo4j",
#         "password": "password"
#     }
#     redis_config = {
#         "host": "localhost",
#         "port": 6379
#     }
#
#     substrate, _, _, _ = await initialize_memory_system(
#         postgres_config, neo4j_config, redis_config
#     )
#
#     # Create MemoryAPI
#     memory_api = MemoryAPI(substrate)
#
#     # Initialize ToolGateway with memory
#     gateway = ToolGateway(registry=tool_registry, memory_api=memory_api)


# ============================================================================
# EXPECTED AUDIT LOG STRUCTURE
# ============================================================================

# Each tool call creates a packet in the tool_audit segment:
#
# {
#     "chunk_id": "tool_audit_2025_01_04_12_34_56_789",
#     "segment": "tool_audit",
#     "agent_id": "L",
#     "content": {
#         "call_id": "call_abc123def456",
#         "tool_id": "search_web",
#         "agent_id": "L",
#         "task_id": "task_xyz789",
#         "status": "success",
#         "duration_ms": 1234,
#         "error_code": None,
#         "timestamp": "2025-01-04T12:34:56.789Z"
#     },
#     "metadata": {"type": "tool_invocation"},
#     "timestamp": "2025-01-04T12:34:56.789Z",
#     "version": 1,
#     "expires_at": "2025-01-05T12:34:56.789Z"  # 24-hour TTL
# }


# ============================================================================
# QUERYING TOOL AUDIT LOGS
# ============================================================================

# Example: Search all tool calls for agent L in last 24 hours
#
#     from core.memory.segments import MemorySegment
#
#     logs = await memory_api.search(
#         query="search_web",  # Optional: filter by tool_id
#         segment=MemorySegment.TOOL_AUDIT,
#         agent_id="L",
#         limit=50
#     )
#
#     for log in logs:
#         print(f"{log['content']['tool_id']}: {log['content']['status']}")


# ============================================================================
# BENEFITS OF TOOL AUDIT MEMORY
# ============================================================================

# 1. Complete audit trail of all tool invocations
# 2. Track performance (duration_ms) over time
# 3. Identify failure patterns (error_code analysis)
# 4. Answer: "Which tools does agent X use most?"
# 5. Compliance: immutable, time-stamped logs
# 6. Analytics: query patterns, latency trends
# 7. Debugging: trace execution flow across tasks


print("Tool audit wiring guide loaded")
