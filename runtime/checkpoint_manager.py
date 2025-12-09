"""
L9 Runtime - Checkpoint Manager
===============================
Version: 1.0.0

Manages checkpoints for deterministic, resumable execution.

Features:
- Snapshot IR state
- Snapshot world-model context
- Snapshot execution plan
- Recover from failure
- Restore execution position
- PacketEnvelope emission

Compatibility:
- Memory substrate (PacketEnvelope v1.1.0)
- World model integration
- IR Engine integration
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Callable, TypeVar, Generic
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class CheckpointType(str, Enum):
    """Type of checkpoint."""
    FULL = "full"  # Complete state snapshot
    INCREMENTAL = "incremental"  # Only changes since last checkpoint
    IR_STATE = "ir_state"  # IR graph snapshot
    WORLD_MODEL = "world_model"  # World model context
    PLAN = "plan"  # Execution plan snapshot
    TASK = "task"  # Task state snapshot
    COMBINED = "combined"  # All states combined


class CheckpointStatus(str, Enum):
    """Status of a checkpoint."""
    CREATING = "creating"
    VALID = "valid"
    CORRUPTED = "corrupted"
    RESTORING = "restoring"
    EXPIRED = "expired"


class RecoveryStrategy(str, Enum):
    """Strategy for recovery from failure."""
    LATEST_CHECKPOINT = "latest_checkpoint"  # Restore from latest valid checkpoint
    SPECIFIC_CHECKPOINT = "specific_checkpoint"  # Restore from specific checkpoint
    FULL_RESTART = "full_restart"  # Restart from beginning
    SKIP_FAILED = "skip_failed"  # Skip failed step, continue


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class IRStateSnapshot:
    """Snapshot of IR engine state."""
    snapshot_id: UUID = field(default_factory=uuid4)
    graph_id: Optional[UUID] = None
    status: str = ""
    intents: list[dict[str, Any]] = field(default_factory=list)
    constraints: list[dict[str, Any]] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    processing_log: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "snapshot_id": str(self.snapshot_id),
            "graph_id": str(self.graph_id) if self.graph_id else None,
            "status": self.status,
            "intents": self.intents,
            "constraints": self.constraints,
            "actions": self.actions,
            "processing_log": self.processing_log,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IRStateSnapshot:
        """Deserialize from dictionary."""
        return cls(
            snapshot_id=UUID(data["snapshot_id"]) if data.get("snapshot_id") else uuid4(),
            graph_id=UUID(data["graph_id"]) if data.get("graph_id") else None,
            status=data.get("status", ""),
            intents=data.get("intents", []),
            constraints=data.get("constraints", []),
            actions=data.get("actions", []),
            processing_log=data.get("processing_log", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
        )
    
    @classmethod
    def from_ir_graph(cls, graph: Any) -> IRStateSnapshot:
        """Create snapshot from IR graph object."""
        return cls(
            graph_id=getattr(graph, "graph_id", None),
            status=getattr(graph, "status", "").value if hasattr(getattr(graph, "status", None), "value") else str(getattr(graph, "status", "")),
            intents=[
                {
                    "node_id": str(i.node_id),
                    "intent_type": i.intent_type.value if hasattr(i.intent_type, "value") else str(i.intent_type),
                    "description": i.description,
                    "target": i.target,
                    "parameters": i.parameters,
                }
                for i in getattr(graph, "intents", {}).values()
            ] if hasattr(graph, "intents") else [],
            constraints=[
                {
                    "node_id": str(c.node_id),
                    "constraint_type": c.constraint_type.value if hasattr(c.constraint_type, "value") else str(c.constraint_type),
                    "status": c.status.value if hasattr(c.status, "value") else str(c.status),
                    "description": c.description,
                }
                for c in getattr(graph, "constraints", {}).values()
            ] if hasattr(graph, "constraints") else [],
            actions=[
                {
                    "node_id": str(a.node_id),
                    "action_type": a.action_type.value if hasattr(a.action_type, "value") else str(a.action_type),
                    "description": a.description,
                    "target": a.target,
                    "parameters": a.parameters,
                    "depends_on": [str(d) for d in a.depends_on],
                }
                for a in getattr(graph, "actions", {}).values()
            ] if hasattr(graph, "actions") else [],
            processing_log=getattr(graph, "processing_log", []),
            metadata=getattr(graph, "metadata", {}).model_dump() if hasattr(getattr(graph, "metadata", None), "model_dump") else dict(getattr(graph, "metadata", {})),
        )


@dataclass
class WorldModelSnapshot:
    """Snapshot of world model context."""
    snapshot_id: UUID = field(default_factory=uuid4)
    entities: list[dict[str, Any]] = field(default_factory=list)
    relations: list[dict[str, Any]] = field(default_factory=list)
    causal_graph: Optional[dict[str, Any]] = None
    patterns: list[dict[str, Any]] = field(default_factory=list)
    heuristics: list[dict[str, Any]] = field(default_factory=list)
    context_variables: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "snapshot_id": str(self.snapshot_id),
            "entities": self.entities,
            "relations": self.relations,
            "causal_graph": self.causal_graph,
            "patterns": self.patterns,
            "heuristics": self.heuristics,
            "context_variables": self.context_variables,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorldModelSnapshot:
        """Deserialize from dictionary."""
        return cls(
            snapshot_id=UUID(data["snapshot_id"]) if data.get("snapshot_id") else uuid4(),
            entities=data.get("entities", []),
            relations=data.get("relations", []),
            causal_graph=data.get("causal_graph"),
            patterns=data.get("patterns", []),
            heuristics=data.get("heuristics", []),
            context_variables=data.get("context_variables", {}),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
        )
    
    @classmethod
    def from_world_model(cls, world_model: Any) -> WorldModelSnapshot:
        """Create snapshot from world model object."""
        entities = []
        if hasattr(world_model, "get_all_entities"):
            for entity in world_model.get_all_entities():
                entities.append({
                    "entity_id": str(getattr(entity, "entity_id", "")),
                    "entity_type": str(getattr(entity, "entity_type", "")),
                    "name": getattr(entity, "name", ""),
                    "attributes": getattr(entity, "attributes", {}),
                })
        
        relations = []
        if hasattr(world_model, "get_all_relations"):
            for relation in world_model.get_all_relations():
                relations.append({
                    "relation_id": str(getattr(relation, "relation_id", "")),
                    "relation_type": str(getattr(relation, "relation_type", "")),
                    "source_id": str(getattr(relation, "source_id", "")),
                    "target_id": str(getattr(relation, "target_id", "")),
                })
        
        return cls(
            entities=entities,
            relations=relations,
            context_variables=getattr(world_model, "context", {}),
        )


@dataclass
class PlanSnapshot:
    """Snapshot of execution plan."""
    snapshot_id: UUID = field(default_factory=uuid4)
    plan_id: Optional[UUID] = None
    steps: list[dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    completed_steps: list[int] = field(default_factory=list)
    failed_steps: list[int] = field(default_factory=list)
    skipped_steps: list[int] = field(default_factory=list)
    step_results: dict[int, dict[str, Any]] = field(default_factory=dict)
    execution_order: list[int] = field(default_factory=list)
    dependencies: dict[int, list[int]] = field(default_factory=dict)
    estimated_remaining_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "snapshot_id": str(self.snapshot_id),
            "plan_id": str(self.plan_id) if self.plan_id else None,
            "steps": self.steps,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "skipped_steps": self.skipped_steps,
            "step_results": {str(k): v for k, v in self.step_results.items()},
            "execution_order": self.execution_order,
            "dependencies": {str(k): v for k, v in self.dependencies.items()},
            "estimated_remaining_ms": self.estimated_remaining_ms,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlanSnapshot:
        """Deserialize from dictionary."""
        return cls(
            snapshot_id=UUID(data["snapshot_id"]) if data.get("snapshot_id") else uuid4(),
            plan_id=UUID(data["plan_id"]) if data.get("plan_id") else None,
            steps=data.get("steps", []),
            current_step=data.get("current_step", 0),
            completed_steps=data.get("completed_steps", []),
            failed_steps=data.get("failed_steps", []),
            skipped_steps=data.get("skipped_steps", []),
            step_results={int(k): v for k, v in data.get("step_results", {}).items()},
            execution_order=data.get("execution_order", []),
            dependencies={int(k): v for k, v in data.get("dependencies", {}).items()},
            estimated_remaining_ms=data.get("estimated_remaining_ms", 0),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
        )


@dataclass
class Checkpoint:
    """Complete checkpoint with all state snapshots."""
    checkpoint_id: UUID = field(default_factory=uuid4)
    task_id: Optional[UUID] = None
    checkpoint_type: CheckpointType = CheckpointType.FULL
    status: CheckpointStatus = CheckpointStatus.VALID
    
    # Snapshots
    ir_state: Optional[IRStateSnapshot] = None
    world_model: Optional[WorldModelSnapshot] = None
    plan: Optional[PlanSnapshot] = None
    
    # Custom data
    custom_data: dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Lineage
    parent_checkpoint_id: Optional[UUID] = None
    sequence_number: int = 0
    
    # Metadata
    description: str = ""
    tags: list[str] = field(default_factory=list)
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "checkpoint_id": str(self.checkpoint_id),
            "task_id": str(self.task_id) if self.task_id else None,
            "checkpoint_type": self.checkpoint_type.value,
            "status": self.status.value,
            "ir_state": self.ir_state.to_dict() if self.ir_state else None,
            "world_model": self.world_model.to_dict() if self.world_model else None,
            "plan": self.plan.to_dict() if self.plan else None,
            "custom_data": self.custom_data,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "parent_checkpoint_id": str(self.parent_checkpoint_id) if self.parent_checkpoint_id else None,
            "sequence_number": self.sequence_number,
            "description": self.description,
            "tags": self.tags,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Checkpoint:
        """Deserialize from dictionary."""
        return cls(
            checkpoint_id=UUID(data["checkpoint_id"]) if data.get("checkpoint_id") else uuid4(),
            task_id=UUID(data["task_id"]) if data.get("task_id") else None,
            checkpoint_type=CheckpointType(data.get("checkpoint_type", "full")),
            status=CheckpointStatus(data.get("status", "valid")),
            ir_state=IRStateSnapshot.from_dict(data["ir_state"]) if data.get("ir_state") else None,
            world_model=WorldModelSnapshot.from_dict(data["world_model"]) if data.get("world_model") else None,
            plan=PlanSnapshot.from_dict(data["plan"]) if data.get("plan") else None,
            custom_data=data.get("custom_data", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            parent_checkpoint_id=UUID(data["parent_checkpoint_id"]) if data.get("parent_checkpoint_id") else None,
            sequence_number=data.get("sequence_number", 0),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            agent_id=data.get("agent_id"),
            session_id=data.get("session_id"),
        )
    
    def to_packet_payload(self) -> dict[str, Any]:
        """Generate payload for PacketEnvelope emission."""
        return {
            "kind": "checkpoint",
            "checkpoint_id": str(self.checkpoint_id),
            "task_id": str(self.task_id) if self.task_id else None,
            "checkpoint_type": self.checkpoint_type.value,
            "status": self.status.value,
            "has_ir_state": self.ir_state is not None,
            "has_world_model": self.world_model is not None,
            "has_plan": self.plan is not None,
            "sequence_number": self.sequence_number,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class RecoveryResult:
    """Result of a recovery operation."""
    success: bool = False
    checkpoint_id: Optional[UUID] = None
    strategy_used: RecoveryStrategy = RecoveryStrategy.LATEST_CHECKPOINT
    restored_ir_state: bool = False
    restored_world_model: bool = False
    restored_plan: bool = False
    execution_position: int = 0
    error: Optional[str] = None
    recovery_time_ms: float = 0.0
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "success": self.success,
            "checkpoint_id": str(self.checkpoint_id) if self.checkpoint_id else None,
            "strategy_used": self.strategy_used.value,
            "restored_ir_state": self.restored_ir_state,
            "restored_world_model": self.restored_world_model,
            "restored_plan": self.restored_plan,
            "execution_position": self.execution_position,
            "error": self.error,
            "recovery_time_ms": self.recovery_time_ms,
        }


@dataclass
class CheckpointConfig:
    """Configuration for checkpoint manager."""
    storage_path: Path = field(default_factory=lambda: Path("checkpoints"))
    max_checkpoints_per_task: int = 10
    auto_checkpoint_interval_ms: int = 30000
    checkpoint_on_step: bool = True
    checkpoint_on_error: bool = True
    compress_checkpoints: bool = False
    expire_after_hours: int = 24
    emit_packets: bool = True


# =============================================================================
# Checkpoint Manager
# =============================================================================

class CheckpointManager:
    """
    Manages checkpoints for deterministic, resumable execution.
    
    Features:
    - Snapshot IR state, world model, and plan
    - Recover from failure
    - Restore execution position
    - Persistence to disk
    - PacketEnvelope emission
    """
    
    def __init__(self, config: Optional[CheckpointConfig] = None):
        """
        Initialize the checkpoint manager.
        
        Args:
            config: Manager configuration
        """
        self._config = config or CheckpointConfig()
        self._checkpoints: dict[UUID, Checkpoint] = {}
        self._task_checkpoints: dict[UUID, list[UUID]] = {}
        self._sequence_counters: dict[UUID, int] = {}
        self._packet_emitter: Optional[Callable] = None
        self._lock = asyncio.Lock()
        
        # Ensure storage directory exists
        self._config.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing checkpoints
        self._load_checkpoints()
        
        logger.info(f"CheckpointManager initialized (storage={self._config.storage_path})")
    
    def set_packet_emitter(self, emitter: Callable) -> None:
        """Set the packet emitter function."""
        self._packet_emitter = emitter
    
    # ==========================================================================
    # Checkpoint Creation
    # ==========================================================================
    
    async def create_checkpoint(
        self,
        task_id: UUID,
        ir_graph: Optional[Any] = None,
        world_model: Optional[Any] = None,
        plan: Optional[dict[str, Any]] = None,
        checkpoint_type: CheckpointType = CheckpointType.FULL,
        description: str = "",
        tags: Optional[list[str]] = None,
        custom_data: Optional[dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Checkpoint:
        """
        Create a checkpoint.
        
        Args:
            task_id: Task ID
            ir_graph: IR graph object to snapshot
            world_model: World model object to snapshot
            plan: Execution plan dictionary to snapshot
            checkpoint_type: Type of checkpoint
            description: Checkpoint description
            tags: Tags for categorization
            custom_data: Additional custom data
            agent_id: Agent creating checkpoint
            session_id: Session identifier
            
        Returns:
            Created Checkpoint
        """
        async with self._lock:
            # Get sequence number
            sequence = self._sequence_counters.get(task_id, 0) + 1
            self._sequence_counters[task_id] = sequence
            
            # Get parent checkpoint
            task_checkpoints = self._task_checkpoints.get(task_id, [])
            parent_id = task_checkpoints[-1] if task_checkpoints else None
            
            # Create snapshots
            ir_state = None
            if ir_graph:
                ir_state = IRStateSnapshot.from_ir_graph(ir_graph)
            
            wm_snapshot = None
            if world_model:
                wm_snapshot = WorldModelSnapshot.from_world_model(world_model)
            
            plan_snapshot = None
            if plan:
                plan_snapshot = PlanSnapshot(
                    plan_id=UUID(plan["plan_id"]) if plan.get("plan_id") else None,
                    steps=plan.get("steps", []),
                    current_step=plan.get("current_step", 0),
                    completed_steps=plan.get("completed_steps", []),
                    failed_steps=plan.get("failed_steps", []),
                    step_results=plan.get("step_results", {}),
                )
            
            # Calculate expiry
            expires_at = None
            if self._config.expire_after_hours > 0:
                from datetime import timedelta
                expires_at = datetime.utcnow() + timedelta(hours=self._config.expire_after_hours)
            
            # Create checkpoint
            checkpoint = Checkpoint(
                task_id=task_id,
                checkpoint_type=checkpoint_type,
                status=CheckpointStatus.VALID,
                ir_state=ir_state,
                world_model=wm_snapshot,
                plan=plan_snapshot,
                custom_data=custom_data or {},
                expires_at=expires_at,
                parent_checkpoint_id=parent_id,
                sequence_number=sequence,
                description=description,
                tags=tags or [],
                agent_id=agent_id,
                session_id=session_id,
            )
            
            # Store
            self._checkpoints[checkpoint.checkpoint_id] = checkpoint
            
            if task_id not in self._task_checkpoints:
                self._task_checkpoints[task_id] = []
            self._task_checkpoints[task_id].append(checkpoint.checkpoint_id)
            
            # Enforce max checkpoints
            await self._enforce_max_checkpoints(task_id)
            
            # Persist
            self._persist_checkpoint(checkpoint)
            
            # Emit packet
            if self._config.emit_packets:
                await self._emit_checkpoint_packet(checkpoint, "checkpoint_created")
            
            logger.info(f"Created checkpoint {checkpoint.checkpoint_id} for task {task_id}")
            
            return checkpoint
    
    def create_checkpoint_sync(
        self,
        task_id: UUID,
        ir_state: Optional[dict[str, Any]] = None,
        world_model_context: Optional[dict[str, Any]] = None,
        plan_state: Optional[dict[str, Any]] = None,
        description: str = "",
    ) -> Checkpoint:
        """
        Synchronously create a checkpoint.
        
        Args:
            task_id: Task ID
            ir_state: IR state dictionary
            world_model_context: World model context dictionary
            plan_state: Plan state dictionary
            description: Checkpoint description
            
        Returns:
            Created Checkpoint
        """
        sequence = self._sequence_counters.get(task_id, 0) + 1
        self._sequence_counters[task_id] = sequence
        
        task_checkpoints = self._task_checkpoints.get(task_id, [])
        parent_id = task_checkpoints[-1] if task_checkpoints else None
        
        ir_snapshot = None
        if ir_state:
            ir_snapshot = IRStateSnapshot.from_dict(ir_state)
        
        wm_snapshot = None
        if world_model_context:
            wm_snapshot = WorldModelSnapshot.from_dict(world_model_context)
        
        plan_snapshot = None
        if plan_state:
            plan_snapshot = PlanSnapshot.from_dict(plan_state)
        
        checkpoint = Checkpoint(
            task_id=task_id,
            checkpoint_type=CheckpointType.FULL,
            status=CheckpointStatus.VALID,
            ir_state=ir_snapshot,
            world_model=wm_snapshot,
            plan=plan_snapshot,
            parent_checkpoint_id=parent_id,
            sequence_number=sequence,
            description=description,
        )
        
        self._checkpoints[checkpoint.checkpoint_id] = checkpoint
        
        if task_id not in self._task_checkpoints:
            self._task_checkpoints[task_id] = []
        self._task_checkpoints[task_id].append(checkpoint.checkpoint_id)
        
        self._persist_checkpoint(checkpoint)
        
        logger.info(f"Created checkpoint (sync) {checkpoint.checkpoint_id} for task {task_id}")
        
        return checkpoint
    
    # ==========================================================================
    # Checkpoint Retrieval
    # ==========================================================================
    
    def get_checkpoint(self, checkpoint_id: UUID) -> Optional[Checkpoint]:
        """Get a checkpoint by ID."""
        return self._checkpoints.get(checkpoint_id)
    
    def get_latest_checkpoint(self, task_id: UUID) -> Optional[Checkpoint]:
        """Get the latest checkpoint for a task."""
        task_checkpoints = self._task_checkpoints.get(task_id, [])
        if not task_checkpoints:
            return None
        
        return self._checkpoints.get(task_checkpoints[-1])
    
    def get_task_checkpoints(self, task_id: UUID) -> list[Checkpoint]:
        """Get all checkpoints for a task."""
        checkpoint_ids = self._task_checkpoints.get(task_id, [])
        return [
            self._checkpoints[cid]
            for cid in checkpoint_ids
            if cid in self._checkpoints
        ]
    
    def get_checkpoint_by_sequence(
        self,
        task_id: UUID,
        sequence_number: int,
    ) -> Optional[Checkpoint]:
        """Get a checkpoint by sequence number."""
        for cid in self._task_checkpoints.get(task_id, []):
            checkpoint = self._checkpoints.get(cid)
            if checkpoint and checkpoint.sequence_number == sequence_number:
                return checkpoint
        return None
    
    def get_valid_checkpoints(self, task_id: UUID) -> list[Checkpoint]:
        """Get all valid (non-expired, non-corrupted) checkpoints for a task."""
        now = datetime.utcnow()
        result = []
        
        for cid in self._task_checkpoints.get(task_id, []):
            checkpoint = self._checkpoints.get(cid)
            if not checkpoint:
                continue
            
            if checkpoint.status == CheckpointStatus.CORRUPTED:
                continue
            
            if checkpoint.expires_at and checkpoint.expires_at < now:
                checkpoint.status = CheckpointStatus.EXPIRED
                continue
            
            result.append(checkpoint)
        
        return result
    
    # ==========================================================================
    # Recovery
    # ==========================================================================
    
    async def recover(
        self,
        task_id: UUID,
        strategy: RecoveryStrategy = RecoveryStrategy.LATEST_CHECKPOINT,
        checkpoint_id: Optional[UUID] = None,
    ) -> RecoveryResult:
        """
        Recover task execution from a checkpoint.
        
        Args:
            task_id: Task ID
            strategy: Recovery strategy
            checkpoint_id: Specific checkpoint ID (for SPECIFIC_CHECKPOINT strategy)
            
        Returns:
            RecoveryResult
        """
        start_time = datetime.utcnow()
        result = RecoveryResult(strategy_used=strategy)
        
        try:
            async with self._lock:
                checkpoint = None
                
                if strategy == RecoveryStrategy.SPECIFIC_CHECKPOINT:
                    if checkpoint_id:
                        checkpoint = self._checkpoints.get(checkpoint_id)
                elif strategy == RecoveryStrategy.LATEST_CHECKPOINT:
                    checkpoint = self.get_latest_checkpoint(task_id)
                elif strategy == RecoveryStrategy.FULL_RESTART:
                    # Clear all checkpoints and start fresh
                    await self._clear_task_checkpoints(task_id)
                    result.success = True
                    result.execution_position = 0
                    return result
                elif strategy == RecoveryStrategy.SKIP_FAILED:
                    # Get latest checkpoint and advance position
                    checkpoint = self.get_latest_checkpoint(task_id)
                    if checkpoint and checkpoint.plan:
                        result.execution_position = checkpoint.plan.current_step + 1
                
                if not checkpoint:
                    result.error = "No valid checkpoint found"
                    return result
                
                # Mark checkpoint as restoring
                checkpoint.status = CheckpointStatus.RESTORING
                
                # Extract restored data
                result.checkpoint_id = checkpoint.checkpoint_id
                result.restored_ir_state = checkpoint.ir_state is not None
                result.restored_world_model = checkpoint.world_model is not None
                result.restored_plan = checkpoint.plan is not None
                
                if checkpoint.plan:
                    result.execution_position = checkpoint.plan.current_step
                
                # Mark as valid after restore
                checkpoint.status = CheckpointStatus.VALID
                
                result.success = True
                
                # Emit packet
                if self._config.emit_packets:
                    await self._emit_checkpoint_packet(checkpoint, "checkpoint_restored")
                
        except Exception as e:
            result.error = str(e)
            logger.error(f"Recovery failed: {e}")
        
        result.recovery_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return result
    
    def restore_ir_state(self, checkpoint: Checkpoint) -> Optional[dict[str, Any]]:
        """
        Extract IR state from checkpoint.
        
        Args:
            checkpoint: Checkpoint to extract from
            
        Returns:
            IR state dictionary or None
        """
        if not checkpoint.ir_state:
            return None
        return checkpoint.ir_state.to_dict()
    
    def restore_world_model_context(self, checkpoint: Checkpoint) -> Optional[dict[str, Any]]:
        """
        Extract world model context from checkpoint.
        
        Args:
            checkpoint: Checkpoint to extract from
            
        Returns:
            World model context dictionary or None
        """
        if not checkpoint.world_model:
            return None
        return checkpoint.world_model.to_dict()
    
    def restore_plan_state(self, checkpoint: Checkpoint) -> Optional[dict[str, Any]]:
        """
        Extract plan state from checkpoint.
        
        Args:
            checkpoint: Checkpoint to extract from
            
        Returns:
            Plan state dictionary or None
        """
        if not checkpoint.plan:
            return None
        return checkpoint.plan.to_dict()
    
    def get_execution_position(self, checkpoint: Checkpoint) -> int:
        """
        Get execution position from checkpoint.
        
        Args:
            checkpoint: Checkpoint
            
        Returns:
            Current step number
        """
        if checkpoint.plan:
            return checkpoint.plan.current_step
        return 0
    
    # ==========================================================================
    # Checkpoint Management
    # ==========================================================================
    
    async def invalidate_checkpoint(
        self,
        checkpoint_id: UUID,
        reason: str = "",
    ) -> bool:
        """
        Mark a checkpoint as corrupted/invalid.
        
        Args:
            checkpoint_id: Checkpoint ID
            reason: Reason for invalidation
            
        Returns:
            True if invalidated
        """
        checkpoint = self._checkpoints.get(checkpoint_id)
        if not checkpoint:
            return False
        
        checkpoint.status = CheckpointStatus.CORRUPTED
        self._persist_checkpoint(checkpoint)
        
        logger.warning(f"Checkpoint {checkpoint_id} invalidated: {reason}")
        return True
    
    async def delete_checkpoint(self, checkpoint_id: UUID) -> bool:
        """
        Delete a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID
            
        Returns:
            True if deleted
        """
        checkpoint = self._checkpoints.get(checkpoint_id)
        if not checkpoint:
            return False
        
        # Remove from task mapping
        if checkpoint.task_id:
            task_checkpoints = self._task_checkpoints.get(checkpoint.task_id, [])
            if checkpoint_id in task_checkpoints:
                task_checkpoints.remove(checkpoint_id)
        
        # Remove from storage
        del self._checkpoints[checkpoint_id]
        
        # Delete file
        checkpoint_file = self._config.storage_path / f"{checkpoint_id}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
        
        logger.info(f"Deleted checkpoint {checkpoint_id}")
        return True
    
    async def _clear_task_checkpoints(self, task_id: UUID) -> int:
        """Clear all checkpoints for a task."""
        checkpoint_ids = self._task_checkpoints.get(task_id, []).copy()
        count = 0
        
        for cid in checkpoint_ids:
            if await self.delete_checkpoint(cid):
                count += 1
        
        self._task_checkpoints[task_id] = []
        
        return count
    
    async def _enforce_max_checkpoints(self, task_id: UUID) -> None:
        """Remove old checkpoints exceeding max limit."""
        task_checkpoints = self._task_checkpoints.get(task_id, [])
        
        while len(task_checkpoints) > self._config.max_checkpoints_per_task:
            oldest_id = task_checkpoints[0]
            await self.delete_checkpoint(oldest_id)
            task_checkpoints = self._task_checkpoints.get(task_id, [])
    
    async def cleanup_expired(self) -> int:
        """
        Clean up expired checkpoints.
        
        Returns:
            Number of checkpoints removed
        """
        now = datetime.utcnow()
        expired_ids = []
        
        for cid, checkpoint in self._checkpoints.items():
            if checkpoint.expires_at and checkpoint.expires_at < now:
                expired_ids.append(cid)
        
        count = 0
        for cid in expired_ids:
            if await self.delete_checkpoint(cid):
                count += 1
        
        logger.info(f"Cleaned up {count} expired checkpoints")
        return count
    
    # ==========================================================================
    # Persistence
    # ==========================================================================
    
    def _persist_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Persist checkpoint to disk."""
        try:
            checkpoint_file = self._config.storage_path / f"{checkpoint.checkpoint_id}.json"
            
            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint.to_dict(), f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to persist checkpoint: {e}")
    
    def _load_checkpoints(self) -> None:
        """Load checkpoints from disk."""
        try:
            for checkpoint_file in self._config.storage_path.glob("*.json"):
                try:
                    with open(checkpoint_file, "r") as f:
                        data = json.load(f)
                    
                    checkpoint = Checkpoint.from_dict(data)
                    self._checkpoints[checkpoint.checkpoint_id] = checkpoint
                    
                    if checkpoint.task_id:
                        if checkpoint.task_id not in self._task_checkpoints:
                            self._task_checkpoints[checkpoint.task_id] = []
                        self._task_checkpoints[checkpoint.task_id].append(checkpoint.checkpoint_id)
                        
                        # Update sequence counter
                        current_seq = self._sequence_counters.get(checkpoint.task_id, 0)
                        self._sequence_counters[checkpoint.task_id] = max(
                            current_seq, checkpoint.sequence_number
                        )
                    
                except Exception as e:
                    logger.error(f"Failed to load checkpoint from {checkpoint_file}: {e}")
            
            if self._checkpoints:
                logger.info(f"Loaded {len(self._checkpoints)} checkpoints")
                
        except Exception as e:
            logger.error(f"Failed to load checkpoints: {e}")
    
    # ==========================================================================
    # Packet Emission
    # ==========================================================================
    
    async def _emit_checkpoint_packet(
        self,
        checkpoint: Checkpoint,
        event_type: str,
    ) -> None:
        """Emit a PacketEnvelope for checkpoint event."""
        if not self._packet_emitter:
            return
        
        payload = checkpoint.to_packet_payload()
        payload["event_type"] = event_type
        
        try:
            await self._packet_emitter({
                "packet_id": str(uuid4()),
                "packet_type": "checkpoint_event",
                "payload": payload,
                "metadata": {
                    "agent": checkpoint.agent_id,
                    "domain": "checkpoint_manager",
                },
                "tags": ["checkpoint", event_type] + checkpoint.tags,
            })
        except Exception as e:
            logger.error(f"Failed to emit checkpoint packet: {e}")
    
    # ==========================================================================
    # Statistics
    # ==========================================================================
    
    def get_stats(self) -> dict[str, Any]:
        """Get checkpoint statistics."""
        total = len(self._checkpoints)
        valid = sum(1 for c in self._checkpoints.values() if c.status == CheckpointStatus.VALID)
        expired = sum(1 for c in self._checkpoints.values() if c.status == CheckpointStatus.EXPIRED)
        corrupted = sum(1 for c in self._checkpoints.values() if c.status == CheckpointStatus.CORRUPTED)
        
        return {
            "total_checkpoints": total,
            "valid_checkpoints": valid,
            "expired_checkpoints": expired,
            "corrupted_checkpoints": corrupted,
            "tasks_with_checkpoints": len(self._task_checkpoints),
        }

