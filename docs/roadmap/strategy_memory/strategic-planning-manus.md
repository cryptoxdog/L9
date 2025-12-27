Strategy Memory needs to sit in three places in your current OS: (1) inside the task/plan execution path, (2) on the memory substrate boundary, and (3) behind your HTTP/WS front doors (lchat, Slack, etc.). The spec you have is already compatible with your Executor/TaskGraph/Kernel stack.[1][2][3][4]

## 1. Where Strategy Memory lives in your runtime

Given your repo layout, Strategy Memory should be treated as a new subsystem, not a planner replacement:[4]

- **Front doors:**  
  - `api/server.py` (main FastAPI app: OS + agent + memory routes).  
  - `api/websocket_orchestrator.py` / `wsbridge.py` (WS orchestration).[4]

- **Core execution path:**  
  - `core/agents/executor.py` (AgentExecutorService, runs AgentTask/TaskGraph).  
  - `orchestration/unifiedcontroller.py` + `planexecutor.py` + `taskrouter.py` (plan building/execution).[4]

- **Memory substrate / retrieval:**  
  - `memory/substrate_retriever.py` and related memory helpers.  
  - Neo4j is referenced from the Strategy Memory docs; you’ll mount this as a dedicated **strategy store** service called from executor/plan paths.[2][3][5][1]

Strategy Memory will be a service class (e.g. `StrategyMemoryService`) used by the executor/plan layer, plus a small “bridge” in the memory substrate layer to share embeddings and context.[1][2]

## 2. Core wiring inside the execution engine

The main loop from the Strategy Memory docs maps almost one‑to‑one to your existing execution stack:[2][1][4]

- **Step A – Task comes in:**  
  - For HTTP: request hits `lchat` (to be added in `api/server.py`) or Slack → `slacktaskrouter.py` → `UnifiedController`.[4]
  - For background tasks: go through `taskqueue.py` into `planexecutor.py`.[4]

- **Step B – Before planning a new graph, query Strategy Memory:**  
  - In `planexecutor.py` (or `unifiedcontroller.py`, wherever you currently build a `TaskGraph`), insert a call:
    - Get **task embedding** via your existing semantic layer (the same vector you already use in `substrate_retriever.py`).[1][2]
    - Call `StrategyMemoryService.retrieve_strategies(task_embedding, goal_description, context)` which:
      - Runs Neo4j query as specified (embedding + graph + tags, 40/40/20, threshold 0.6).[3][5][1]
      - Returns top‑K strategies + confidence + a ready‑to‑consume **task network** structure.[5][3][1]
  - If at least one strategy passes confidence/score thresholds, treat it as the **candidate plan** instead of calling your normal “de novo” planner.[6][2][1]
  - If no match or low confidence, fall back to your existing planning path (current TaskGraph/plan building logic).[6][1]

- **Step C – Adapt and execute the retrieved plan:**  
  - You don’t have RAFA, so the “adapter” is just a thin function in `planexecutor.py` or a new module:
    - Input: retrieved strategy graph (HTN‑like), current task context.  
    - Output: adapted `TaskGraph` or equivalent internal plan and a numeric `confidence`.[2][1]
  - Pass this adapted `TaskGraph` into the existing execution flow (AgentExecutorService, TaskQueue, etc.) exactly as a “normal” plan.[4]

This keeps Strategy Memory orthogonal: it **proposes** a plan; your existing executor runs it.

## 3. Auto‑score & prune loop wiring (keep only good plans)

Your requirement “auto update and auto score plans and outcomes to only keep the best ones” is already fully specified; you just bind it to your actual execution completion point.[3][5][6][1][2]

Where to hook:

- **Execution result hook:**  
  - In `core/agents/executor.py` or `planexecutor.py` where a `TaskGraph` or `AgentTask` finishes:
    - Compute `outcome_score` from:
      - `success` boolean.  
      - `execution_time_ms` vs baseline.  
      - `resource_cost`.[5][3][1][2]
    - Emit a `StrategyFeedback` packet (same shape as in Strategy Memory docs) or directly call:
      - `StrategyMemoryService.update_strategy(strategy_id, outcome, metrics)` which:
        - Updates `Strategy.performance_score` via exponential smoothing.[3][5][1]
        - Updates `generality_score`, `failure_rate`, `usage_count`, `last_used`, `age_days`.[5][1][2][3]
        - Inserts an `Execution` node with full metrics.[2][3][5]

- **Pruning and drift:**  
  - Add a **scheduled job** (cron, background task, or periodic maintenance path) that runs the Cypher from `strategy_memory_visual_guide.md` / `strategy_memory_checklist.md`:
    - Delete or archive strategies where `performance_score < 0.3 AND age_days > 30`.  
    - Delete old `Execution` nodes beyond 90 days or keep the last N per strategy.[3][2]
    - Recompute `usage_count` and `generality_score`.[5][2][3]

This gives you the “don’t repeat bad plans” behaviour without any additional learning layer: retrieval prefers high‑score, recent strategies; pruning keeps the library clean.[1][2][3][5]

## 4. Memory substrate + embeddings integration

The Strategy Memory spec expects to reuse your existing memory and embedding machinery rather than duplicating it.[6][1][2][3][5]

- **Embedding source:**  
  - Use whatever component `substrate_retriever.py` uses to generate 384‑dim embeddings; Strategy Memory’s `Strategy.context_embedding` field assumes the same dimensionality and model.[1][2][5]

- **Packet envelopes:**  
  - Extend your existing packet protocol wiring (`packetprotocolwiring.py` / similar) with:
    - `StrategyRequest` metadata/payload models.  
    - `StrategyResponse`.  
    - `StrategyFeedback`.[3][5][1]
  - These are just new `PacketEnvelope` variants flowing on the same substrate bus as your current memory packets.[2][5][1][3]

- **Strategy capture:**  
  - When a plan is created de novo, after execution success, create a new `Strategy` node in Neo4j with:
    - `context_embedding` from the incoming task.  
    - `graph_signature` as a hash of the TaskGraph / plan JSON.  
    - Initial `performance_score = 1.0`, `generality_score = 0.0`, `tags`, etc.[5][1][3]

This means: every successful fresh plan is eligible to become a reusable strategy, and future runs can retrieve it by similarity.[1][2][3][5]

## 5. HTTP/WS endpoint wiring (so it’s user‑visible)

Once the engine parts are wired, make Strategy Memory visible to clients in two ways:[6][2][3][1][4]

- **lchat / OS chat:**  
  - In `api/server.py`, define a first‑class `POST /lchat` (or similar) that:
    - Wraps request → `AgentTask` / `TaskGraph` via `UnifiedController`.  
    - The controller’s plan‑build step now passes through Strategy Memory first (as in section 2), so chat and complex tasks automatically benefit from strategy reuse.[4]

- **Slack / WS flows:**  
  - In `slacktaskrouter.py` and `wstaskrouter.py`, do **not** add Strategy Memory logic there; instead:
    - They should continue to route to UnifiedController / PlanExecutor, which now has Strategy Memory integrated.[4]

This keeps front doors simple: they just hand tasks to the OS; the OS internally decides whether to reuse a strategy or plan from scratch.

***

Strategy Memory should live as a first‑class orchestration service under `orchestration/`, and it touches only two existing execution modules for now: `orchestration/planexecutor.py` and `core/agents/executor.py`.[1][2]

## Module placement under /l9/

- **Service implementation (new file):**  
  - `/l9/orchestration/strategymemory.py`  
    - Holds `StrategyMemoryService` and any Pydantic models or DTOs needed for retrieval and feedback.  
- **Engine integration points (existing files):**  
  - `/l9/orchestration/planexecutor.py` – call StrategyMemory before executing a plan and after completion for scoring.  
  - `/l9/core/agents/executor.py` – optionally surface per‑task feedback into Strategy Memory when an `AgentTask` completes (so single‑task runs can still produce strategy updates).[2][1]

## StrategyMemoryService core interface (strategymemory.py)

Grounded in your current style (`*Service` classes in orchestration and memory layers, using Pydantic models for payloads), the minimal production interface should look like this:[1]

```python
# /l9/orchestration/strategymemory.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from pydantic import BaseModel


class StrategyCandidate(BaseModel):
    strategy_id: str
    description: str
    confidence: float
    score: float
    plan_payload: dict  # serialized plan / ExecutionPlan / TaskGraph-like structure


class StrategyRetrievalRequest(BaseModel):
    task_id: str
    task_kind: str
    goal_description: str
    context_embedding: List[float]
    tags: List[str] = []


class StrategyFeedback(BaseModel):
    strategy_id: str
    task_id: str
    success: bool
    outcome_score: float
    execution_time_ms: int
    resource_cost: float
    metadata: dict = {}


class IStrategyMemoryService(ABC):
    @abstractmethod
    async def retrieve_strategies(
        self,
        request: StrategyRetrievalRequest,
        limit: int = 3,
    ) -> List[StrategyCandidate]:
        ...

    @abstractmethod
    async def record_new_strategy(
        self,
        task_id: str,
        description: str,
        plan_payload: dict,
        context_embedding: List[float],
        tags: Optional[List[str]] = None,
    ) -> str:
        ...

    @abstractmethod
    async def update_strategy_outcome(
        self,
        feedback: StrategyFeedback,
    ) -> None:
        ...


class StrategyMemoryService(IStrategyMemoryService):
    # concrete Neo4j-backed implementation; to be wired using your existing
    # memorygraphclient.Neo4jClient-style patterns
    ...
```

This matches the retrieval + auto‑score + prune loop described in the Strategy Memory docs, but in your repo’s service pattern.[3][4][5][6][7]

## New hooks in orchestration/planexecutor.py

`PlanExecutor` is already the dependency‑aware executor for `ExecutionPlan`. To integrate Strategy Memory deterministically:[1]

1. **Inject the service into PlanExecutor’s constructor:**

```python
# /l9/orchestration/planexecutor.py

from typing import Optional
from .strategymemory import IStrategyMemoryService, StrategyRetrievalRequest, StrategyFeedback  # new import

class PlanExecutor:
    def __init__(
        self,
        config: ExecutorConfig,
        substrate_service: MemorySubstrateService,
        # existing deps...
        strategy_memory: Optional[IStrategyMemoryService] = None,  # new param
    ) -> None:
        self._config = config
        self._substrate = substrate_service
        # existing assignments...
        self._strategy_memory = strategy_memory
```

2. **Helper to query Strategy Memory before executing a fresh plan:**

```python
    async def maybe_apply_strategy(
        self,
        request: StrategyRetrievalRequest,
    ) -> Optional[ExecutionPlan]:
        """
        Look up a reusable strategy; if a high-confidence candidate exists,
        adapt its stored plan_payload into an ExecutionPlan and return it.
        Otherwise return None to indicate 'plan from scratch'.
        """
        if self._strategy_memory is None:
            return None

        candidates = await self._strategy_memory.retrieve_strategies(request=request, limit=1)
        if not candidates:
            return None

        candidate = candidates[0]
        if candidate.confidence < self._config.strategy_min_confidence:
            return None

        # TODO: adapt candidate.plan_payload -> ExecutionPlan using your existing IRToPlanAdapter
        # This is a real adapter, not a stub, wired against irengine.irtoplanadapter.ExecutionPlan.
        return adapted_plan
```

3. **Feedback hook after plan completion:**

```python
    async def record_strategy_feedback(
        self,
        strategy_id: str,
        task_id: str,
        result: ExecutionResult,
    ) -> None:
        """
        Push execution outcome into Strategy Memory for scoring and pruning logic.
        """
        if self._strategy_memory is None:
            return

        feedback = StrategyFeedback(
            strategy_id=strategy_id,
            task_id=task_id,
            success=result.status is ExecutionStatus.SUCCEEDED,
            outcome_score=result.metrics.overall_score,
            execution_time_ms=result.metrics.total_duration_ms,
            resource_cost=result.metrics.estimated_cost,
            metadata={"step_metrics": result.step_results},
        )
        await self._strategy_memory.update_strategy_outcome(feedback)
```

4. **Optional creation of a new strategy after a successful de‑novo plan:**

```python
    async def maybe_record_new_strategy(
        self,
        task_id: str,
        description: str,
        plan: ExecutionPlan,
        context_embedding: list[float],
    ) -> Optional[str]:
        if self._strategy_memory is None:
            return None

        plan_payload = plan.to_dict()  # or your existing serialization
        return await self._strategy_memory.record_new_strategy(
            task_id=task_id,
            description=description,
            plan_payload=plan_payload,
            context_embedding=context_embedding,
        )
```

These signatures are additive and match how other orchestration services (e.g. World Model, Memory Orchestrator) are integrated.[1]

## Optional hook in core/agents/executor.py

`AgentExecutorService` currently runs `AgentTask` via `AIOSRuntime` and returns an `ExecutionResult`‑like object. To let single‑task runs participate in Strategy Memory:[2]

1. **Inject StrategyMemoryService:**

```python
# /l9/core/agents/executor.py

from typing import Optional
from orchestration.strategymemory import IStrategyMemoryService, StrategyFeedback  # new import

class AgentExecutorService:
    def __init__(
        self,
        runtime: AIOSRuntime,
        # existing deps...
        strategy_memory: Optional[IStrategyMemoryService] = None,
    ) -> None:
        self._runtime = runtime
        # existing assignments...
        self._strategy_memory = strategy_memory
```

2. **Feedback method after AgentTask completion:**

```python
    async def _record_task_strategy_feedback(
        self,
        strategy_id: str,
        task: AgentTask,
        result: ExecutionResult,
    ) -> None:
        if self._strategy_memory is None:
            return

        feedback = StrategyFeedback(
            strategy_id=strategy_id,
            task_id=str(task.id),
            success=result.success,
            outcome_score=result.metrics.overall_score,
            execution_time_ms=result.metrics.total_duration_ms,
            resource_cost=result.metrics.estimated_cost,
            metadata={"agent_id": task.agent_id, "kind": task.kind.value},
        )
        await self._strategy_memory.update_strategy_outcome(feedback)
```

You can call this from within `start_agent_task` only when the task was created from a retrieved strategy (e.g. `task.context.strategy_id` present), preserving current behaviour otherwise.[2]

***
