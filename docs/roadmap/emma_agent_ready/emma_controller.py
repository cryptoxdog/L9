"""
Emma Agent Controller — Core orchestration logic.

Implements the main Emma agent controller with:
- Task dispatch and routing
- Memory context assembly
- Governance gate enforcement
- Escalation coordination
- Metrics emission
"""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from emma_agent.modules.memory_manager import MemoryManager
from emma_agent.modules.governance_handler import GovernanceHandler
from emma_agent.modules.escalation_manager import EscalationManager
from emma_agent.infra.database import DatabasePool
from emma_agent.infra.cache import CacheManager
from emma_agent.infra.metrics import MetricsCollector
from emma_agent.infra.health import HealthChecker


logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Task type categories."""
    RESEARCH = "research"
    DECISION = "decision"
    ACTION = "action"
    COORDINATION = "coordination"
    MEMORY = "memory"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


@dataclass
class Task:
    """Task definition with metadata."""
    task_id: str
    task_type: TaskType
    description: str
    parameters: Dict[str, Any]
    created_at: datetime
    created_by: str
    priority: int = 5
    timeout_seconds: float = 300.0
    estimated_cost: float = 0.0
    status: TaskStatus = TaskStatus.PENDING
    correlation_id: str = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None
    correlation_id: Optional[str] = None


class EmmaController:
    """
    Main Emma agent controller.
    
    Orchestrates task execution, memory management, governance, and escalation.
    """

    def __init__(
        self,
        db_pool: DatabasePool,
        cache_manager: CacheManager,
        memory_manager: MemoryManager,
        governance_handler: GovernanceHandler,
        escalation_manager: EscalationManager,
        metrics_collector: MetricsCollector,
        health_checker: HealthChecker,
    ) -> None:
        """
        Initialize Emma controller.
        
        Args:
            db_pool: Database connection pool
            cache_manager: Redis cache manager
            memory_manager: Unified memory backend
            governance_handler: Governance policy enforcer
            escalation_manager: Escalation workflow coordinator
            metrics_collector: Prometheus metrics
            health_checker: Health check manager
        """
        self.db_pool = db_pool
        self.cache_manager = cache_manager
        self.memory_manager = memory_manager
        self.governance_handler = governance_handler
        self.escalation_manager = escalation_manager
        self.metrics_collector = metrics_collector
        self.health_checker = health_checker

        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}

        logger.info("EmmaController initialized")

    async def initialize(self) -> None:
        """Initialize all subsystems."""
        logger.info("Initializing Emma subsystems")

        await self.db_pool.initialize()
        await self.cache_manager.initialize()
        await self.memory_manager.initialize()
        await self.governance_handler.initialize()
        await self.escalation_manager.initialize()

        logger.info("Emma subsystems initialized")

    async def shutdown(self) -> None:
        """Shutdown all subsystems gracefully."""
        logger.info("Shutting down Emma")

        await self.escalation_manager.shutdown()
        await self.governance_handler.shutdown()
        await self.memory_manager.shutdown()
        await self.cache_manager.shutdown()
        await self.db_pool.shutdown()

        logger.info("Emma shutdown complete")

    async def submit_task(self, task: Task) -> str:
        """
        Submit task for execution.
        
        Args:
            task: Task to execute
            
        Returns:
            Task ID
            
        Raises:
            ValueError: If task is invalid
        """
        if not task.task_id:
            task.task_id = str(uuid.uuid4())

        logger.info(
            f"Task submitted: {task.task_id}",
            extra={
                "task_type": task.task_type.value,
                "priority": task.priority,
                "correlation_id": task.correlation_id,
            },
        )

        self.active_tasks[task.task_id] = task
        await self.task_queue.put(task)

        # Emit metric
        self.metrics_collector.increment("emma.tasks.submitted", tags={
            "type": task.task_type.value,
        })

        return task.task_id

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a single task with governance gating.
        
        Args:
            task: Task to execute
            
        Returns:
            Task result
        """
        start_time = datetime.utcnow()
        task.status = TaskStatus.RUNNING

        try:
            logger.info(
                f"Executing task: {task.task_id}",
                extra={"correlation_id": task.correlation_id},
            )

            # Step 1: Governance gate
            gate_decision = await self.governance_handler.evaluate_gate(task)

            if gate_decision == "ESCALATE":
                logger.warning(
                    f"Task escalated: {task.task_id}",
                    extra={"correlation_id": task.correlation_id},
                )

                escalation_id = await self.escalation_manager.create_escalation(task)

                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.ESCALATED,
                    error=f"Escalated to {escalation_id}",
                    correlation_id=task.correlation_id,
                )

            # Step 2: Memory context assembly
            memory_context = await self.memory_manager.assemble_context(task)

            # Step 3: Execute task based on type
            if task.task_type == TaskType.RESEARCH:
                result = await self._execute_research(task, memory_context)
            elif task.task_type == TaskType.DECISION:
                result = await self._execute_decision(task, memory_context)
            elif task.task_type == TaskType.ACTION:
                result = await self._execute_action(task, memory_context)
            elif task.task_type == TaskType.COORDINATION:
                result = await self._execute_coordination(task, memory_context)
            elif task.task_type == TaskType.MEMORY:
                result = await self._execute_memory(task, memory_context)
            else:
                result = None

            task.status = TaskStatus.COMPLETED

            duration = (datetime.utcnow() - start_time).total_seconds()

            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                duration_seconds=duration,
                correlation_id=task.correlation_id,
            )

            # Store result
            self.completed_tasks[task.task_id] = task_result

            # Emit metrics
            self.metrics_collector.histogram("emma.task.duration", duration, tags={
                "type": task.task_type.value,
                "status": "success",
            })

            logger.info(
                f"Task completed: {task.task_id}",
                extra={
                    "duration": duration,
                    "correlation_id": task.correlation_id,
                },
            )

            return task_result

        except Exception as e:
            logger.error(
                f"Task failed: {task.task_id}: {str(e)}",
                extra={"correlation_id": task.correlation_id},
                exc_info=True,
            )

            task.status = TaskStatus.FAILED
            duration = (datetime.utcnow() - start_time).total_seconds()

            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                duration_seconds=duration,
                correlation_id=task.correlation_id,
            )

            self.completed_tasks[task.task_id] = task_result

            # Emit metrics
            self.metrics_collector.histogram("emma.task.duration", duration, tags={
                "type": task.task_type.value,
                "status": "failure",
            })

            return task_result

    async def _execute_research(
        self,
        task: Task,
        memory_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute research task."""
        # TODO: Implement research execution logic
        logger.info(f"Executing research task: {task.task_id}")
        return {"status": "research_complete"}

    async def _execute_decision(
        self,
        task: Task,
        memory_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute decision task."""
        # TODO: Implement decision execution logic
        logger.info(f"Executing decision task: {task.task_id}")
        return {"status": "decision_made"}

    async def _execute_action(
        self,
        task: Task,
        memory_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute action task."""
        # TODO: Implement action execution logic
        logger.info(f"Executing action task: {task.task_id}")
        return {"status": "action_complete"}

    async def _execute_coordination(
        self,
        task: Task,
        memory_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute coordination task."""
        # TODO: Implement coordination execution logic
        logger.info(f"Executing coordination task: {task.task_id}")
        return {"status": "coordination_complete"}

    async def _execute_memory(
        self,
        task: Task,
        memory_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute memory task."""
        # TODO: Implement memory execution logic
        logger.info(f"Executing memory task: {task.task_id}")
        return {"status": "memory_operation_complete"}

    async def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """Get task result."""
        return self.completed_tasks.get(task_id)

    async def get_active_tasks(self) -> List[Task]:
        """Get list of active tasks."""
        return list(self.active_tasks.values())

    async def health_check(self) -> Dict[str, Any]:
        """Health check all subsystems."""
        return await self.health_checker.check()
