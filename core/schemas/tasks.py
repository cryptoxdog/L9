"""
L9 Core Schemas - Task Types
============================

Task-related schema definitions for L9's runtime pipeline.

Defines:
- TaskStatus: Lifecycle states for tasks
- AgentTask: Core task model with metadata
- TaskResult: Task execution result
- TaskEnvelope: Wrapper for routing tasks to agents

These types bridge WebSocket events and the task queue system.

Version: 1.0.0
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class TaskStatus(str, Enum):
    """Lifecycle status of a task."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskKind(str, Enum):
    """Kind of task for routing decisions."""
    RESULT = "result"
    ERROR = "error"
    COMMAND = "command"
    QUERY = "query"
    RESEARCH = "research"
    EXECUTION = "execution"


# =============================================================================
# Agent Task
# =============================================================================

class AgentTask(BaseModel):
    """
    Core task model representing work to be executed.
    
    Attributes:
        id: Unique task identifier
        kind: Task kind for routing
        payload: Task-specific data
        created_at: Task creation timestamp
        priority: Task priority (1=highest, 10=lowest)
        trace_id: Distributed tracing identifier
        timeout_ms: Execution timeout in milliseconds
        
    Usage:
        task = AgentTask(
            kind="execution",
            payload={"command": "build", "target": "api"},
            priority=3
        )
    """
    id: UUID = Field(default_factory=uuid4, description="Unique task identifier")
    kind: str = Field(..., description="Task kind for routing")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Task-specific data")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    priority: int = Field(default=5, ge=1, le=10, description="Priority (1=highest)")
    trace_id: Optional[str] = Field(None, description="Distributed trace ID")
    timeout_ms: Optional[int] = Field(None, ge=0, description="Execution timeout (ms)")
    
    model_config = {"extra": "allow"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "kind": self.kind,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
            "priority": self.priority,
            "trace_id": self.trace_id,
            "timeout_ms": self.timeout_ms,
        }


# =============================================================================
# Task Result
# =============================================================================

class TaskResult(BaseModel):
    """
    Result of task execution.
    
    Attributes:
        id: Task ID this result belongs to
        status: Final execution status
        output: Execution output data
        error: Error message if failed
        completed_at: Completion timestamp
        duration_ms: Execution duration in milliseconds
        
    Usage:
        result = TaskResult(
            id=task.id,
            status=TaskStatus.COMPLETED,
            output={"message": "Build successful"},
            duration_ms=1500
        )
    """
    id: UUID = Field(..., description="Task ID")
    status: TaskStatus = Field(..., description="Final execution status")
    output: Dict[str, Any] = Field(default_factory=dict, description="Execution output")
    error: Optional[str] = Field(None, description="Error message if failed")
    completed_at: datetime = Field(default_factory=datetime.utcnow, description="Completion timestamp")
    duration_ms: Optional[int] = Field(None, ge=0, description="Execution duration (ms)")
    
    model_config = {"extra": "allow"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "completed_at": self.completed_at.isoformat(),
            "duration_ms": self.duration_ms,
        }


# =============================================================================
# Task Envelope
# =============================================================================

class TaskEnvelope(BaseModel):
    """
    Wrapper for routing tasks to agents.
    
    Contains a task and routing metadata for the orchestrator
    to dispatch to the appropriate agent.
    
    Attributes:
        task: The enclosed AgentTask
        agent_id: Target agent identifier (optional for broadcast)
        assigned_at: When the task was assigned
        source_event_id: Originating event ID
        retry_count: Number of delivery retries
        
    Usage:
        envelope = TaskEnvelope(
            task=my_task,
            agent_id="coder-agent-1"
        )
    """
    task: AgentTask = Field(..., description="The enclosed task")
    agent_id: Optional[str] = Field(None, description="Target agent ID")
    assigned_at: Optional[datetime] = Field(None, description="Assignment timestamp")
    source_event_id: Optional[UUID] = Field(None, description="Originating event ID")
    retry_count: int = Field(default=0, ge=0, description="Delivery retry count")
    
    model_config = {"extra": "allow"}
    
    def assign_to(self, agent_id: str) -> "TaskEnvelope":
        """
        Assign this envelope to a specific agent.
        
        Args:
            agent_id: Target agent identifier
            
        Returns:
            Self with updated assignment
        """
        self.agent_id = agent_id
        self.assigned_at = datetime.utcnow()
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "task": self.task.to_dict(),
            "agent_id": self.agent_id,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "source_event_id": str(self.source_event_id) if self.source_event_id else None,
            "retry_count": self.retry_count,
        }


# =============================================================================
# Phase 3 Stubs
# =============================================================================

class TaskGraph(BaseModel):
    """
    Phase 3 Stub: DAG of dependent tasks.
    
    Will support parallel execution and dependency management
    when LangGraph-based routing is implemented.
    """
    graph_id: UUID = Field(default_factory=uuid4)
    tasks: list[AgentTask] = Field(default_factory=list)
    dependencies: Dict[str, list[str]] = Field(default_factory=dict)
    # TODO: Phase 3 - Add LangGraph state machine integration


class TaskBatch(BaseModel):
    """
    Phase 3 Stub: Batch of tasks for bulk processing.
    
    Will support atomic batch operations and transactional
    task execution.
    """
    batch_id: UUID = Field(default_factory=uuid4)
    envelopes: list[TaskEnvelope] = Field(default_factory=list)
    atomic: bool = Field(default=False)
    # TODO: Phase 3 - Add transaction support


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Enums
    "TaskStatus",
    "TaskKind",
    # Models
    "AgentTask",
    "TaskResult",
    "TaskEnvelope",
    # Phase 3 Stubs
    "TaskGraph",
    "TaskBatch",
]

