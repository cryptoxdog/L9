"""
L9 Runtime - Task Queue
========================

Production task queue with Redis backend and in-memory fallback.

Used by ws_bridge and orchestrators to enqueue work items
that are processed by the unified controller.

Version: 2.0.0 (Redis support)

Note: Automatically uses Redis if available, falls back to in-memory.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Try to import Redis client
try:
    from runtime.redis_client import get_redis_client
    _has_redis_client = True
except ImportError:
    _has_redis_client = False
    logger.debug("Redis client not available - using in-memory queue only")


@dataclass
class QueuedTask:
    """A task waiting in the queue."""

    task_id: str
    name: str
    payload: Dict[str, Any]
    handler: str
    agent_id: Optional[str]
    priority: int
    tags: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "payload": self.payload,
            "handler": self.handler,
            "agent_id": self.agent_id,
            "priority": self.priority,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QueuedTask:
        """Deserialize from dict."""
        return cls(
            task_id=data["task_id"],
            name=data["name"],
            payload=data["payload"],
            handler=data["handler"],
            agent_id=data.get("agent_id"),
            priority=data.get("priority", 5),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
        )


class TaskQueue:
    """
    Production task queue with Redis backend and in-memory fallback.
    
    Tasks are ordered by priority (lower = higher priority).
    Automatically uses Redis if available, otherwise falls back to in-memory.
    """

    def __init__(self, queue_name: str = "l9:tasks", use_redis: bool = True) -> None:
        """
        Initialize task queue.
        
        Args:
            queue_name: Queue name for Redis (default: "l9:tasks")
            use_redis: Whether to attempt Redis connection (default: True)
        """
        self._queue_name = queue_name
        self._use_redis = use_redis and _has_redis_client
        self._redis_client = None
        self._queue: deque[QueuedTask] = deque()
        self._lock = asyncio.Lock()
        self._handlers: Dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}
        self._redis_available = False
        
        if self._use_redis:
            # Try to connect to Redis (async, will be checked on first use)
            logger.info(f"TaskQueue initialized with Redis support (queue: {queue_name})")
        else:
            logger.info("TaskQueue initialized (in-memory only)")

    async def _ensure_redis(self) -> bool:
        """Ensure Redis client is connected."""
        if not self._use_redis:
            return False
        
        if self._redis_client is None:
            self._redis_client = await get_redis_client()
            self._redis_available = self._redis_client is not None and self._redis_client.is_available()
            
            if self._redis_available:
                logger.info("TaskQueue: Redis backend active")
            else:
                logger.info("TaskQueue: Redis unavailable, using in-memory fallback")
        
        return self._redis_available

    async def enqueue(
        self,
        name: str,
        payload: Dict[str, Any],
        handler: str = "default",
        agent_id: Optional[str] = None,
        priority: int = 5,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Add a task to the queue.
        
        Args:
            name: Human-readable task name
            payload: Task data
            handler: Handler function name to invoke
            agent_id: Optional target agent
            priority: 1-10, lower is higher priority
            tags: Optional tags for filtering
            
        Returns:
            Task ID
        """
        task = QueuedTask(
            task_id=str(uuid4()),
            name=name,
            payload=payload,
            handler=handler,
            agent_id=agent_id,
            priority=priority,
            tags=tags or [],
        )
        
        # Try Redis first
        if await self._ensure_redis():
            try:
                task_id = await self._redis_client.enqueue_task(
                    self._queue_name,
                    task.to_dict(),
                    priority=priority,
                )
                if task_id:
                    logger.debug(
                        "Enqueued task %s to Redis: name=%s, priority=%d, handler=%s",
                        task_id,
                        name,
                        priority,
                        handler,
                    )
                    return task_id
            except Exception as e:
                logger.warning(f"Redis enqueue failed, falling back to in-memory: {e}")
        
        # Fallback to in-memory
        async with self._lock:
            # Insert in priority order
            inserted = False
            for i, existing in enumerate(self._queue):
                if task.priority < existing.priority:
                    self._queue.insert(i, task)
                    inserted = True
                    break
            if not inserted:
                self._queue.append(task)
        
        logger.debug(
            "Enqueued task %s (in-memory): name=%s, priority=%d, handler=%s",
            task.task_id,
            name,
            priority,
            handler,
        )
        return task.task_id

    async def dequeue(self) -> Optional[QueuedTask]:
        """
        Remove and return the highest priority task.
        
        Returns:
            QueuedTask or None if queue is empty
        """
        # Try Redis first
        if await self._ensure_redis():
            try:
                task_data = await self._redis_client.dequeue_task(self._queue_name)
                if task_data:
                    task = QueuedTask.from_dict(task_data)
                    logger.debug(f"Dequeued task {task.task_id} from Redis")
                    return task
            except Exception as e:
                logger.warning(f"Redis dequeue failed, falling back to in-memory: {e}")
        
        # Fallback to in-memory
        async with self._lock:
            if not self._queue:
                return None
            return self._queue.popleft()

    async def peek(self) -> Optional[QueuedTask]:
        """Return the next task without removing it."""
        # Try Redis first
        if await self._ensure_redis():
            try:
                # Redis doesn't have peek, so we'd need to implement it differently
                # For now, fall back to in-memory peek
                pass
            except Exception:
                pass
        
        # Fallback to in-memory
        async with self._lock:
            if not self._queue:
                return None
            return self._queue[0]

    async def size(self) -> int:
        """Return current queue size."""
        # Try Redis first
        if await self._ensure_redis():
            try:
                redis_size = await self._redis_client.queue_size(self._queue_name)
                # Also check in-memory queue
                async with self._lock:
                    in_memory_size = len(self._queue)
                return redis_size + in_memory_size
            except Exception:
                pass
        
        # Fallback to in-memory
        async with self._lock:
            return len(self._queue)

    def register_handler(
        self,
        name: str,
        handler: Callable[..., Coroutine[Any, Any, Any]],
    ) -> None:
        """
        Register a handler function for a handler name.
        
        Args:
            name: Handler name (e.g., "ws_event_handler")
            handler: Async function to invoke
        """
        self._handlers[name] = handler
        logger.debug("Registered handler: %s", name)

    async def process_one(self) -> bool:
        """
        Process a single task from the queue.
        
        Returns:
            True if a task was processed, False if queue was empty
        """
        task = await self.dequeue()
        if task is None:
            return False

        handler = self._handlers.get(task.handler)
        if handler is None:
            logger.warning("No handler registered for: %s", task.handler)
            return True

        try:
            await handler(task.payload, agent_id=task.agent_id)
            logger.debug("Processed task %s", task.task_id)
        except Exception as e:
            logger.error("Handler %s failed for task %s: %s", task.handler, task.task_id, e)

        return True


__all__ = ["TaskQueue", "QueuedTask"]

