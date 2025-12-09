"""
L9 Runtime - Task State Management
==================================
Version: 2.0.0

Persistent task metadata with agent involvement and packet lineage tracking.

Features:
- Task lifecycle management
- State transitions with validation
- Checkpointing and recovery
- Agent involvement tracking
- Packet lineage (DAG-style)
- Persistence to disk and memory substrate

Compatibility:
- Memory substrate (PacketEnvelope v1.1.0)
- World model integration
- IR Engine integration
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Callable
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class TaskStatus(str, Enum):
    """Status of a task."""
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CHECKPOINTED = "checkpointed"
    RESUMING = "resuming"


class AgentRole(str, Enum):
    """Role of an agent in a task."""
    OWNER = "owner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    OBSERVER = "observer"
    COORDINATOR = "coordinator"


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class AgentInvolvement:
    """Tracks an agent's involvement in a task."""
    agent_id: str
    role: AgentRole = AgentRole.EXECUTOR
    joined_at: datetime = field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = None
    contributions: list[dict[str, Any]] = field(default_factory=list)
    actions_performed: int = 0
    decisions_made: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat(),
            "left_at": self.left_at.isoformat() if self.left_at else None,
            "contributions": self.contributions,
            "actions_performed": self.actions_performed,
            "decisions_made": self.decisions_made,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentInvolvement:
        """Deserialize from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            role=AgentRole(data.get("role", "executor")),
            joined_at=datetime.fromisoformat(data["joined_at"]) if data.get("joined_at") else datetime.utcnow(),
            left_at=datetime.fromisoformat(data["left_at"]) if data.get("left_at") else None,
            contributions=data.get("contributions", []),
            actions_performed=data.get("actions_performed", 0),
            decisions_made=data.get("decisions_made", 0),
            metadata=data.get("metadata", {}),
        )
    
    def record_contribution(self, contribution_type: str, details: dict[str, Any]) -> None:
        """Record a contribution made by the agent."""
        self.contributions.append({
            "type": contribution_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
        })
        self.actions_performed += 1


@dataclass
class PacketLineage:
    """Tracks packet derivation for DAG-style lineage."""
    packet_id: UUID
    packet_type: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    parent_packet_ids: list[UUID] = field(default_factory=list)
    derivation_type: Optional[str] = None  # 'split', 'merge', 'transform', 'inference'
    generation: int = 0
    root_packet_id: Optional[UUID] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "packet_id": str(self.packet_id),
            "packet_type": self.packet_type,
            "created_at": self.created_at.isoformat(),
            "parent_packet_ids": [str(p) for p in self.parent_packet_ids],
            "derivation_type": self.derivation_type,
            "generation": self.generation,
            "root_packet_id": str(self.root_packet_id) if self.root_packet_id else None,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PacketLineage:
        """Deserialize from dictionary."""
        return cls(
            packet_id=UUID(data["packet_id"]),
            packet_type=data.get("packet_type", "unknown"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            parent_packet_ids=[UUID(p) for p in data.get("parent_packet_ids", [])],
            derivation_type=data.get("derivation_type"),
            generation=data.get("generation", 0),
            root_packet_id=UUID(data["root_packet_id"]) if data.get("root_packet_id") else None,
            metadata=data.get("metadata", {}),
        )


@dataclass
class TaskCheckpoint:
    """Checkpoint data for task state recovery."""
    checkpoint_id: UUID = field(default_factory=uuid4)
    task_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: TaskStatus = TaskStatus.CHECKPOINTED
    progress: float = 0.0
    current_step: int = 0
    data: dict[str, Any] = field(default_factory=dict)
    ir_state: Optional[dict[str, Any]] = None
    world_model_context: Optional[dict[str, Any]] = None
    plan_state: Optional[dict[str, Any]] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "checkpoint_id": str(self.checkpoint_id),
            "task_id": str(self.task_id),
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "data": self.data,
            "ir_state": self.ir_state,
            "world_model_context": self.world_model_context,
            "plan_state": self.plan_state,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskCheckpoint:
        """Deserialize from dictionary."""
        return cls(
            checkpoint_id=UUID(data["checkpoint_id"]) if data.get("checkpoint_id") else uuid4(),
            task_id=UUID(data["task_id"]) if data.get("task_id") else uuid4(),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.utcnow(),
            status=TaskStatus(data.get("status", "checkpointed")),
            progress=data.get("progress", 0.0),
            current_step=data.get("current_step", 0),
            data=data.get("data", {}),
            ir_state=data.get("ir_state"),
            world_model_context=data.get("world_model_context"),
            plan_state=data.get("plan_state"),
        )


@dataclass
class TaskTimestamps:
    """Detailed timestamps for task lifecycle."""
    created_at: datetime = field(default_factory=datetime.utcnow)
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    resumed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    last_checkpoint_at: Optional[datetime] = None
    last_activity_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "created_at": self.created_at.isoformat(),
            "queued_at": self.queued_at.isoformat() if self.queued_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "resumed_at": self.resumed_at.isoformat() if self.resumed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "last_checkpoint_at": self.last_checkpoint_at.isoformat() if self.last_checkpoint_at else None,
            "last_activity_at": self.last_activity_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskTimestamps:
        """Deserialize from dictionary."""
        def parse_dt(key: str) -> Optional[datetime]:
            val = data.get(key)
            return datetime.fromisoformat(val) if val else None
        
        return cls(
            created_at=parse_dt("created_at") or datetime.utcnow(),
            queued_at=parse_dt("queued_at"),
            started_at=parse_dt("started_at"),
            paused_at=parse_dt("paused_at"),
            resumed_at=parse_dt("resumed_at"),
            completed_at=parse_dt("completed_at"),
            failed_at=parse_dt("failed_at"),
            cancelled_at=parse_dt("cancelled_at"),
            last_checkpoint_at=parse_dt("last_checkpoint_at"),
            last_activity_at=parse_dt("last_activity_at") or datetime.utcnow(),
        )


@dataclass
class TaskState:
    """
    Complete state of a task with agent involvement and packet lineage.
    
    Supports deterministic, resumable execution with full traceability.
    """
    task_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.CREATED
    progress: float = 0.0
    current_step: int = 0
    total_steps: int = 0
    
    # Task data
    data: dict[str, Any] = field(default_factory=dict)
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: Optional[dict[str, Any]] = None
    
    # Timestamps
    timestamps: TaskTimestamps = field(default_factory=TaskTimestamps)
    
    # Agent involvement
    agents: list[AgentInvolvement] = field(default_factory=list)
    owner_agent_id: Optional[str] = None
    
    # Packet lineage (DAG-style)
    packet_lineage: list[PacketLineage] = field(default_factory=list)
    source_packet_id: Optional[UUID] = None
    emitted_packet_ids: list[UUID] = field(default_factory=list)
    
    # Checkpoints
    checkpoints: list[TaskCheckpoint] = field(default_factory=list)
    active_checkpoint_id: Optional[UUID] = None
    
    # History
    history: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    
    # Metadata
    tags: list[str] = field(default_factory=list)
    priority: int = 3  # 1=critical, 5=lowest
    session_id: Optional[str] = None
    parent_task_id: Optional[UUID] = None
    child_task_ids: list[UUID] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "task_id": str(self.task_id),
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "data": self.data,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "timestamps": self.timestamps.to_dict(),
            "agents": [a.to_dict() for a in self.agents],
            "owner_agent_id": self.owner_agent_id,
            "packet_lineage": [p.to_dict() for p in self.packet_lineage],
            "source_packet_id": str(self.source_packet_id) if self.source_packet_id else None,
            "emitted_packet_ids": [str(p) for p in self.emitted_packet_ids],
            "checkpoints": [c.to_dict() for c in self.checkpoints],
            "active_checkpoint_id": str(self.active_checkpoint_id) if self.active_checkpoint_id else None,
            "history": self.history,
            "errors": self.errors,
            "tags": self.tags,
            "priority": self.priority,
            "session_id": self.session_id,
            "parent_task_id": str(self.parent_task_id) if self.parent_task_id else None,
            "child_task_ids": [str(c) for c in self.child_task_ids],
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskState:
        """Deserialize from dictionary."""
        return cls(
            task_id=UUID(data["task_id"]) if data.get("task_id") else uuid4(),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", "created")),
            progress=data.get("progress", 0.0),
            current_step=data.get("current_step", 0),
            total_steps=data.get("total_steps", 0),
            data=data.get("data", {}),
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data"),
            timestamps=TaskTimestamps.from_dict(data.get("timestamps", {})),
            agents=[AgentInvolvement.from_dict(a) for a in data.get("agents", [])],
            owner_agent_id=data.get("owner_agent_id"),
            packet_lineage=[PacketLineage.from_dict(p) for p in data.get("packet_lineage", [])],
            source_packet_id=UUID(data["source_packet_id"]) if data.get("source_packet_id") else None,
            emitted_packet_ids=[UUID(p) for p in data.get("emitted_packet_ids", [])],
            checkpoints=[TaskCheckpoint.from_dict(c) for c in data.get("checkpoints", [])],
            active_checkpoint_id=UUID(data["active_checkpoint_id"]) if data.get("active_checkpoint_id") else None,
            history=data.get("history", []),
            errors=data.get("errors", []),
            tags=data.get("tags", []),
            priority=data.get("priority", 3),
            session_id=data.get("session_id"),
            parent_task_id=UUID(data["parent_task_id"]) if data.get("parent_task_id") else None,
            child_task_ids=[UUID(c) for c in data.get("child_task_ids", [])],
            metadata=data.get("metadata", {}),
        )
    
    def to_packet_payload(self) -> dict[str, Any]:
        """Generate payload for PacketEnvelope emission."""
        return {
            "kind": "task_state",
            "task_id": str(self.task_id),
            "name": self.name,
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "agent_count": len(self.agents),
            "checkpoint_count": len(self.checkpoints),
            "error_count": len(self.errors),
            "created_at": self.timestamps.created_at.isoformat(),
        }


# =============================================================================
# Task State Manager
# =============================================================================

class TaskStateManager:
    """
    Manages task states with agent involvement and packet lineage tracking.
    
    Features:
    - State tracking with validation
    - Status transitions
    - Agent involvement tracking
    - Packet lineage management
    - Checkpointing
    - Persistence
    """
    
    # Valid status transitions
    VALID_TRANSITIONS = {
        TaskStatus.CREATED: [TaskStatus.QUEUED, TaskStatus.CANCELLED],
        TaskStatus.QUEUED: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
        TaskStatus.RUNNING: [TaskStatus.PAUSED, TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.CHECKPOINTED],
        TaskStatus.PAUSED: [TaskStatus.RUNNING, TaskStatus.RESUMING, TaskStatus.CANCELLED],
        TaskStatus.CHECKPOINTED: [TaskStatus.RESUMING, TaskStatus.CANCELLED],
        TaskStatus.RESUMING: [TaskStatus.RUNNING, TaskStatus.FAILED, TaskStatus.CANCELLED],
        TaskStatus.COMPLETED: [],
        TaskStatus.FAILED: [TaskStatus.QUEUED, TaskStatus.RESUMING],  # Allow retry
        TaskStatus.CANCELLED: [],
    }
    
    def __init__(
        self,
        persistence_path: Optional[Path] = None,
        emit_packets: bool = True,
    ):
        """
        Initialize the state manager.
        
        Args:
            persistence_path: Optional path for state persistence
            emit_packets: Whether to emit PacketEnvelopes
        """
        self._states: dict[UUID, TaskState] = {}
        self._persistence_path = persistence_path
        self._emit_packets = emit_packets
        self._status_callbacks: dict[TaskStatus, list[Callable]] = {
            status: [] for status in TaskStatus
        }
        self._packet_emitter: Optional[Callable] = None
        
        # Load persisted states
        if persistence_path and persistence_path.exists():
            self._load_states()
        
        logger.info("TaskStateManager initialized")
    
    def set_packet_emitter(self, emitter: Callable) -> None:
        """Set the packet emitter function."""
        self._packet_emitter = emitter
    
    # ==========================================================================
    # State Management
    # ==========================================================================
    
    def create_state(
        self,
        name: str,
        description: str = "",
        total_steps: int = 0,
        input_data: Optional[dict[str, Any]] = None,
        owner_agent_id: Optional[str] = None,
        source_packet_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
        parent_task_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        priority: int = 3,
    ) -> TaskState:
        """
        Create a new task state.
        
        Args:
            name: Task name
            description: Task description
            total_steps: Total steps in task
            input_data: Initial input data
            owner_agent_id: Owner agent ID
            source_packet_id: Source packet that triggered this task
            session_id: Session identifier
            parent_task_id: Parent task ID
            tags: Task tags
            priority: Task priority (1-5)
            
        Returns:
            Created TaskState
        """
        state = TaskState(
            name=name,
            description=description,
            total_steps=total_steps,
            input_data=input_data or {},
            owner_agent_id=owner_agent_id,
            source_packet_id=source_packet_id,
            session_id=session_id,
            parent_task_id=parent_task_id,
            tags=tags or [],
            priority=priority,
        )
        
        # Add owner as first agent
        if owner_agent_id:
            state.agents.append(AgentInvolvement(
                agent_id=owner_agent_id,
                role=AgentRole.OWNER,
            ))
        
        # Track source packet in lineage
        if source_packet_id:
            state.packet_lineage.append(PacketLineage(
                packet_id=source_packet_id,
                packet_type="source",
                derivation_type="trigger",
            ))
        
        self._states[state.task_id] = state
        self._record_history(state, "created", {"name": name})
        
        # Link to parent task
        if parent_task_id:
            parent = self.get_state(parent_task_id)
            if parent:
                parent.child_task_ids.append(state.task_id)
        
        logger.info(f"Created task state: {state.task_id} ({name})")
        
        return state
    
    def get_state(self, task_id: UUID) -> Optional[TaskState]:
        """Get task state by ID."""
        return self._states.get(task_id)
    
    def get_all_states(self) -> list[TaskState]:
        """Get all task states."""
        return list(self._states.values())
    
    def get_states_by_status(self, status: TaskStatus) -> list[TaskState]:
        """Get states with a specific status."""
        return [s for s in self._states.values() if s.status == status]
    
    def get_states_by_agent(self, agent_id: str) -> list[TaskState]:
        """Get states involving a specific agent."""
        result = []
        for state in self._states.values():
            for agent in state.agents:
                if agent.agent_id == agent_id:
                    result.append(state)
                    break
        return result
    
    def get_states_by_session(self, session_id: str) -> list[TaskState]:
        """Get states in a specific session."""
        return [s for s in self._states.values() if s.session_id == session_id]
    
    # ==========================================================================
    # Status Transitions
    # ==========================================================================
    
    def transition(
        self,
        task_id: UUID,
        new_status: TaskStatus,
        reason: str = "",
        agent_id: Optional[str] = None,
    ) -> bool:
        """
        Transition task to new status.
        
        Args:
            task_id: Task ID
            new_status: Target status
            reason: Reason for transition
            agent_id: Agent performing the transition
            
        Returns:
            True if transition succeeded
        """
        state = self._states.get(task_id)
        if not state:
            logger.error(f"Task not found: {task_id}")
            return False
        
        # Check if transition is valid
        valid_next = self.VALID_TRANSITIONS.get(state.status, [])
        if new_status not in valid_next:
            logger.error(
                f"Invalid transition: {state.status.value} -> {new_status.value}"
            )
            return False
        
        old_status = state.status
        state.status = new_status
        
        # Update timestamps
        now = datetime.utcnow()
        state.timestamps.last_activity_at = now
        
        if new_status == TaskStatus.QUEUED:
            state.timestamps.queued_at = now
        elif new_status == TaskStatus.RUNNING:
            state.timestamps.started_at = now
        elif new_status == TaskStatus.PAUSED:
            state.timestamps.paused_at = now
        elif new_status == TaskStatus.RESUMING:
            state.timestamps.resumed_at = now
        elif new_status == TaskStatus.COMPLETED:
            state.timestamps.completed_at = now
            state.progress = 1.0
        elif new_status == TaskStatus.FAILED:
            state.timestamps.failed_at = now
        elif new_status == TaskStatus.CANCELLED:
            state.timestamps.cancelled_at = now
        
        self._record_history(state, "transition", {
            "from": old_status.value,
            "to": new_status.value,
            "reason": reason,
            "agent_id": agent_id,
        })
        
        # Execute callbacks
        for callback in self._status_callbacks.get(new_status, []):
            try:
                callback(state)
            except Exception as e:
                logger.error(f"Status callback error: {e}")
        
        # Persist
        self._persist_state(state)
        
        logger.info(f"Task {task_id}: {old_status.value} -> {new_status.value}")
        
        return True
    
    def start(self, task_id: UUID, agent_id: Optional[str] = None) -> bool:
        """Start a task."""
        state = self.get_state(task_id)
        if state and state.status == TaskStatus.CREATED:
            self.transition(task_id, TaskStatus.QUEUED, agent_id=agent_id)
        return self.transition(task_id, TaskStatus.RUNNING, agent_id=agent_id)
    
    def complete(
        self,
        task_id: UUID,
        output_data: Optional[dict[str, Any]] = None,
        agent_id: Optional[str] = None,
    ) -> bool:
        """Mark task as completed."""
        state = self.get_state(task_id)
        if state:
            state.progress = 1.0
            state.output_data = output_data
        return self.transition(task_id, TaskStatus.COMPLETED, agent_id=agent_id)
    
    def fail(
        self,
        task_id: UUID,
        error: str,
        agent_id: Optional[str] = None,
    ) -> bool:
        """Mark task as failed."""
        state = self.get_state(task_id)
        if state:
            state.errors.append(error)
        return self.transition(task_id, TaskStatus.FAILED, error, agent_id=agent_id)
    
    def pause(self, task_id: UUID, agent_id: Optional[str] = None) -> bool:
        """Pause a task."""
        return self.transition(task_id, TaskStatus.PAUSED, agent_id=agent_id)
    
    def resume(self, task_id: UUID, agent_id: Optional[str] = None) -> bool:
        """Resume a paused task."""
        state = self.get_state(task_id)
        if state:
            self.transition(task_id, TaskStatus.RESUMING, agent_id=agent_id)
        return self.transition(task_id, TaskStatus.RUNNING, agent_id=agent_id)
    
    def cancel(
        self,
        task_id: UUID,
        reason: str = "",
        agent_id: Optional[str] = None,
    ) -> bool:
        """Cancel a task."""
        return self.transition(task_id, TaskStatus.CANCELLED, reason, agent_id=agent_id)
    
    # ==========================================================================
    # Agent Involvement
    # ==========================================================================
    
    def add_agent(
        self,
        task_id: UUID,
        agent_id: str,
        role: AgentRole = AgentRole.EXECUTOR,
    ) -> bool:
        """
        Add an agent to a task.
        
        Args:
            task_id: Task ID
            agent_id: Agent identifier
            role: Agent role
            
        Returns:
            True if added
        """
        state = self._states.get(task_id)
        if not state:
            return False
        
        # Check if agent already involved
        for agent in state.agents:
            if agent.agent_id == agent_id:
                logger.warning(f"Agent {agent_id} already involved in task {task_id}")
                return False
        
        involvement = AgentInvolvement(agent_id=agent_id, role=role)
        state.agents.append(involvement)
        
        self._record_history(state, "agent_added", {
            "agent_id": agent_id,
            "role": role.value,
        })
        
        logger.info(f"Agent {agent_id} added to task {task_id} as {role.value}")
        return True
    
    def remove_agent(self, task_id: UUID, agent_id: str) -> bool:
        """
        Remove an agent from a task.
        
        Args:
            task_id: Task ID
            agent_id: Agent identifier
            
        Returns:
            True if removed
        """
        state = self._states.get(task_id)
        if not state:
            return False
        
        for i, agent in enumerate(state.agents):
            if agent.agent_id == agent_id:
                agent.left_at = datetime.utcnow()
                
                self._record_history(state, "agent_removed", {
                    "agent_id": agent_id,
                })
                
                logger.info(f"Agent {agent_id} removed from task {task_id}")
                return True
        
        return False
    
    def record_agent_contribution(
        self,
        task_id: UUID,
        agent_id: str,
        contribution_type: str,
        details: dict[str, Any],
    ) -> bool:
        """
        Record a contribution from an agent.
        
        Args:
            task_id: Task ID
            agent_id: Agent identifier
            contribution_type: Type of contribution
            details: Contribution details
            
        Returns:
            True if recorded
        """
        state = self._states.get(task_id)
        if not state:
            return False
        
        for agent in state.agents:
            if agent.agent_id == agent_id:
                agent.record_contribution(contribution_type, details)
                state.timestamps.last_activity_at = datetime.utcnow()
                return True
        
        return False
    
    def get_task_agents(self, task_id: UUID) -> list[AgentInvolvement]:
        """Get all agents involved in a task."""
        state = self._states.get(task_id)
        return state.agents if state else []
    
    # ==========================================================================
    # Packet Lineage
    # ==========================================================================
    
    def add_packet_to_lineage(
        self,
        task_id: UUID,
        packet_id: UUID,
        packet_type: str,
        parent_packet_ids: Optional[list[UUID]] = None,
        derivation_type: Optional[str] = None,
    ) -> bool:
        """
        Add a packet to task lineage.
        
        Args:
            task_id: Task ID
            packet_id: Packet ID
            packet_type: Type of packet
            parent_packet_ids: Parent packet IDs
            derivation_type: How this packet was derived
            
        Returns:
            True if added
        """
        state = self._states.get(task_id)
        if not state:
            return False
        
        # Calculate generation
        generation = 0
        if parent_packet_ids:
            for parent_id in parent_packet_ids:
                for p in state.packet_lineage:
                    if p.packet_id == parent_id:
                        generation = max(generation, p.generation + 1)
                        break
        
        # Find root packet
        root_packet_id = state.source_packet_id
        if not root_packet_id and state.packet_lineage:
            root_packet_id = state.packet_lineage[0].packet_id
        
        lineage = PacketLineage(
            packet_id=packet_id,
            packet_type=packet_type,
            parent_packet_ids=parent_packet_ids or [],
            derivation_type=derivation_type,
            generation=generation,
            root_packet_id=root_packet_id,
        )
        
        state.packet_lineage.append(lineage)
        state.emitted_packet_ids.append(packet_id)
        
        self._record_history(state, "packet_added", {
            "packet_id": str(packet_id),
            "packet_type": packet_type,
            "generation": generation,
        })
        
        return True
    
    def get_packet_lineage(self, task_id: UUID) -> list[PacketLineage]:
        """Get packet lineage for a task."""
        state = self._states.get(task_id)
        return state.packet_lineage if state else []
    
    def get_packet_ancestors(self, task_id: UUID, packet_id: UUID) -> list[PacketLineage]:
        """Get all ancestor packets in lineage."""
        state = self._states.get(task_id)
        if not state:
            return []
        
        ancestors = []
        to_check = [packet_id]
        checked = set()
        
        while to_check:
            current_id = to_check.pop(0)
            if current_id in checked:
                continue
            checked.add(current_id)
            
            for lineage in state.packet_lineage:
                if lineage.packet_id == current_id:
                    if current_id != packet_id:
                        ancestors.append(lineage)
                    to_check.extend(lineage.parent_packet_ids)
        
        return ancestors
    
    # ==========================================================================
    # Progress
    # ==========================================================================
    
    def update_progress(
        self,
        task_id: UUID,
        progress: Optional[float] = None,
        step: Optional[int] = None,
    ) -> bool:
        """
        Update task progress.
        
        Args:
            task_id: Task ID
            progress: Progress value (0.0 to 1.0)
            step: Current step number
            
        Returns:
            True if updated
        """
        state = self._states.get(task_id)
        if not state:
            return False
        
        if progress is not None:
            state.progress = max(0.0, min(1.0, progress))
        
        if step is not None:
            state.current_step = step
            if state.total_steps > 0:
                state.progress = step / state.total_steps
        
        state.timestamps.last_activity_at = datetime.utcnow()
        
        return True
    
    def update_data(
        self,
        task_id: UUID,
        data: dict[str, Any],
        merge: bool = True,
    ) -> bool:
        """
        Update task data.
        
        Args:
            task_id: Task ID
            data: Data to update
            merge: Whether to merge with existing
            
        Returns:
            True if updated
        """
        state = self._states.get(task_id)
        if not state:
            return False
        
        if merge:
            state.data.update(data)
        else:
            state.data = data
        
        state.timestamps.last_activity_at = datetime.utcnow()
        
        return True
    
    # ==========================================================================
    # Checkpointing
    # ==========================================================================
    
    def checkpoint(
        self,
        task_id: UUID,
        ir_state: Optional[dict[str, Any]] = None,
        world_model_context: Optional[dict[str, Any]] = None,
        plan_state: Optional[dict[str, Any]] = None,
    ) -> Optional[TaskCheckpoint]:
        """
        Create a checkpoint.
        
        Args:
            task_id: Task ID
            ir_state: IR engine state to snapshot
            world_model_context: World model context to snapshot
            plan_state: Plan state to snapshot
            
        Returns:
            TaskCheckpoint or None
        """
        state = self._states.get(task_id)
        if not state:
            return None
        
        checkpoint = TaskCheckpoint(
            task_id=task_id,
            status=state.status,
            progress=state.progress,
            current_step=state.current_step,
            data=state.data.copy(),
            ir_state=ir_state,
            world_model_context=world_model_context,
            plan_state=plan_state,
        )
        
        state.checkpoints.append(checkpoint)
        state.active_checkpoint_id = checkpoint.checkpoint_id
        state.timestamps.last_checkpoint_at = datetime.utcnow()
        
        self._record_history(state, "checkpoint", {
            "checkpoint_id": str(checkpoint.checkpoint_id),
        })
        
        logger.debug(f"Created checkpoint for task {task_id}")
        
        return checkpoint
    
    def restore_checkpoint(
        self,
        task_id: UUID,
        checkpoint_id: Optional[UUID] = None,
    ) -> bool:
        """
        Restore from checkpoint.
        
        Args:
            task_id: Task ID
            checkpoint_id: Specific checkpoint ID (or latest if None)
            
        Returns:
            True if restored
        """
        state = self._states.get(task_id)
        if not state or not state.checkpoints:
            return False
        
        # Find checkpoint
        checkpoint = None
        if checkpoint_id:
            for cp in state.checkpoints:
                if cp.checkpoint_id == checkpoint_id:
                    checkpoint = cp
                    break
        else:
            checkpoint = state.checkpoints[-1]
        
        if not checkpoint:
            return False
        
        # Restore state
        state.status = checkpoint.status
        state.progress = checkpoint.progress
        state.current_step = checkpoint.current_step
        state.data = checkpoint.data.copy()
        state.active_checkpoint_id = checkpoint.checkpoint_id
        state.timestamps.resumed_at = datetime.utcnow()
        
        self._record_history(state, "restore", {
            "checkpoint_id": str(checkpoint.checkpoint_id),
        })
        
        logger.info(f"Restored task {task_id} from checkpoint")
        
        return True
    
    def get_checkpoint(
        self,
        task_id: UUID,
        checkpoint_id: Optional[UUID] = None,
    ) -> Optional[TaskCheckpoint]:
        """Get a specific checkpoint or latest."""
        state = self._states.get(task_id)
        if not state or not state.checkpoints:
            return None
        
        if checkpoint_id:
            for cp in state.checkpoints:
                if cp.checkpoint_id == checkpoint_id:
                    return cp
            return None
        
        return state.checkpoints[-1]
    
    # ==========================================================================
    # Callbacks
    # ==========================================================================
    
    def on_status(
        self,
        status: TaskStatus,
        callback: Callable[[TaskState], None],
    ) -> None:
        """Register a status callback."""
        self._status_callbacks[status].append(callback)
    
    # ==========================================================================
    # Persistence
    # ==========================================================================
    
    def _persist_state(self, state: TaskState) -> None:
        """Persist a state to disk."""
        if not self._persistence_path:
            return
        
        self._persistence_path.mkdir(parents=True, exist_ok=True)
        
        state_file = self._persistence_path / f"{state.task_id}.json"
        try:
            with open(state_file, "w") as f:
                json.dump(state.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist state: {e}")
    
    def _load_states(self) -> None:
        """Load states from disk."""
        if not self._persistence_path:
            return
        
        for state_file in self._persistence_path.glob("*.json"):
            try:
                with open(state_file, "r") as f:
                    data = json.load(f)
                state = TaskState.from_dict(data)
                self._states[state.task_id] = state
            except Exception as e:
                logger.error(f"Failed to load state from {state_file}: {e}")
        
        if self._states:
            logger.info(f"Loaded {len(self._states)} task states")
    
    def _record_history(
        self,
        state: TaskState,
        event: str,
        details: dict[str, Any],
    ) -> None:
        """Record an event in task history."""
        state.history.append({
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
        })
    
    def save_all(self) -> int:
        """Save all states to disk."""
        count = 0
        for state in self._states.values():
            self._persist_state(state)
            count += 1
        logger.info(f"Saved {count} task states")
        return count
    
    # ==========================================================================
    # Cleanup
    # ==========================================================================
    
    def cleanup_completed(self, max_age_hours: int = 24) -> int:
        """
        Clean up old completed tasks.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of tasks removed
        """
        cutoff = datetime.utcnow()
        removed = 0
        
        for task_id, state in list(self._states.items()):
            if state.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
                completed_at = state.timestamps.completed_at or state.timestamps.cancelled_at
                if completed_at:
                    age_hours = (cutoff - completed_at).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        del self._states[task_id]
                        
                        # Remove persisted file
                        if self._persistence_path:
                            state_file = self._persistence_path / f"{task_id}.json"
                            if state_file.exists():
                                state_file.unlink()
                        
                        removed += 1
        
        logger.info(f"Cleaned up {removed} old tasks")
        return removed
