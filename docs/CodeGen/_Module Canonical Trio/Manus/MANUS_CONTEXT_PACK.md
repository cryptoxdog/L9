# MANUS CONTEXT PACK

> **Purpose**: Canonical L9 codebase reference for generating accurate Module Specs  
> **Version**: 1.0.0  
> **Last Updated**: 2025-12-16  
> **Related**: See `L9_IDEMPOTENCY_SSOT.md` in this folder for idempotency patterns

---

## Table of Contents

1. [Core Agent Schemas](#1-core-agent-schemas) — `AgentTask`, `ExecutionResult`, `ToolBinding`
2. [Agent Executor](#2-agent-executor) — Protocol definitions, execution loop
3. [Substrate Models](#3-substrate-models) — `PacketEnvelope`, DTOs, reasoning blocks
4. [Packet Envelope Schema](#4-packet-envelope-schema) — Immutable packet with `frozen=True`
5. [Governance Schemas](#5-governance-schemas) — `Policy`, `EvaluationRequest`, `EvaluationResult`
6. [Governance Engine](#6-governance-engine) — Policy evaluation, deny-by-default
7. [Tool Registry Adapter](#7-tool-registry-adapter) — `ExecutorToolRegistry`, dispatch
8. [Config Settings](#8-config-settings) — Pydantic settings pattern
9. [Module Spec Template](#9-module-spec-template) — v2.1.0 YAML format

---

## 1. Core Agent Schemas

**File**: `core/agents/schemas.py`

```python
"""
L9 Core Agents - Schemas
========================

Pydantic schemas for agent tasks, configurations, and execution state.

Defines:
- AgentTask: Work to be done by an agent
- AgentConfig: Configuration for an agent instance
- AIOSResult: Result from AIOS reasoning call
- ExecutorState: State machine states for executor loop
- ToolCallRequest: Request to dispatch a tool call
- ToolCallResult: Result from a tool call

Version: 1.0.0
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4, uuid5, NAMESPACE_DNS

from pydantic import BaseModel, Field


# =============================================================================
# Constants
# =============================================================================

AGENT_EXECUTOR_NAMESPACE = uuid5(NAMESPACE_DNS, "agent.executor.l9.internal")


# =============================================================================
# Enums
# =============================================================================

class ExecutorState(str, Enum):
    """State machine states for the executor loop."""
    INITIALIZING = "initializing"
    REASONING = "reasoning"
    TOOL_USE = "tool_use"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


class TaskKind(str, Enum):
    """Kind of agent task."""
    QUERY = "query"
    COMMAND = "command"
    RESEARCH = "research"
    EXECUTION = "execution"
    CONVERSATION = "conversation"


# =============================================================================
# Agent Task
# =============================================================================

class AgentTask(BaseModel):
    """
    Defines the work to be done by an agent.
    
    Contains the target agent, context, payload, and execution parameters.
    
    Attributes:
        id: Unique task identifier
        kind: Type of task for routing
        agent_id: Target agent identifier (e.g., "l9-standard-v1")
        source_id: Source that created this task
        thread_identifier: Logical thread for conversation grouping
        payload: Task-specific data
        context: Additional context for execution
        created_at: Task creation timestamp
        timeout_ms: Execution timeout in milliseconds
        max_iterations: Maximum reasoning iterations allowed
    """
    id: UUID = Field(default_factory=uuid4, description="Unique task identifier")
    kind: TaskKind = Field(default=TaskKind.QUERY, description="Task kind for routing")
    agent_id: str = Field(..., description="Target agent identifier")
    source_id: str = Field(default="system", description="Source that created this task")
    thread_identifier: Optional[str] = Field(None, description="Thread identifier for grouping")
    payload: dict[str, Any] = Field(default_factory=dict, description="Task-specific data")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional execution context")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    timeout_ms: int = Field(default=120000, ge=1000, description="Execution timeout (ms)")
    max_iterations: int = Field(default=10, ge=1, le=100, description="Max reasoning iterations")
    
    model_config = {"extra": "forbid"}
    
    def get_thread_id(self) -> UUID:
        """
        Generate deterministic thread UUID from stable thread identity.
        
        Uses UUIDv5 with namespace and source_id + thread_identifier.
        Thread UUID is NOT derived from task ID to ensure thread stability.
        """
        identity = f"{self.source_id}:{self.thread_identifier or 'default'}"
        return uuid5(AGENT_EXECUTOR_NAMESPACE, identity)
    
    def get_dedupe_key(self) -> str:
        """Get deduplication key for idempotency checking."""
        return str(self.id)


# =============================================================================
# Agent Config
# =============================================================================

class ToolBinding(BaseModel):
    """
    A tool bound to an agent instance.
    
    Identity: tool_id is the SOLE canonical identity.
    display_name is for UI/logs only - never used for lookup, dispatch, or binding.
    """
    tool_id: str = Field(..., description="Canonical tool identity (used for all lookups/dispatch)")
    display_name: Optional[str] = Field(None, description="Human-readable name for UI/logs only")
    description: Optional[str] = Field(None, description="Tool description")
    input_schema: dict[str, Any] = Field(default_factory=dict, description="JSON Schema for tool input parameters")
    enabled: bool = Field(default=True, description="Whether tool is enabled for this binding")


class AgentConfig(BaseModel):
    """
    Configuration for an agent instance.
    
    Includes the agent's identity, personality reference, and bound toolset.
    
    Attributes:
        agent_id: Unique agent identifier
        personality_id: Reference to agent personality/prompt definition
        model: LLM model to use
        temperature: LLM temperature
        max_tokens: Max response tokens
        tools: List of tools bound to this agent
        system_prompt: Optional system prompt override
        metadata: Additional configuration metadata
    """
    agent_id: str = Field(..., description="Unique agent identifier")
    personality_id: str = Field(default="l9-standard-v1", description="Personality reference")
    model: str = Field(default="gpt-4o", description="LLM model")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=4000, ge=100, le=128000, description="Max response tokens")
    tools: list[ToolBinding] = Field(default_factory=list, description="Bound tools")
    system_prompt: Optional[str] = Field(None, description="System prompt override")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {"extra": "forbid"}


# =============================================================================
# Tool Call Types
# =============================================================================

class ToolCallRequest(BaseModel):
    """
    Request to dispatch a tool call.
    
    Generated by AIOS when reasoning produces a tool invocation.
    Identity: tool_id is the canonical tool identity - matches function.name in OpenAI schema.
    """
    call_id: UUID = Field(default_factory=uuid4, description="Unique call identifier")
    tool_id: str = Field(..., description="Canonical tool identity (must match function.name)")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for tool")
    task_id: UUID = Field(..., description="Parent task ID")
    iteration: int = Field(..., ge=0, description="Iteration number in execution loop")
    
    model_config = {"extra": "forbid"}


class ToolCallResult(BaseModel):
    """
    Result from a tool call.
    
    Returned by tool registry after dispatching.
    Identity: tool_id is tagged on result for context re-entry.
    """
    call_id: UUID = Field(..., description="Call identifier from request")
    tool_id: str = Field(..., description="Canonical tool identity (for context re-entry)")
    success: bool = Field(..., description="Whether call succeeded")
    result: Any = Field(None, description="Tool result if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    duration_ms: int = Field(default=0, ge=0, description="Execution duration")
    
    model_config = {"extra": "forbid"}


# =============================================================================
# AIOS Result
# =============================================================================

class AIOSResultType(str, Enum):
    """Type of AIOS result."""
    RESPONSE = "response"
    TOOL_CALL = "tool_call"
    ERROR = "error"


class AIOSResult(BaseModel):
    """
    Result from AIOS reasoning call.
    
    Contains either a final response or a tool call request.
    
    Attributes:
        result_type: Type of result (response, tool_call, error)
        content: Response content if result_type is RESPONSE
        tool_call: Tool call request if result_type is TOOL_CALL
        error: Error message if result_type is ERROR
        tokens_used: Total tokens used in this call
        finish_reason: LLM finish reason
    """
    result_type: AIOSResultType = Field(..., description="Type of result")
    content: Optional[str] = Field(None, description="Response content")
    tool_call: Optional[ToolCallRequest] = Field(None, description="Tool call if requested")
    error: Optional[str] = Field(None, description="Error message")
    tokens_used: int = Field(default=0, ge=0, description="Tokens used")
    finish_reason: Optional[str] = Field(None, description="LLM finish reason")
    
    model_config = {"extra": "forbid"}
    
    @classmethod
    def response(cls, content: str, tokens_used: int = 0) -> "AIOSResult":
        """Create a response result."""
        return cls(
            result_type=AIOSResultType.RESPONSE,
            content=content,
            tokens_used=tokens_used,
            finish_reason="stop",
        )
    
    @classmethod
    def tool_request(cls, tool_call: ToolCallRequest, tokens_used: int = 0) -> "AIOSResult":
        """Create a tool call result."""
        return cls(
            result_type=AIOSResultType.TOOL_CALL,
            tool_call=tool_call,
            tokens_used=tokens_used,
            finish_reason="tool_calls",
        )
    
    @classmethod
    def error_result(cls, error: str) -> "AIOSResult":
        """Create an error result."""
        return cls(
            result_type=AIOSResultType.ERROR,
            error=error,
        )


# =============================================================================
# Execution Result
# =============================================================================

class ExecutionResult(BaseModel):
    """
    Final result of agent task execution.
    
    Attributes:
        task_id: Task that was executed
        status: Final execution status
        result: Final response content
        iterations: Total iterations performed
        duration_ms: Total execution duration
        error: Error message if failed
        trace_id: Trace ID for debugging
    """
    task_id: UUID = Field(..., description="Task ID")
    status: str = Field(..., description="Final status: completed, failed, terminated")
    result: Optional[str] = Field(None, description="Final response content")
    iterations: int = Field(default=0, ge=0, description="Total iterations")
    duration_ms: int = Field(default=0, ge=0, description="Total duration")
    error: Optional[str] = Field(None, description="Error message if failed")
    trace_id: Optional[UUID] = Field(None, description="Trace ID")
    
    model_config = {"extra": "forbid"}


# =============================================================================
# Idempotency Response
# =============================================================================

class DuplicateTaskResponse(BaseModel):
    """
    Response when a duplicate task is detected.
    
    IDEMPOTENCY LIMITATION: Currently in-memory only.
    Duplicate detection is lost on executor restart.
    Substrate-backed idempotency planned for v1.2.
    """
    ok: bool = Field(default=True)
    status: str = Field(default="duplicate")
    task_id: UUID = Field(..., description="Original task ID")
    
    model_config = {"extra": "forbid"}


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Enums
    "ExecutorState",
    "TaskKind",
    "AIOSResultType",
    # Models
    "AgentTask",
    "AgentConfig",
    "ToolBinding",
    "ToolCallRequest",
    "ToolCallResult",
    "AIOSResult",
    "ExecutionResult",
    "DuplicateTaskResponse",
    # Constants
    "AGENT_EXECUTOR_NAMESPACE",
]
```

---

## 2. Agent Executor

**File**: `core/agents/executor.py`

```python
"""
L9 Core Agents - Agent Executor Service
========================================

The Agent Executor is the heart of the agentic system, orchestrating agent
instantiation, tool binding, and the execution loop.

Key responsibilities:
- Instantiate agents based on registered configurations
- Bind governance-approved tools to agent instances
- Run the execution loop (reasoning <-> tool_use state machine)
- Dispatch tool calls through the tool registry
- Store reasoning traces and results via memory substrate

This module does NOT:
- Define agent personalities or core reasoning (AIOS does that)
- Approve or deny tool usage (Governance Engine does that)
- Create new database tables

Version: 1.0.0
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Callable, Optional, Protocol
from uuid import UUID

from core.agents.schemas import (
    AgentTask,
    AgentConfig,
    AIOSResult,
    AIOSResultType,
    ExecutorState,
    ExecutionResult,
    DuplicateTaskResponse,
    ToolCallRequest,
    ToolCallResult,
    ToolBinding,
)
from core.agents.agent_instance import AgentInstance
from memory.substrate_models import PacketEnvelopeIn, PacketMetadata

logger = logging.getLogger(__name__)


# =============================================================================
# Protocol Definitions (Interfaces)
# =============================================================================

class AIOSRuntime(Protocol):
    """Protocol for AIOS runtime interface."""
    
    async def execute_reasoning(
        self,
        context: dict[str, Any],
    ) -> AIOSResult:
        """
        Execute reasoning with the given context.
        
        Args:
            context: Context bundle from AgentInstance.assemble_context()
            
        Returns:
            AIOSResult with response or tool call
        """
        ...


class ToolRegistryProtocol(Protocol):
    """Protocol for tool registry interface."""
    
    async def dispatch_tool_call(
        self,
        tool_id: str,
        arguments: dict[str, Any],
        context: dict[str, Any],
    ) -> ToolCallResult:
        """
        Dispatch a tool call.
        
        Args:
            tool_id: Canonical tool identity
            arguments: Arguments for tool
            context: Execution context
            
        Returns:
            ToolCallResult with result or error (includes tool_id)
        """
        ...
    
    def get_approved_tools(
        self,
        agent_id: str,
        principal_id: str,
    ) -> list[ToolBinding]:
        """
        Get list of tools approved for an agent.
        
        Args:
            agent_id: Agent identifier
            principal_id: Principal requesting tools
            
        Returns:
            List of approved tool bindings
        """
        ...


class SubstrateServiceProtocol(Protocol):
    """Protocol for memory substrate service interface."""
    
    async def write_packet(
        self,
        packet_in: PacketEnvelopeIn,
    ) -> Any:
        """
        Write a packet to the substrate.
        
        Args:
            packet_in: Packet envelope to write
            
        Returns:
            Write result
        """
        ...
    
    async def search_packets(
        self,
        thread_id: UUID,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Search packets by thread ID.
        
        Args:
            thread_id: Thread identifier
            limit: Max results
            
        Returns:
            List of matching packets
        """
        ...


class AgentRegistryProtocol(Protocol):
    """Protocol for agent registry interface."""
    
    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """
        Get configuration for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            AgentConfig or None if not found
        """
        ...
    
    def agent_exists(self, agent_id: str) -> bool:
        """Check if an agent is registered."""
        ...


# =============================================================================
# Agent Executor Service
# =============================================================================

class AgentExecutorService:
    """
    Service for executing agent tasks.
    
    Orchestrates the agent execution loop:
    1. Validate and instantiate agent
    2. Bind approved tools
    3. Run reasoning loop until completion or max iterations
    4. Store traces and results
    
    All dependencies are injected - no singletons.
    """
    
    def __init__(
        self,
        aios_runtime: AIOSRuntime,
        tool_registry: ToolRegistryProtocol,
        substrate_service: SubstrateServiceProtocol,
        agent_registry: AgentRegistryProtocol,
        default_agent_id: Optional[str] = None,
        max_iterations: Optional[int] = None,
    ):
        """
        Initialize the executor service.
        
        Args:
            aios_runtime: AIOS runtime for reasoning
            tool_registry: Tool registry for dispatching
            substrate_service: Memory substrate for persistence
            agent_registry: Agent registry for configs
            default_agent_id: Default agent ID (from env if not provided)
            max_iterations: Max iterations (from env if not provided)
        """
        self._aios_runtime = aios_runtime
        self._tool_registry = tool_registry
        self._substrate_service = substrate_service
        self._agent_registry = agent_registry
        
        # Configuration from env vars (read at init, not import time)
        self._default_agent_id = default_agent_id or os.getenv(
            "DEFAULT_AGENT_ID", "l9-standard-v1"
        )
        self._max_iterations = max_iterations or int(
            os.getenv("AGENT_MAX_ITERATIONS", "10")
        )
        
        # Idempotency cache
        # LIMITATION: In-memory only - cleared on process restart.
        # NOT durable: If executor restarts, duplicate tasks will re-execute.
        # For substrate-backed idempotency, see roadmap v1.2.
        self._processed_tasks: dict[str, ExecutionResult] = {}
        
        logger.info(
            "agent.executor.init: default_agent_id=%s, max_iterations=%d",
            self._default_agent_id,
            self._max_iterations,
        )
    
    # =========================================================================
    # Public API
    # =========================================================================
    
    async def start_agent_task(
        self,
        task: AgentTask,
    ) -> ExecutionResult | DuplicateTaskResponse:
        """
        Start executing an agent task.
        
        This is the main entry point for task execution.
        
        Args:
            task: The task to execute
            
        Returns:
            ExecutionResult or DuplicateTaskResponse if duplicate
        """
        # ... (execution loop implementation)
        pass


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "AgentExecutorService",
    "AIOSRuntime",
    "ToolRegistryProtocol",
    "SubstrateServiceProtocol",
    "AgentRegistryProtocol",
]
```

---

## 3. Substrate Models

**File**: `memory/substrate_models.py`

```python
"""
L9 Memory Substrate - Pydantic Models
Version: 1.1.0

Defines PacketEnvelope, StructuredReasoningBlock, and all DTOs
for the memory substrate API.

Changelog v1.1.0:
- Added PacketLineage model for DAG-style packet relationships
- Added thread_id, lineage, tags, ttl to PacketEnvelope
- Updated PacketEnvelopeIn with new fields
- Updated PacketStoreRow with new DB columns
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# =============================================================================
# PacketEnvelope Models
# =============================================================================

class PacketConfidence(BaseModel):
    """Confidence score and rationale for a packet."""
    score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score 0-1")
    rationale: Optional[str] = Field(None, description="Explanation of confidence level")


class PacketProvenance(BaseModel):
    """Provenance information for packet traceability."""
    parent_packet: Optional[UUID] = Field(None, description="Parent packet ID if derived")
    source: Optional[str] = Field(None, description="Source system or agent")
    tool: Optional[str] = Field(None, description="Tool that generated this packet")


class PacketLineage(BaseModel):
    """
    Lineage information for packet genealogy tracking (v1.1.0).
    
    Enables tracing the full derivation path of a packet through
    the system, supporting multi-parent DAG relationships.
    """
    parent_ids: list[UUID] = Field(default_factory=list, description="Parent packet IDs (multi-parent DAG)")
    derivation_type: Optional[str] = Field(None, description="How derived: 'split', 'merge', 'transform', 'inference'")
    generation: int = Field(default=0, description="Generation number in lineage chain")
    root_packet_id: Optional[UUID] = Field(None, description="Original root packet if known")


class PacketMetadata(BaseModel):
    """Metadata attached to a packet envelope."""
    schema_version: Optional[str] = Field("1.0.0", description="Schema version")
    reasoning_mode: Optional[str] = Field(None, description="Reasoning mode used")
    agent: Optional[str] = Field(None, description="Agent identifier")
    domain: Optional[str] = Field("plastic_brokerage", description="Domain context")


class PacketEnvelope(BaseModel):
    """
    Canonical envelope for substrate writes and reasoning traces.
    
    This is the core data structure for all agent events, memory writes,
    and reasoning traces flowing through the memory substrate.
    
    v1.1.0: Added thread_id, lineage, tags, ttl for enhanced
    threading, DAG-style lineage, labeling, and memory expiration.
    """
    packet_id: UUID = Field(default_factory=uuid4, description="UUID for this packet")
    packet_type: str = Field(..., description="Type: 'event', 'memory_write', 'reasoning_trace', 'insight', etc.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="ISO timestamp")
    payload: dict[str, Any] = Field(..., description="JSON payload to persist or reason over")
    metadata: Optional[PacketMetadata] = Field(default_factory=PacketMetadata)
    provenance: Optional[PacketProvenance] = Field(None)
    confidence: Optional[PacketConfidence] = Field(None)
    reasoning_block: Optional[dict[str, Any]] = Field(None, description="Optional StructuredReasoningBlock inline")
    
    # v1.1.0 additions (backward compatible - all optional)
    thread_id: Optional[UUID] = Field(None, description="Logical conversation/task thread identifier")
    lineage: Optional[PacketLineage] = Field(None, description="Lineage metadata for DAG-style derivation tracking")
    tags: list[str] = Field(default_factory=list, description="Lightweight labels for filtering and retrieval")
    ttl: Optional[datetime] = Field(None, description="Optional expiry timestamp for memory hygiene/GC")


class PacketEnvelopeIn(BaseModel):
    """
    Input model for packet submission (allows partial fields).
    packet_id and timestamp are auto-generated if not provided.
    
    v1.1.0: Added thread_id, lineage, tags, ttl support.
    """
    packet_id: Optional[UUID] = Field(None, description="UUID for this packet (auto-generated if omitted)")
    packet_type: str = Field(..., description="Type: 'event', 'memory_write', 'reasoning_trace', 'insight', etc.")
    timestamp: Optional[datetime] = Field(None, description="ISO timestamp (auto-generated if omitted)")
    payload: dict[str, Any] = Field(..., description="JSON payload to persist or reason over")
    metadata: Optional[PacketMetadata] = Field(None)
    provenance: Optional[PacketProvenance] = Field(None)
    confidence: Optional[PacketConfidence] = Field(None)
    reasoning_block: Optional[dict[str, Any]] = Field(None)
    
    # v1.1.0 additions
    thread_id: Optional[UUID] = Field(None, description="Thread UUID for conversation/session linking")
    lineage: Optional[PacketLineage] = Field(None, description="Packet derivation lineage")
    tags: Optional[list[str]] = Field(None, description="Flexible tags for filtering")
    ttl: Optional[datetime] = Field(None, description="Optional expiration timestamp")

    def to_envelope(self) -> PacketEnvelope:
        """Convert input to full PacketEnvelope with defaults."""
        return PacketEnvelope(
            packet_id=self.packet_id or uuid4(),
            packet_type=self.packet_type,
            timestamp=self.timestamp or datetime.utcnow(),
            payload=self.payload,
            metadata=self.metadata or PacketMetadata(),
            provenance=self.provenance,
            confidence=self.confidence,
            reasoning_block=self.reasoning_block,
            thread_id=self.thread_id,
            lineage=self.lineage,
            tags=self.tags or [],
            ttl=self.ttl,
        )


# =============================================================================
# Database Row DTOs
# =============================================================================

class PacketStoreRow(BaseModel):
    """DTO for packet_store table (v1.1.0 extended)."""
    packet_id: UUID
    packet_type: str
    envelope: dict[str, Any]
    timestamp: datetime
    routing: Optional[dict[str, Any]]
    provenance: Optional[dict[str, Any]]
    # v1.1.0 additions - match DB columns
    thread_id: Optional[UUID] = None
    parent_ids: list[UUID] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    ttl: Optional[datetime] = None


class KnowledgeFact(BaseModel):
    """
    A knowledge fact extracted from packet processing.
    
    Represents subject-predicate-object triples with confidence
    for populating the knowledge graph / world model.
    """
    fact_id: UUID = Field(default_factory=uuid4, description="UUID for this fact")
    subject: str = Field(..., description="Entity or concept being described")
    predicate: str = Field(..., description="Relationship or attribute type")
    object: Any = Field(..., description="Value, entity, or structured data")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Extraction confidence")
    source_packet: Optional[UUID] = Field(None, description="Originating packet ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 4. Packet Envelope Schema

**File**: `core/schemas/packet_envelope.py`

```python
"""
L9 Packet Envelope Schema

Generated from: Memory.yaml v1.0.1
Module ID: memory.packet_envelope.v1.0.1
Status: aligned_with_repo

Canonical event container used by the Memory Substrate.
Matches the v1.0 repository implementation in substrate_models.py.
Immutable once written.

Contracts:
- PacketEnvelope must be immutable once written.
- Embedding vectors are stored in a separate semantic_memory table (not inline).
- payload is arbitrary JSON and not variant-typed in v1.0.1.
- Only packet_type, payload, timestamp are guaranteed.
"""

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# =============================================================================
# Enums (required by research_factory_nodes)
# =============================================================================

class PacketKind(str, Enum):
    """Kind of packet for routing/classification."""
    EVENT = "event"
    INSIGHT = "insight"
    RESULT = "result"
    ERROR = "error"
    COMMAND = "command"
    QUERY = "query"


class PacketEnvelope(BaseModel):
    """
    Canonical event container used by the Memory Substrate.
    
    Matches the v1.0 repository implementation in substrate_models.py.
    IMMUTABLE once written.
    
    Contracts:
    - PacketEnvelope must be immutable once written.
    - Embedding vectors are stored in a separate semantic_memory table (not inline).
    - payload is arbitrary JSON and not variant-typed in v1.0.1.
    - Only packet_type, payload, timestamp are guaranteed.
    """
    # Primary Key
    packet_id: UUID = Field(default_factory=uuid4, description="Unique packet identifier")
    
    # Required Fields
    packet_type: str = Field(
        ..., 
        min_length=1,
        description="Semantic category of the packet (e.g., event, message)"
    )
    payload: dict[str, Any] = Field(
        ..., 
        description="Flexible JSON-like structure. Repository does not enforce shape."
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp (generated automatically)"
    )
    
    # Optional Fields
    metadata: Optional[PacketMetadata] = Field(None)
    provenance: Optional[PacketProvenance] = Field(None)
    confidence: Optional[PacketConfidence] = Field(None)

    model_config = {
        "frozen": True,  # IMMUTABILITY ENFORCED
        "validate_assignment": True,
        "extra": "forbid",
    }

    def with_update(self, **updates) -> "PacketEnvelope":
        """
        Create a new PacketEnvelope with updates, linking to this as parent.
        
        This is the ONLY way to "modify" a packet (immutability preserved).
        """
        new_provenance = PacketProvenance(
            parent_packet=self.packet_id,
            source_agent=self.provenance.source_agent if self.provenance else None
        )
        return self.model_copy(update={
            "packet_id": uuid4(),
            "provenance": new_provenance,
            "timestamp": datetime.utcnow(),
            **updates
        })
```

---

## 5. Governance Schemas

**File**: `core/governance/schemas.py`

```python
"""
L9 Core Governance - Schemas
============================

Pydantic models for governance policies and evaluation.

Defines:
- PolicyEffect: allow/deny effect
- ConditionOperator: comparison operators for conditions
- PolicyCondition: conditional evaluation clause
- Policy: complete policy definition
- EvaluationRequest: request for policy evaluation
- EvaluationResult: result of policy evaluation

Version: 1.0.0
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class PolicyEffect(str, Enum):
    """Effect of a policy when matched."""
    ALLOW = "allow"
    DENY = "deny"


class ConditionOperator(str, Enum):
    """Operators for policy conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


# =============================================================================
# Policy
# =============================================================================

class Policy(BaseModel):
    """
    A governance policy definition.
    
    Policies define rules for allowing or denying actions.
    First-match wins by priority (lowest priority number wins).
    
    Attributes:
        id: Unique policy identifier
        name: Human-readable policy name
        description: Policy description
        effect: Allow or deny effect
        priority: Evaluation priority (lower = higher priority)
        actions: List of actions this policy applies to
        subjects: List of subjects (agents/users) this applies to
        resources: List of resources this applies to
        conditions: Additional conditions that must be met
        enabled: Whether this policy is active
    """
    id: str = Field(..., min_length=1, description="Unique policy identifier")
    name: str = Field(..., min_length=1, description="Policy name")
    description: str = Field(default="", description="Policy description")
    effect: PolicyEffect = Field(..., description="Allow or deny")
    priority: int = Field(default=100, ge=0, description="Priority (lower = higher)")
    actions: list[str] = Field(default_factory=lambda: ["*"], description="Actions this applies to")
    subjects: list[str] = Field(default_factory=lambda: ["*"], description="Subjects this applies to")
    resources: list[str] = Field(default_factory=lambda: ["*"], description="Resources this applies to")
    conditions: list[PolicyCondition] = Field(default_factory=list, description="Additional conditions")
    enabled: bool = Field(default=True, description="Whether policy is active")
    
    model_config = {"extra": "forbid"}


# =============================================================================
# Evaluation Request/Result
# =============================================================================

class EvaluationRequest(BaseModel):
    """
    Request for policy evaluation.
    
    Submitted by services (e.g., Tool Registry) to determine
    if an action should be allowed.
    """
    request_id: UUID = Field(default_factory=uuid4, description="Request identifier")
    action: str = Field(..., min_length=1, description="Action being requested")
    subject: str = Field(..., min_length=1, description="Entity making request")
    resource: str = Field(..., min_length=1, description="Target resource")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    correlation_id: Optional[UUID] = Field(None, description="Correlation ID for tracing")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    
    model_config = {"extra": "forbid"}


class EvaluationResult(BaseModel):
    """
    Result of policy evaluation.
    """
    request_id: UUID = Field(..., description="Original request ID")
    allowed: bool = Field(..., description="Whether action is allowed")
    effect: PolicyEffect = Field(..., description="Applied effect")
    policy_id: Optional[str] = Field(None, description="Matched policy ID")
    policy_name: Optional[str] = Field(None, description="Matched policy name")
    reason: str = Field(..., description="Decision reason")
    evaluated_at: datetime = Field(default_factory=datetime.utcnow, description="Evaluation timestamp")
    duration_ms: int = Field(default=0, ge=0, description="Evaluation duration")
    
    model_config = {"extra": "forbid"}
    
    @classmethod
    def allow(cls, request_id: UUID, policy: Policy, duration_ms: int = 0) -> "EvaluationResult":
        """Create an allow result."""
        return cls(
            request_id=request_id,
            allowed=True,
            effect=PolicyEffect.ALLOW,
            policy_id=policy.id,
            policy_name=policy.name,
            reason=f"Allowed by policy: {policy.name}",
            duration_ms=duration_ms,
        )
    
    @classmethod
    def deny(cls, request_id: UUID, policy: Optional[Policy] = None, 
             reason: Optional[str] = None, duration_ms: int = 0) -> "EvaluationResult":
        """Create a deny result."""
        if policy:
            return cls(
                request_id=request_id,
                allowed=False,
                effect=PolicyEffect.DENY,
                policy_id=policy.id,
                policy_name=policy.name,
                reason=reason or f"Denied by policy: {policy.name}",
                duration_ms=duration_ms,
            )
        return cls(
            request_id=request_id,
            allowed=False,
            effect=PolicyEffect.DENY,
            policy_id=None,
            policy_name=None,
            reason=reason or "Denied by default: no matching allow policy",
            duration_ms=duration_ms,
        )
```

---

## 6. Governance Engine

**File**: `core/governance/engine.py`

```python
"""
L9 Core Governance - Policy Engine
==================================

Stateless, deterministic policy evaluation engine.

Key responsibilities:
- Evaluate policy requests against loaded policies
- Enforce deny-by-default security posture
- Emit audit packets for all evaluations
- Support hot-reload of policies

This module does NOT:
- Store long-term state between evaluations
- Make external network calls
- Create database tables

Version: 1.0.0
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Protocol
from uuid import UUID

from core.governance.schemas import (
    Policy,
    PolicyEffect,
    EvaluationRequest,
    EvaluationResult,
)
from core.governance.loader import PolicyLoader, PolicyLoadError
from memory.substrate_models import PacketEnvelopeIn, PacketMetadata

logger = logging.getLogger(__name__)


class GovernanceEngineService:
    """
    Stateless policy evaluation engine.
    
    Evaluates requests against loaded policies using first-match-wins
    by priority. Enforces deny-by-default: if no policy matches, deny.
    
    The engine is purely a decision maker - it does not execute actions
    or modify state. Each evaluation is atomic and independent.
    """
    
    def __init__(
        self,
        policy_loader: PolicyLoader,
        substrate_service: Optional[SubstrateServiceProtocol] = None,
        emit_audit_packets: bool = True,
    ):
        """
        Initialize the governance engine.
        
        Args:
            policy_loader: Loaded policy loader instance
            substrate_service: Optional substrate for audit packets
            emit_audit_packets: Whether to emit audit packets
        """
        self._policy_loader = policy_loader
        self._substrate_service = substrate_service
        self._emit_audit = emit_audit_packets
        
        # Statistics
        self._evaluations_total = 0
        self._evaluations_allowed = 0
        self._evaluations_denied = 0
    
    async def evaluate_policy(self, request: EvaluationRequest) -> EvaluationResult:
        """
        Evaluate a policy request.
        
        This is the main entry point for policy evaluation.
        First-match-wins by priority. Deny-by-default if no match.
        
        Args:
            request: Evaluation request
            
        Returns:
            EvaluationResult with allow/deny decision
        """
        # ... implementation
        pass
    
    def evaluate_policy_sync(self, request: EvaluationRequest) -> EvaluationResult:
        """
        Synchronous policy evaluation (no audit packet).
        
        Use this for high-frequency evaluations where audit
        packets would be too expensive.
        """
        # ... implementation
        pass


# =============================================================================
# Factory Functions
# =============================================================================

def create_governance_engine(
    manifest_dir: Optional[str | Path] = None,
    preloaded_policies: Optional[list[Policy]] = None,
    substrate_service: Optional[SubstrateServiceProtocol] = None,
    emit_audit_packets: bool = True,
) -> GovernanceEngineService:
    """
    Factory function to create a GovernanceEngineService.
    """
    loader = PolicyLoader(
        manifest_dir=manifest_dir,
        preloaded_policies=preloaded_policies,
    )
    
    return GovernanceEngineService(
        policy_loader=loader,
        substrate_service=substrate_service,
        emit_audit_packets=emit_audit_packets,
    )
```

---

## 7. Tool Registry Adapter

**File**: `core/tools/registry_adapter.py`

```python
"""
L9 Core Tools - Registry Adapter
================================

Adapts the existing tool registry for use with AgentExecutorService.

This adapter:
- Implements ToolRegistryProtocol expected by executor
- Wraps the existing services.research.tools.tool_registry
- Converts ToolMetadata to ToolBinding
- Dispatches tool calls and returns ToolCallResult
- Enforces governance rules (deny-by-default for side effects)

Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Optional, Protocol
from uuid import UUID, uuid4

from core.agents.schemas import (
    ToolBinding,
    ToolCallResult,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Risk Levels
# =============================================================================

class RiskLevel:
    """Risk levels for tools."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Side-effect tools that require governance approval
SIDE_EFFECT_TOOLS = {
    "http_request",  # Can make external requests
}

# Tools with elevated risk
HIGH_RISK_TOOLS = {
    "shell_exec",
    "file_write",
    "database_write",
}


# =============================================================================
# Executor Tool Registry
# =============================================================================

class ExecutorToolRegistry:
    """
    Tool registry adapter for AgentExecutorService.
    
    Wraps the existing tool registry and provides:
    - ToolBinding conversion for agent context
    - Tool dispatch with result wrapping
    - Governance enforcement (side-effect denial)
    - Rate limiting checks
    """
    
    def __init__(
        self,
        base_registry: Optional[Any] = None,
        governance_enabled: bool = True,
    ):
        """
        Initialize the adapter.
        
        Args:
            base_registry: Existing ToolRegistry (auto-creates if None)
            governance_enabled: Whether to enforce governance
        """
        # ... initialization
        pass
    
    def get_approved_tools(
        self,
        agent_id: str,
        principal_id: str,
    ) -> list[ToolBinding]:
        """
        Get list of tools approved for an agent.
        
        Converts ToolMetadata to ToolBinding format expected by AgentInstance.
        Applies governance filtering (denies side-effect tools by default).
        
        Args:
            agent_id: Agent identifier
            principal_id: Principal requesting tools
        
        Returns:
            List of approved ToolBinding objects
        """
        # ... implementation
        pass
    
    async def dispatch_tool_call(
        self,
        tool_id: str,
        arguments: dict[str, Any],
        context: dict[str, Any],
    ) -> ToolCallResult:
        """
        Dispatch a tool call and return result.
        
        Uses tool_id as the sole identity for lookup and dispatch.
        
        Args:
            tool_id: Canonical tool identity
            arguments: Arguments for tool
            context: Execution context
        
        Returns:
            ToolCallResult with success/failure, result, and tool_id
        """
        # ... implementation
        pass
    
    def approve_tool(self, agent_id: str, tool_id: str) -> None:
        """Explicitly approve a tool for an agent."""
        pass
    
    def revoke_tool(self, agent_id: str, tool_id: str) -> None:
        """Revoke approval for a tool."""
        pass


# =============================================================================
# Factory Function
# =============================================================================

def create_executor_tool_registry(
    governance_enabled: bool = True,
    base_registry: Optional[Any] = None,
) -> ExecutorToolRegistry:
    """
    Factory function to create an ExecutorToolRegistry.
    """
    return ExecutorToolRegistry(
        base_registry=base_registry,
        governance_enabled=governance_enabled,
    )
```

---

## 8. Config Settings

**File**: `config/settings.py`

```python
"""
L9 Unified Integration Toggle Settings
Version: 1.0.0

Centralized configuration for all external integrations.
All integrations can be toggled on/off via environment variables.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class IntegrationSettings(BaseSettings):
    """
    Configuration for L9 external integrations.
    
    Environment variables:
    - SLACK_APP_ENABLED: Enable Slack integration (default: false)
    - MAC_AGENT_ENABLED: Enable Mac Agent integration (default: false)
    - EMAIL_ENABLED: Enable Email integration (default: false)
    - INBOX_PARSER_ENABLED: Enable Inbox Parser integration (default: false)
    - TWILIO_ENABLED: Enable Twilio integration (default: false)
    - WABA_ENABLED: Enable WABA integration (default: false)
    """
    
    # Integration toggles
    slack_app_enabled: bool = Field(
        default=False,
        alias="SLACK_APP_ENABLED",
        description="Enable Slack Events API integration"
    )
    
    mac_agent_enabled: bool = Field(
        default=False,
        alias="MAC_AGENT_ENABLED",
        description="Enable Mac Agent task execution"
    )
    
    email_enabled: bool = Field(
        default=False,
        alias="EMAIL_ENABLED",
        description="Enable Email integration"
    )
    
    # Storage configuration
    l9_data_root: str = Field(
        default=os.path.expanduser("~/.l9"),
        alias="L9_DATA_ROOT",
        description="Root directory for L9 data storage"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Singleton instance
_settings: IntegrationSettings | None = None


def get_integration_settings() -> IntegrationSettings:
    """Get or create integration settings singleton."""
    global _settings
    if _settings is None:
        _settings = IntegrationSettings()
    return _settings


def reset_integration_settings() -> None:
    """Reset settings (useful for testing)."""
    global _settings
    _settings = None


# Convenience accessor
settings = get_integration_settings()
```

---

## 9. Module Spec Template

**File**: `Module-Spec-v2.1.yaml`

```yaml
# ============================================================================
# L9 UNIVERSAL MODULE SPEC — v2.1.0
# ============================================================================
# Purpose: Define WHAT to build (P generates HOW)
# Audience: User fills → P consumes → C wires
# Part of Trio: [Spec] → [P-Prompt] → [C-Prompt]
# ============================================================================

# ============================================================================
# SECTION 1: MODULE IDENTITY (REQUIRED)
# ============================================================================
module:
  # REQUIRED — Unique identifier (lowercase, snake_case)
  # This is the CANONICAL tool_id. Use this everywhere (not tool_name).
  id: "{{module_id}}"
  
  # REQUIRED — Human-readable name (display only, not for code references)
  name: "{{Module Name}}"
  
  # REQUIRED — One-line purpose
  purpose: "{{Brief description of what this module does}}"
  
  # Fixed values (do not change)
  system: "L9"
  language: "python"
  runtime: "python>=3.11"
  owner: "Boss"

# ============================================================================
# SECTION 7: IDEMPOTENCY (REQUIRED)
# ============================================================================
idempotency:
  enabled: true  # or false
  
  # How to identify duplicate requests
  dedupe_key:
    primary: "{{event_id | message_id}}"
    fallback: "hash(payload)"
  
  # What to do on duplicate
  on_duplicate: "return {ok: true, dedupe: true}"
  
  # Thread identification
  thread_id:
    type: "UUIDv5"  # REQUIRED — deterministic
    namespace: "{{module}}.l9.internal"
    components:
      - "{{source_id}}"
      - "{{channel_id}}"
      - "{{thread_identifier}}"

# ============================================================================
# SECTION 11: MANDATORY STANDARDS (REQUIRED)
# ============================================================================
standards:

  # IDENTITY — Use tool_id, not tool_name
  identity:
    canonical_identifier: "tool_id"
    description: |
      Always use module.id (tool_id) as the canonical identifier in:
      - Log events (tool_id field)
      - Packet metadata (tool_id field)
      - Metrics labels (tool_id tag)
      - Config references (tool_id key)
      Never use tool_name for programmatic references (display only).

  # LOGGING — Use structlog, not stdlib logging
  logging:
    library: "structlog"
    forbidden: ["logging", "print"]
    setup_pattern: |
      import structlog
      log = structlog.get_logger(__name__)
      
      # Usage
      log.info("event_name", field1="value1", field2="value2")

  # HTTP CLIENT — Use httpx, not aiohttp
  http_client:
    library: "httpx"
    forbidden: ["aiohttp", "requests"]
    async_pattern: |
      import httpx
      
      async with httpx.AsyncClient(timeout=30.0) as client:
          response = await client.post(url, json=payload)

# ============================================================================
# SECTION 12: NOTES FOR P
# ============================================================================
notes_for_perplexity:
  - "Use REPO_CONTEXT_PACK imports exactly"
  - "Use PacketEnvelopeIn for all packets"
  - "Use UUIDv5 for thread_id (not uuid4)"
  - "All handlers accept injected services (no singletons)"
  - "Route handlers get services from request.app.state"
  - "Use tool_id (module.id) as canonical identifier everywhere"
  - "Use structlog for all logging (never stdlib logging)"
  - "Use httpx for all HTTP calls (never aiohttp)"
```

---

## Key Patterns Summary

| Pattern | Location | Usage |
|---------|----------|-------|
| **Pydantic `extra="forbid"`** | All schemas | Reject unknown fields |
| **Pydantic `frozen=True`** | `PacketEnvelope` | Immutable after creation |
| **Protocol-based DI** | `executor.py` | No singletons, inject dependencies |
| **UUIDv5 for threads** | `AgentTask.get_thread_id()` | Deterministic thread identity |
| **tool_id canonical** | `ToolBinding`, `ToolCallResult` | Never use display_name for lookup |
| **Deny-by-default** | `GovernanceEngine` | No policy match = deny |
| **ON CONFLICT upserts** | See `L9_IDEMPOTENCY_SSOT.md` | Idempotent DB writes |
| **structlog + httpx** | `Module-Spec-v2.1.yaml` | Mandatory standards |

---

## Related Files

- **Idempotency Patterns**: `L9_IDEMPOTENCY_SSOT.md` (same folder)
- **Full Executor**: `core/agents/executor.py` (788 lines)
- **Full Substrate Models**: `memory/substrate_models.py` (312 lines)

