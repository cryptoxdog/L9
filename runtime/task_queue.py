"""
L9 Runtime - Task Queue
=======================
Version: 2.0.0

Deterministic, resumable task queue with async processing.

Features:
- Priority-based scheduling
- Background execution
- Task cancellation + restart
- Persistence and recovery
- PacketEnvelope emission
- Agent coordination

Compatibility:
- Memory substrate (PacketEnvelope v1.1.0)
- World model integration
- IR Engine integration
"""

from __future__ import annotations

import asyncio
import heapq
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Any, Callable, Optional, Awaitable, Union
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Constants
# =============================================================================

class TaskPriority(IntEnum):
    """Task priority levels (lower = higher priority)."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class TaskExecutionStatus(str):
    """Task execution status constants."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RESTARTING = "restarting"


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class QueuedTask:
    """A task in the queue with full execution metadata."""
    task_id: UUID = field(default_factory=uuid4)
    name: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    payload: dict[str, Any] = field(default_factory=dict)
    handler: Optional[str] = None
    status: str = TaskExecutionStatus.QUEUED
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    # Agent and lineage tracking
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    parent_task_id: Optional[UUID] = None
    child_task_ids: list[UUID] = field(default_factory=list)
    # Packet tracking
    source_packet_id: Optional[UUID] = None
    emitted_packet_ids: list[UUID] = field(default_factory=list)
    # Checkpoint support
    checkpoint_id: Optional[str] = None
    checkpoint_data: Optional[dict[str, Any]] = None
    # Execution metadata
    execution_count: int = 0
    last_error: Optional[str] = None
    worker_id: Optional[int] = None
    tags: list[str] = field(default_factory=list)
    
    def __lt__(self, other: QueuedTask) -> bool:
        """Compare for heap ordering."""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.created_at < other.created_at
    
    def __hash__(self) -> int:
        """Hash by task_id for set operations."""
        return hash(self.task_id)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "task_id": str(self.task_id),
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status,
            "retries": self.retries,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "parent_task_id": str(self.parent_task_id) if self.parent_task_id else None,
            "child_task_ids": [str(c) for c in self.child_task_ids],
            "source_packet_id": str(self.source_packet_id) if self.source_packet_id else None,
            "emitted_packet_ids": [str(p) for p in self.emitted_packet_ids],
            "checkpoint_id": self.checkpoint_id,
            "execution_count": self.execution_count,
            "last_error": self.last_error,
            "worker_id": self.worker_id,
            "tags": self.tags,
            "payload": self.payload,
            "result": self.result,
            "error": self.error,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QueuedTask:
        """Deserialize from dictionary."""
        return cls(
            task_id=UUID(data["task_id"]) if data.get("task_id") else uuid4(),
            name=data.get("name", ""),
            priority=TaskPriority[data.get("priority", "NORMAL")],
            status=data.get("status", TaskExecutionStatus.QUEUED),
            retries=data.get("retries", 0),
            max_retries=data.get("max_retries", 3),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            cancelled_at=datetime.fromisoformat(data["cancelled_at"]) if data.get("cancelled_at") else None,
            agent_id=data.get("agent_id"),
            session_id=data.get("session_id"),
            parent_task_id=UUID(data["parent_task_id"]) if data.get("parent_task_id") else None,
            child_task_ids=[UUID(c) for c in data.get("child_task_ids", [])],
            source_packet_id=UUID(data["source_packet_id"]) if data.get("source_packet_id") else None,
            emitted_packet_ids=[UUID(p) for p in data.get("emitted_packet_ids", [])],
            checkpoint_id=data.get("checkpoint_id"),
            checkpoint_data=data.get("checkpoint_data"),
            execution_count=data.get("execution_count", 0),
            last_error=data.get("last_error"),
            worker_id=data.get("worker_id"),
            tags=data.get("tags", []),
            payload=data.get("payload", {}),
            result=data.get("result"),
            error=data.get("error"),
        )
    
    def to_packet_payload(self) -> dict[str, Any]:
        """Generate payload for PacketEnvelope emission."""
        return {
            "kind": "task_event",
            "task_id": str(self.task_id),
            "name": self.name,
            "status": self.status,
            "priority": self.priority.name,
            "agent_id": self.agent_id,
            "execution_count": self.execution_count,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class QueueConfig:
    """Configuration for task queue."""
    max_size: int = 10000
    max_workers: int = 4
    worker_timeout_ms: int = 60000
    retry_delay_ms: int = 1000
    rate_limit_per_second: Optional[float] = None
    enable_deduplication: bool = True
    persistence_path: Optional[Path] = None
    emit_packets: bool = True
    background_mode: bool = False
    checkpoint_interval_ms: int = 5000
    graceful_shutdown_timeout_ms: int = 30000


@dataclass
class QueueStats:
    """Queue statistics."""
    queued_count: int = 0
    processing_count: int = 0
    completed_count: int = 0
    failed_count: int = 0
    cancelled_count: int = 0
    total_processed: int = 0
    average_wait_ms: float = 0.0
    average_process_ms: float = 0.0
    total_retries: int = 0
    workers_active: int = 0


# =============================================================================
# Handler Types
# =============================================================================

TaskHandler = Union[
    Callable[[dict[str, Any]], dict[str, Any]],
    Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
]


# =============================================================================
# Task Queue Implementation
# =============================================================================

class TaskQueue:
    """
    Priority task queue with deterministic, resumable execution.
    
    Features:
    - Priority-based scheduling
    - Background execution
    - Task cancellation + restart
    - Persistence and recovery
    - PacketEnvelope emission
    - Multiple async workers
    """
    
    def __init__(self, config: Optional[QueueConfig] = None):
        """
        Initialize the task queue.
        
        Args:
            config: Queue configuration
        """
        self._config = config or QueueConfig()
        self._queue: list[QueuedTask] = []
        self._processing: dict[UUID, QueuedTask] = {}
        self._completed: list[QueuedTask] = []
        self._cancelled: dict[UUID, QueuedTask] = {}
        self._handlers: dict[str, TaskHandler] = {}
        self._running = False
        self._workers: list[asyncio.Task] = []
        self._task_ids: set[UUID] = set()
        self._stats = QueueStats()
        self._rate_limiter: Optional[asyncio.Semaphore] = None
        self._shutdown_event: Optional[asyncio.Event] = None
        self._packet_emitter: Optional[Callable] = None
        self._lock = asyncio.Lock()
        self._background_task: Optional[asyncio.Task] = None
        
        # Load persisted state
        if self._config.persistence_path:
            self._load_state()
        
        logger.info(f"TaskQueue initialized (max_workers={self._config.max_workers})")
    
    # ==========================================================================
    # Handler Registration
    # ==========================================================================
    
    def register_handler(
        self,
        name: str,
        handler: TaskHandler,
    ) -> None:
        """
        Register a task handler.
        
        Args:
            name: Handler name
            handler: Handler function (sync or async)
        """
        self._handlers[name] = handler
        logger.debug(f"Registered handler: {name}")
    
    def unregister_handler(self, name: str) -> bool:
        """
        Unregister a task handler.
        
        Args:
            name: Handler name
            
        Returns:
            True if handler was removed
        """
        if name in self._handlers:
            del self._handlers[name]
            logger.debug(f"Unregistered handler: {name}")
            return True
        return False
    
    def get_handler(self, name: str) -> Optional[TaskHandler]:
        """Get a registered handler."""
        return self._handlers.get(name)
    
    def set_packet_emitter(self, emitter: Callable) -> None:
        """Set the packet emitter function for PacketEnvelope emission."""
        self._packet_emitter = emitter
    
    # ==========================================================================
    # Queue Operations
    # ==========================================================================
    
    async def enqueue(
        self,
        name: str,
        payload: dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        handler: Optional[str] = None,
        max_retries: int = 3,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        parent_task_id: Optional[UUID] = None,
        source_packet_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
    ) -> QueuedTask:
        """
        Add a task to the queue.
        
        Args:
            name: Task name
            payload: Task payload
            priority: Task priority
            handler: Handler name
            max_retries: Maximum retry attempts
            agent_id: Agent identifier
            session_id: Session identifier
            parent_task_id: Parent task for hierarchical tracking
            source_packet_id: Source packet that triggered this task
            tags: Task tags
            
        Returns:
            QueuedTask
        """
        async with self._lock:
            if len(self._queue) >= self._config.max_size:
                raise RuntimeError("Queue is full")
            
            task = QueuedTask(
                name=name,
                priority=priority,
                payload=payload,
                handler=handler or name,
                max_retries=max_retries,
                agent_id=agent_id,
                session_id=session_id,
                parent_task_id=parent_task_id,
                source_packet_id=source_packet_id,
                tags=tags or [],
            )
            
            # Deduplication check
            if self._config.enable_deduplication:
                if task.task_id in self._task_ids:
                    logger.warning(f"Duplicate task rejected: {task.task_id}")
                    return task
            
            heapq.heappush(self._queue, task)
            self._task_ids.add(task.task_id)
            self._stats.queued_count += 1
            
            # Link to parent task
            if parent_task_id:
                parent = self.get_task(parent_task_id)
                if parent:
                    parent.child_task_ids.append(task.task_id)
            
            # Emit packet
            await self._emit_task_packet(task, "task_enqueued")
            
            # Persist state
            self._persist_state()
            
            logger.debug(f"Enqueued task: {task.name} (priority={priority.name}, id={task.task_id})")
            
            return task
    
    def enqueue_sync(
        self,
        name: str,
        payload: dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        handler: Optional[str] = None,
        max_retries: int = 3,
        agent_id: Optional[str] = None,
    ) -> QueuedTask:
        """
        Synchronously add a task to the queue.
        
        Args:
            name: Task name
            payload: Task payload
            priority: Task priority
            handler: Handler name
            max_retries: Maximum retry attempts
            agent_id: Agent identifier
            
        Returns:
            QueuedTask
        """
        if len(self._queue) >= self._config.max_size:
            raise RuntimeError("Queue is full")
        
        task = QueuedTask(
            name=name,
            priority=priority,
            payload=payload,
            handler=handler or name,
            max_retries=max_retries,
            agent_id=agent_id,
        )
        
        if self._config.enable_deduplication:
            if task.task_id in self._task_ids:
                logger.warning(f"Duplicate task rejected: {task.task_id}")
                return task
        
        heapq.heappush(self._queue, task)
        self._task_ids.add(task.task_id)
        self._stats.queued_count += 1
        
        logger.debug(f"Enqueued task (sync): {task.name}")
        
        return task
    
    async def dequeue(self) -> Optional[QueuedTask]:
        """
        Get the next task from queue.
        
        Returns:
            Next QueuedTask or None
        """
        async with self._lock:
            if not self._queue:
                return None
            
            task = heapq.heappop(self._queue)
            task.status = TaskExecutionStatus.PROCESSING
            task.started_at = datetime.utcnow()
            task.execution_count += 1
            
            self._processing[task.task_id] = task
            self._stats.queued_count -= 1
            self._stats.processing_count += 1
            
            return task
    
    async def complete_task(
        self,
        task_id: UUID,
        result: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task ID
            result: Task result
            
        Returns:
            True if completed
        """
        async with self._lock:
            task = self._processing.get(task_id)
            if not task:
                return False
            
            task.status = TaskExecutionStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            
            del self._processing[task_id]
            self._completed.append(task)
            
            self._stats.processing_count -= 1
            self._stats.completed_count += 1
            self._stats.total_processed += 1
            
            # Update average processing time
            if task.started_at:
                process_ms = (task.completed_at - task.started_at).total_seconds() * 1000
                self._update_average_process_time(process_ms)
            
            # Emit packet
            await self._emit_task_packet(task, "task_completed")
            
            # Persist state
            self._persist_state()
            
            logger.info(f"Task completed: {task_id}")
            
            return True
    
    async def fail_task(
        self,
        task_id: UUID,
        error: str,
        retry: bool = True,
    ) -> bool:
        """
        Mark a task as failed.
        
        Args:
            task_id: Task ID
            error: Error message
            retry: Whether to retry
            
        Returns:
            True if handled
        """
        async with self._lock:
            task = self._processing.get(task_id)
            if not task:
                return False
            
            del self._processing[task_id]
            self._stats.processing_count -= 1
            
            if retry and task.retries < task.max_retries:
                # Re-queue with incremented retry
                task.status = TaskExecutionStatus.QUEUED
                task.retries += 1
                task.last_error = error
                task.started_at = None
                task.worker_id = None
                
                self._stats.total_retries += 1
                
                # Delay before retry
                if self._config.retry_delay_ms > 0:
                    await asyncio.sleep(self._config.retry_delay_ms / 1000)
                
                heapq.heappush(self._queue, task)
                self._stats.queued_count += 1
                
                await self._emit_task_packet(task, "task_retrying")
                
                logger.info(f"Re-queued task {task_id} (retry {task.retries})")
            else:
                task.status = TaskExecutionStatus.FAILED
                task.error = error
                task.last_error = error
                task.completed_at = datetime.utcnow()
                
                self._completed.append(task)
                self._stats.failed_count += 1
                self._stats.total_processed += 1
                
                await self._emit_task_packet(task, "task_failed")
                
                logger.warning(f"Task {task_id} failed: {error}")
            
            self._persist_state()
            
            return True
    
    async def cancel_task(
        self,
        task_id: UUID,
        reason: str = "",
    ) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: Task ID
            reason: Cancellation reason
            
        Returns:
            True if cancelled
        """
        async with self._lock:
            # Check if in queue
            for i, task in enumerate(self._queue):
                if task.task_id == task_id:
                    self._queue.pop(i)
                    heapq.heapify(self._queue)
                    
                    task.status = TaskExecutionStatus.CANCELLED
                    task.cancelled_at = datetime.utcnow()
                    task.error = reason or "Cancelled by user"
                    
                    self._cancelled[task_id] = task
                    self._stats.queued_count -= 1
                    self._stats.cancelled_count += 1
                    
                    await self._emit_task_packet(task, "task_cancelled")
                    
                    logger.info(f"Task cancelled from queue: {task_id}")
                    self._persist_state()
                    return True
            
            # Check if processing
            if task_id in self._processing:
                task = self._processing[task_id]
                task.status = TaskExecutionStatus.CANCELLED
                task.cancelled_at = datetime.utcnow()
                task.error = reason or "Cancelled by user"
                
                del self._processing[task_id]
                self._cancelled[task_id] = task
                self._stats.processing_count -= 1
                self._stats.cancelled_count += 1
                
                await self._emit_task_packet(task, "task_cancelled")
                
                logger.info(f"Task cancelled while processing: {task_id}")
                self._persist_state()
                return True
            
            return False
    
    async def restart_task(
        self,
        task_id: UUID,
        reset_retries: bool = False,
    ) -> Optional[QueuedTask]:
        """
        Restart a cancelled or failed task.
        
        Args:
            task_id: Task ID
            reset_retries: Whether to reset retry count
            
        Returns:
            Restarted task or None
        """
        async with self._lock:
            # Find in cancelled
            task = self._cancelled.get(task_id)
            
            # Find in completed (failed)
            if not task:
                for t in self._completed:
                    if t.task_id == task_id and t.status == TaskExecutionStatus.FAILED:
                        task = t
                        self._completed.remove(t)
                        break
            
            if not task:
                logger.warning(f"Task not found for restart: {task_id}")
                return None
            
            # Remove from cancelled
            if task_id in self._cancelled:
                del self._cancelled[task_id]
                self._stats.cancelled_count -= 1
            
            # Reset task
            task.status = TaskExecutionStatus.RESTARTING
            if reset_retries:
                task.retries = 0
            task.error = None
            task.last_error = None
            task.started_at = None
            task.completed_at = None
            task.cancelled_at = None
            task.result = None
            task.worker_id = None
            
            # Re-queue
            task.status = TaskExecutionStatus.QUEUED
            heapq.heappush(self._queue, task)
            self._stats.queued_count += 1
            
            await self._emit_task_packet(task, "task_restarted")
            
            logger.info(f"Task restarted: {task_id}")
            self._persist_state()
            
            return task
    
    # ==========================================================================
    # Worker Management
    # ==========================================================================
    
    async def start(self, background: bool = False) -> None:
        """
        Start the queue workers.
        
        Args:
            background: Run in background mode
        """
        if self._running:
            return
        
        self._running = True
        self._shutdown_event = asyncio.Event()
        
        # Create rate limiter if configured
        if self._config.rate_limit_per_second:
            self._rate_limiter = asyncio.Semaphore(
                int(self._config.rate_limit_per_second)
            )
        
        # Start workers
        for i in range(self._config.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)
        
        self._stats.workers_active = len(self._workers)
        
        # Background mode handling
        if background or self._config.background_mode:
            self._background_task = asyncio.create_task(self._background_monitor())
        
        logger.info(f"Started {len(self._workers)} workers (background={background})")
    
    async def stop(self, wait: bool = True) -> None:
        """
        Stop the queue workers.
        
        Args:
            wait: Whether to wait for current tasks
        """
        self._running = False
        
        if self._shutdown_event:
            self._shutdown_event.set()
        
        if wait:
            # Graceful shutdown with timeout
            timeout = self._config.graceful_shutdown_timeout_ms / 1000
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._workers, return_exceptions=True),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                logger.warning("Graceful shutdown timed out, forcing worker cancellation")
                for worker in self._workers:
                    worker.cancel()
        else:
            # Force cancel
            for worker in self._workers:
                worker.cancel()
        
        # Stop background monitor
        if self._background_task:
            self._background_task.cancel()
            self._background_task = None
        
        self._workers.clear()
        self._stats.workers_active = 0
        
        # Persist final state
        self._persist_state()
        
        logger.info("Workers stopped")
    
    async def _worker(self, worker_id: int) -> None:
        """Worker coroutine."""
        logger.debug(f"Worker {worker_id} started")
        
        while self._running:
            # Check shutdown signal
            if self._shutdown_event and self._shutdown_event.is_set():
                break
            
            # Get next task
            task = await self.dequeue()
            
            if not task:
                await asyncio.sleep(0.1)
                continue
            
            task.worker_id = worker_id
            
            # Rate limiting
            if self._rate_limiter:
                async with self._rate_limiter:
                    await self._process_task(task, worker_id)
            else:
                await self._process_task(task, worker_id)
        
        logger.debug(f"Worker {worker_id} stopped")
    
    async def _process_task(self, task: QueuedTask, worker_id: int) -> None:
        """Process a single task."""
        logger.debug(f"Worker {worker_id} processing: {task.name}")
        
        try:
            handler = self._handlers.get(task.handler)
            
            if handler:
                # Execute handler
                result = handler(task.payload)
                
                # Handle async handlers
                if asyncio.iscoroutine(result):
                    result = await asyncio.wait_for(
                        result,
                        timeout=self._config.worker_timeout_ms / 1000,
                    )
                
                await self.complete_task(task.task_id, result)
            else:
                await self.fail_task(task.task_id, f"No handler: {task.handler}", retry=False)
            
        except asyncio.TimeoutError:
            await self.fail_task(task.task_id, "Task timeout")
        except asyncio.CancelledError:
            await self.fail_task(task.task_id, "Task cancelled", retry=False)
            raise
        except Exception as e:
            await self.fail_task(task.task_id, str(e))
    
    async def _background_monitor(self) -> None:
        """Background monitoring task."""
        checkpoint_interval = self._config.checkpoint_interval_ms / 1000
        
        while self._running:
            try:
                await asyncio.sleep(checkpoint_interval)
                
                # Periodic checkpoint
                self._persist_state()
                
                # Log stats
                logger.debug(
                    f"Queue stats: queued={self._stats.queued_count}, "
                    f"processing={self._stats.processing_count}, "
                    f"completed={self._stats.completed_count}"
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background monitor error: {e}")
    
    def _update_average_process_time(self, process_ms: float) -> None:
        """Update average processing time."""
        total = self._stats.total_processed
        if total == 1:
            self._stats.average_process_ms = process_ms
        else:
            self._stats.average_process_ms = (
                (self._stats.average_process_ms * (total - 1) + process_ms) / total
            )
    
    # ==========================================================================
    # Packet Emission
    # ==========================================================================
    
    async def _emit_task_packet(self, task: QueuedTask, event_type: str) -> None:
        """Emit a PacketEnvelope for task event."""
        if not self._config.emit_packets:
            return
        
        packet_id = uuid4()
        task.emitted_packet_ids.append(packet_id)
        
        payload = task.to_packet_payload()
        payload["event_type"] = event_type
        
        if self._packet_emitter:
            try:
                await self._packet_emitter({
                    "packet_id": str(packet_id),
                    "packet_type": "task_event",
                    "payload": payload,
                    "metadata": {
                        "agent": task.agent_id,
                        "domain": "task_runtime",
                    },
                    "tags": ["task", event_type] + task.tags,
                })
            except Exception as e:
                logger.error(f"Failed to emit task packet: {e}")
    
    # ==========================================================================
    # Persistence
    # ==========================================================================
    
    def _persist_state(self) -> None:
        """Persist queue state to disk."""
        if not self._config.persistence_path:
            return
        
        try:
            self._config.persistence_path.mkdir(parents=True, exist_ok=True)
            
            state = {
                "queue": [t.to_dict() for t in self._queue],
                "processing": {str(k): v.to_dict() for k, v in self._processing.items()},
                "completed": [t.to_dict() for t in self._completed[-100:]],  # Keep last 100
                "cancelled": {str(k): v.to_dict() for k, v in self._cancelled.items()},
                "stats": {
                    "queued_count": self._stats.queued_count,
                    "processing_count": self._stats.processing_count,
                    "completed_count": self._stats.completed_count,
                    "failed_count": self._stats.failed_count,
                    "cancelled_count": self._stats.cancelled_count,
                    "total_processed": self._stats.total_processed,
                },
                "persisted_at": datetime.utcnow().isoformat(),
            }
            
            state_file = self._config.persistence_path / "queue_state.json"
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to persist state: {e}")
    
    def _load_state(self) -> None:
        """Load queue state from disk."""
        if not self._config.persistence_path:
            return
        
        state_file = self._config.persistence_path / "queue_state.json"
        if not state_file.exists():
            return
        
        try:
            with open(state_file, "r") as f:
                state = json.load(f)
            
            # Restore queue
            for task_data in state.get("queue", []):
                task = QueuedTask.from_dict(task_data)
                heapq.heappush(self._queue, task)
                self._task_ids.add(task.task_id)
            
            # Restore processing (move back to queue)
            for task_data in state.get("processing", {}).values():
                task = QueuedTask.from_dict(task_data)
                task.status = TaskExecutionStatus.QUEUED
                task.started_at = None
                heapq.heappush(self._queue, task)
                self._task_ids.add(task.task_id)
            
            # Restore cancelled
            for task_id, task_data in state.get("cancelled", {}).items():
                task = QueuedTask.from_dict(task_data)
                self._cancelled[UUID(task_id)] = task
            
            # Restore stats
            saved_stats = state.get("stats", {})
            self._stats.queued_count = len(self._queue)
            self._stats.completed_count = saved_stats.get("completed_count", 0)
            self._stats.failed_count = saved_stats.get("failed_count", 0)
            self._stats.cancelled_count = len(self._cancelled)
            self._stats.total_processed = saved_stats.get("total_processed", 0)
            
            logger.info(f"Loaded state: {len(self._queue)} queued tasks")
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
    
    # ==========================================================================
    # Status and Query
    # ==========================================================================
    
    def get_stats(self) -> QueueStats:
        """Get queue statistics."""
        return self._stats
    
    def get_queue_length(self) -> int:
        """Get number of queued tasks."""
        return len(self._queue)
    
    def get_processing_count(self) -> int:
        """Get number of tasks being processed."""
        return len(self._processing)
    
    def get_task(self, task_id: UUID) -> Optional[QueuedTask]:
        """Get a task by ID."""
        # Check processing
        if task_id in self._processing:
            return self._processing[task_id]
        
        # Check cancelled
        if task_id in self._cancelled:
            return self._cancelled[task_id]
        
        # Check queue
        for task in self._queue:
            if task.task_id == task_id:
                return task
        
        # Check completed
        for task in self._completed:
            if task.task_id == task_id:
                return task
        
        return None
    
    def get_tasks_by_agent(self, agent_id: str) -> list[QueuedTask]:
        """Get all tasks for an agent."""
        result = []
        
        for task in self._queue:
            if task.agent_id == agent_id:
                result.append(task)
        
        for task in self._processing.values():
            if task.agent_id == agent_id:
                result.append(task)
        
        return result
    
    def get_tasks_by_status(self, status: str) -> list[QueuedTask]:
        """Get tasks with a specific status."""
        if status == TaskExecutionStatus.QUEUED:
            return list(self._queue)
        elif status == TaskExecutionStatus.PROCESSING:
            return list(self._processing.values())
        elif status == TaskExecutionStatus.CANCELLED:
            return list(self._cancelled.values())
        elif status in (TaskExecutionStatus.COMPLETED, TaskExecutionStatus.FAILED):
            return [t for t in self._completed if t.status == status]
        
        return []
    
    def get_queued_tasks(self) -> list[QueuedTask]:
        """Get all queued tasks (sorted by priority)."""
        return sorted(self._queue)
    
    def get_completed_tasks(self, limit: int = 100) -> list[QueuedTask]:
        """Get recently completed tasks."""
        return self._completed[-limit:]
    
    def clear_queue(self) -> int:
        """
        Clear all queued tasks.
        
        Returns:
            Number of tasks cleared
        """
        count = len(self._queue)
        self._queue.clear()
        self._stats.queued_count = 0
        self._persist_state()
        return count
    
    def is_running(self) -> bool:
        """Check if queue is running."""
        return self._running
