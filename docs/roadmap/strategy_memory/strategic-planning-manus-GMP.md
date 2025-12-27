

Phase 0 is only the TODO plan lock, so this answers with a deterministic change list and no code edits yet.[1][2]

## GMP Phase 0 – TODO plan lock

### 0.1 Target files (and status)

1. `/l9/orchestration/strategymemory.py`  
   - Action: **Insert** (new file).  
2. `/l9/orchestration/planexecutor.py`  
   - Action: **Wrap/Insert** (new imports, ctor arg, and helper methods; no behaviour changes outside defined regions).  
3. `/l9/core/agents/executor.py`  
   - Action: **Wrap/Insert** (new imports, ctor arg, and optional feedback helper; no behaviour changes outside defined regions).  

No other files will be touched under this TODO plan.

***

### 0.2 Concrete TODO items (per file, with actions)

#### File 1: `/l9/orchestration/strategymemory.py` (INSERT)

**Goal:** Introduce a production‑grade Strategy Memory abstraction matching existing orchestration patterns and ready to be backed by Neo4j (via `memorygraphclient.Neo4jClient` later).  

**Planned contents:**

1. **Imports section (INSERT):**
   - `from __future__ import annotations`
   - Standard typing: `from typing import Any, List, Optional`
   - Pydantic base: `from pydantic import BaseModel`
   - (No external side effects; no DB wiring yet.)

2. **Pydantic models (INSERT):**
   - `StrategyCandidate(BaseModel)` with fields:
     - `strategy_id: str`
     - `description: str`
     - `confidence: float`
     - `score: float`
     - `plan_payload: dict`
   - `StrategyRetrievalRequest(BaseModel)` with fields:
     - `task_id: str`
     - `task_kind: str`
     - `goal_description: str`
     - `context_embedding: List[float]`
     - `tags: List[str] = []`
   - `StrategyFeedback(BaseModel)` with fields:
     - `strategy_id: str`
     - `task_id: str`
     - `success: bool`
     - `outcome_score: float`
     - `execution_time_ms: int`
     - `resource_cost: float`
     - `metadata: dict = {}`

3. **Service interface (INSERT):**
   - `class IStrategyMemoryService(ABC)` with three abstract methods:
     - `async def retrieve_strategies(self, request: StrategyRetrievalRequest, limit: int = 3) -> List[StrategyCandidate]: ...`
     - `async def record_new_strategy(self, task_id: str, description: str, plan_payload: dict, context_embedding: List[float], tags: Optional[List[str]] = None) -> str: ...`
     - `async def update_strategy_outcome(self, feedback: StrategyFeedback) -> None: ...`

4. **Concrete service shell (INSERT):**
   - `class StrategyMemoryService(IStrategyMemoryService):`
     - `__init__(...)` taking generic dependencies (e.g. `neo4j_client: Neo4jClient | Any`) but implemented using actual imports if they already exist; otherwise, keep it dependency‑injected only, no stubs.
     - Methods implementing the three interface methods with **real return types and raising `NotImplementedError` only where a later GMP will fill in Neo4j queries**.
   - This is allowed because behaviour is explicit and fails loud; there are no “TODO” comments or silent stubs.

***

#### File 2: `/l9/orchestration/planexecutor.py` (INSERT/WRAP)

**Goal:** Allow `PlanExecutor` to optionally use `StrategyMemoryService` for retrieval and feedback, without changing default behaviour when no instance is passed.  

**Planned modifications:**

1. **Imports block (INSERT):**
   - Add imports near existing orchestration imports:
     - `from typing import Optional`
     - `from .strategymemory import IStrategyMemoryService, StrategyRetrievalRequest, StrategyFeedback, StrategyCandidate`
   - Ensure no circular imports by keeping this purely in `orchestration` layer.

2. **PlanExecutor.__init__ signature (WRAP):**
   - Locate `class PlanExecutor:` and its `__init__` definition (confirmed in `class_definitions.txt`).[1]
   - Add a new optional parameter at the end:
     - `strategy_memory: Optional[IStrategyMemoryService] = None`
   - Inside `__init__`, assign:
     - `self._strategy_memory = strategy_memory`

3. **Configuration check (INSERT, small):**
   - If `ExecutorConfig` already exists (it does), extend it minimally to support an optional confidence threshold:
     - Add field: `strategy_min_confidence: float = 0.7`
   - This is a safe default and does not affect existing callers.

4. **Strategy retrieval helper (INSERT, new method):**
   - Add an async method on `PlanExecutor`:

     ```python
     async def maybe_apply_strategy(
         self,
         request: StrategyRetrievalRequest,
     ) -> Optional[ExecutionPlan]:
         """
         If Strategy Memory is configured, attempt to retrieve a reusable plan.
         Returns an ExecutionPlan when a high-confidence strategy is found,
         otherwise returns None to signal 'plan from scratch'.
         """
         if self._strategy_memory is None:
             return None

         candidates = await self._strategy_memory.retrieve_strategies(request=request, limit=1)
         if not candidates:
             return None

         candidate = candidates[0]
         if candidate.confidence < self._config.strategy_min_confidence:
             return None

         # Adapt candidate.plan_payload -> ExecutionPlan using existing IR adapters.
         return self._adapt_strategy_plan(candidate)
     ```

5. **Adapter helper (INSERT, new private method):**
   - Add:

     ```python
     def _adapt_strategy_plan(
         self,
         candidate: StrategyCandidate,
     ) -> ExecutionPlan:
         """
         Deterministically adapt a stored plan_payload into an ExecutionPlan.
         Uses existing IRToPlanAdapter or equivalent; no new abstractions.
         """
         # Implementation will call existing IR-to-plan utilities;
         # exact calls will be wired in Phase 2 using real functions.
     ```

   - Phase 1 will confirm the exact adapter symbol (`IRToPlanAdapter`) from `irengine.irtoplanadapter`. This plan only locks the existence of the wrapper method.

6. **Feedback hook (INSERT, new method):**
   - Add:

     ```python
     async def record_strategy_feedback(
         self,
         strategy_id: str,
         task_id: str,
         result: ExecutionResult,
     ) -> None:
         if self._strategy_memory is None:
             return

         feedback = StrategyFeedback(
             strategy_id=strategy_id,
             task_id=task_id,
             success=result.status is ExecutionStatus.SUCCEEDED,
             outcome_score=result.metrics.overall_score,
             execution_time_ms=result.metrics.total_duration_ms,
             resource_cost=result.metrics.estimated_cost,
             metadata={"step_results": [sr.dict() for sr in result.step_results]},
         )
         await self._strategy_memory.update_strategy_outcome(feedback)
     ```

7. **New strategy creation helper (INSERT, new method):**
   - Add:

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

         plan_payload = plan.to_dict()  # existing method from ExecutionPlan
         return await self._strategy_memory.record_new_strategy(
             task_id=task_id,
             description=description,
             plan_payload=plan_payload,
             context_embedding=context_embedding,
         )
     ```

8. **No change yet to the main execute() flow:**
   - Phase 0 explicitly **does not** rewire the core execution loop; it only adds optional helpers and wiring.  
   - Actual call sites (where `maybe_apply_strategy` and `record_strategy_feedback` are invoked) will be defined in a later GMP once the Strategy Memory backend is implemented.

***

#### File 3: `/l9/core/agents/executor.py` (INSERT/WRAP)

**Goal:** Allow `AgentExecutorService` (or equivalent class in this module) to push per‑task outcomes into Strategy Memory when a task is associated with a stored strategy, without affecting default behaviour.  

**Planned modifications:**

1. **Imports block (INSERT):**
   - Add near existing orchestration imports:
     - `from typing import Optional`
     - `from orchestration.strategymemory import IStrategyMemoryService, StrategyFeedback`

2. **AgentExecutorService.__init__ signature (WRAP):**
   - Locate `class AgentExecutorService` and its `__init__` function in `core/agents/executor.py`.[1]
   - Add optional parameter at the end:
     - `strategy_memory: Optional[IStrategyMemoryService] = None`
   - Assign inside `__init__`:
     - `self._strategy_memory = strategy_memory`

3. **Feedback helper (INSERT, new private method):**

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
           metadata={
               "agent_id": task.agent_id,
               "kind": task.kind.value,
           },
       )
       await self._strategy_memory.update_strategy_outcome(feedback)
   ```

4. **No behavioural change in public methods yet:**
   - Existing methods such as `start_agent_task` or equivalent will not be modified in Phase 0; they will only be updated in a later phase to call `_record_task_strategy_feedback` when `task.context` (or similar) carries a `strategy_id`.  
   - This ensures zero drift and keeps current behaviour intact.

***

### 0.3 Expected behaviour after full GMP execution (for this TODO set)

- System can be constructed with an optional `StrategyMemoryService` instance wired into both `PlanExecutor` and `AgentExecutorService`.  
- New helper methods exist to:
  - Ask Strategy Memory for a candidate plan (`maybe_apply_strategy`).
  - Record execution feedback (`record_strategy_feedback`, `_record_task_strategy_feedback`).
  - Optionally persist successful plans as reusable strategies (`maybe_record_new_strategy`).  
- When `strategy_memory` is `None`, all new paths are no‑ops; the OS behaves exactly as today.  

***

PHASE 1 – BASELINE CONFIRMATION
[ ] 1.1 Verify file existence and locations
    - Confirm /l9/orchestration/planexecutor.py exists and contains:
      - class PlanExecutor
      - ExecutorConfig
      - ExecutionResult, ExecutionStatus, ExecutionPlan (or equivalent) definitions or imports.
    - Confirm /l9/core/agents/executor.py exists and contains:
      - class AgentExecutorService (or equivalent primary executor class).
      - AgentTask model import.
    - Confirm no existing /l9/orchestration/strategymemory.py file to avoid conflicts.

[ ] 1.2 Confirm constructor signatures and patterns
    - In PlanExecutor.__init__, enumerate current parameters and ensure adding
      strategy_memory: Optional[IStrategyMemoryService] = None
      does not break call sites (grep for “PlanExecutor(” across the repo).
    - In AgentExecutorService.__init__, enumerate current parameters and ensure adding
      strategy_memory: Optional[IStrategyMemoryService] = None
      is compatible with all instantiations (grep for “AgentExecutorService(”).
    - Verify ExecutorConfig already exists and can safely accept a new
      strategy_min_confidence: float = 0.7 field without failing config parsing.

[ ] 1.3 Confirm supporting types
    - Verify there is an ExecutionPlan type used by PlanExecutor (directly or via irengine.irtoplanadapter).
    - Verify ExecutionResult has:
      - status field comparable to ExecutionStatus.SUCCEEDED
      - metrics with overall_score, total_duration_ms, estimated_cost (or equivalent names; note exact names).
      - step_results iterable of step result objects with dict() or similar for serialization.
    - Verify AgentTask model has:
      - id
      - agent_id
      - kind (enum, probably TaskKind or similar with .value attribute).

[ ] 1.4 Check import graph and circularity risk
    - Confirm orchestration.planexecutor does not import core.agents.executor (to keep one-way dependency).
    - Confirm core.agents.executor can import orchestration.strategymemory without introducing cycles
      (no reverse import from strategymemory back into core.agents.executor).

[ ] 1.5 Confirm tests and config files references
    - Search tests for PlanExecutor and AgentExecutorService usage to ensure additional constructor
      parameter will not break fixtures or integration tests.
    - Confirm no hard-coded argument lists in factories or bootstrap code that would fail on signature change.

----------------------------------------------------------------
PHASE 2 – IMPLEMENTATION (CODE CHANGES)
[ ] 2.1 Create /l9/orchestration/strategymemory.py
    - Add imports:
      - from __future__ import annotations
      - from abc import ABC, abstractmethod
      - from typing import Any, List, Optional
      - from pydantic import BaseModel
    - Define Pydantic models:
      - StrategyCandidate(BaseModel):
          strategy_id: str
          description: str
          confidence: float
          score: float
          plan_payload: dict
      - StrategyRetrievalRequest(BaseModel):
          task_id: str
          task_kind: str
          goal_description: str
          context_embedding: List[float]
          tags: List[str] = []
      - StrategyFeedback(BaseModel):
          strategy_id: str
          task_id: str
          success: bool
          outcome_score: float
          execution_time_ms: int
          resource_cost: float
          metadata: dict = {}
    - Define IStrategyMemoryService(ABC) with abstract async methods:
      - retrieve_strategies(self, request: StrategyRetrievalRequest, limit: int = 3) -> List[StrategyCandidate]
      - record_new_strategy(self, task_id: str, description: str, plan_payload: dict,
                            context_embedding: List[float], tags: Optional[List[str]] = None) -> str
      - update_strategy_outcome(self, feedback: StrategyFeedback) -> None
    - Define StrategyMemoryService(IStrategyMemoryService):
      - __init__(self, backend: Any) -> None: store backend reference only.
      - Implement methods by delegating to backend or raising explicit NotImplementedError
        with clear message if backend is None (fail loud, no silent stubs).

[ ] 2.2 Modify /l9/orchestration/planexecutor.py – imports and config
    - Add imports:
      - from typing import Optional
      - from .strategymemory import (
            IStrategyMemoryService,
            StrategyRetrievalRequest,
            StrategyFeedback,
            StrategyCandidate,
        )
    - Extend ExecutorConfig (if present) with:
      - strategy_min_confidence: float = 0.7
      ensuring this field has a default and is fully backwards compatible.

[ ] 2.3 Modify PlanExecutor.__init__
    - Update signature:
      def __init__(..., strategy_memory: Optional[IStrategyMemoryService] = None) -> None:
    - Assign:
      self._strategy_memory = strategy_memory
    - Ensure all existing arguments preserve order and defaults; only append the new parameter.

[ ] 2.4 Add PlanExecutor.maybe_apply_strategy
    - Implement async def maybe_apply_strategy(self, request: StrategyRetrievalRequest) -> Optional[ExecutionPlan]:
      - If self._strategy_memory is None: return None.
      - candidates = await self._strategy_memory.retrieve_strategies(request=request, limit=1)
      - If not candidates: return None.
      - candidate = candidates[0]
      - If candidate.confidence < self._config.strategy_min_confidence: return None.
      - Return self._adapt_strategy_plan(candidate).

[ ] 2.5 Add PlanExecutor._adapt_strategy_plan
    - Implement:
      def _adapt_strategy_plan(self, candidate: StrategyCandidate) -> ExecutionPlan:
          """
          Adapt candidate.plan_payload into an ExecutionPlan using existing IR/plan adapters.
          """
          # Use existing adapter, e.g. IRToPlanAdapter.from_dict or similar,
          # matching the real function names from irengine.irtoplanadapter.
    - Wire this to actual adapter methods discovered in Phase 1 (no pseudo-calls).

[ ] 2.6 Add PlanExecutor.record_strategy_feedback
    - Implement async def record_strategy_feedback(self, strategy_id: str, task_id: str,
                                                   result: ExecutionResult) -> None:
      - If self._strategy_memory is None: return.
      - Build StrategyFeedback with:
          strategy_id=strategy_id
          task_id=task_id
          success=(result.status is ExecutionStatus.SUCCEEDED)
          outcome_score=result.metrics.overall_score
          execution_time_ms=result.metrics.total_duration_ms
          resource_cost=result.metrics.estimated_cost
          metadata={"step_results": [sr.dict() for sr in result.step_results]}
      - await self._strategy_memory.update_strategy_outcome(feedback)

[ ] 2.7 Add PlanExecutor.maybe_record_new_strategy
    - Implement async def maybe_record_new_strategy(self, task_id: str, description: str,
                                                    plan: ExecutionPlan,
                                                    context_embedding: list[float]) -> Optional[str]:
      - If self._strategy_memory is None: return None.
      - plan_payload = plan.to_dict() (or equivalent serializer confirmed in Phase 1).
      - return await self._strategy_memory.record_new_strategy(
            task_id=task_id,
            description=description,
            plan_payload=plan_payload,
            context_embedding=context_embedding,
        )

[ ] 2.8 Modify /l9/core/agents/executor.py – imports and wiring
    - Add imports:
      - from typing import Optional
      - from orchestration.strategymemory import IStrategyMemoryService, StrategyFeedback
    - Update AgentExecutorService.__init__ signature:
      def __init__(..., strategy_memory: Optional[IStrategyMemoryService] = None) -> None:
    - Assign:
      self._strategy_memory = strategy_memory

[ ] 2.9 Add AgentExecutorService._record_task_strategy_feedback
    - Implement async def _record_task_strategy_feedback(
            self,
            strategy_id: str,
            task: AgentTask,
            result: ExecutionResult,
        ) -> None:
      - If self._strategy_memory is None: return.
      - Build StrategyFeedback:
          strategy_id=strategy_id
          task_id=str(task.id)
          success=result.success
          outcome_score=result.metrics.overall_score
          execution_time_ms=result.metrics.total_duration_ms
          resource_cost=result.metrics.estimated_cost
          metadata={"agent_id": task.agent_id, "kind": task.kind.value}
      - await self._strategy_memory.update_strategy_outcome(feedback)
    - Do not yet change public methods to call this; that will be a later explicit GMP.

----------------------------------------------------------------
PHASE 3 – ENFORCEMENT (GUARDS & FEATURE FLAGS)
[ ] 3.1 Feature flag / config safeguard
    - Ensure Strategy Memory integration is fully optional:
      - If no IStrategyMemoryService instance is passed to PlanExecutor or AgentExecutorService,
        all new methods become no-ops and are never auto-invoked.
    - Optionally add an OS-level config field or env-sourced flag (e.g. L9_ENABLE_STRATEGY_MEMORY)
      only if there is an existing pattern for such flags; otherwise rely solely on “service is None”.

[ ] 3.2 Type and contract enforcement
    - Add docstrings to StrategyMemoryService and IStrategyMemoryService describing:
      - Expected backend behaviour (e.g. Neo4j client or compatible interface).
      - That methods must be async and must not raise on “no results” for retrieve_strategies.
    - Validate that StrategyRetrievalRequest and StrategyFeedback fields align with the
      Strategy Memory specification (embedding as List[float], scores as float, etc.).

[ ] 3.3 Error handling discipline
    - In PlanExecutor helpers, catch and log Strategy Memory errors (if there is an existing
      logger pattern in planexecutor) and degrade gracefully to “no strategy” rather than
      failing the whole plan.
    - In AgentExecutorService helper, treat Strategy Memory errors as non-fatal: log and continue.

----------------------------------------------------------------
PHASE 4 – VALIDATION (TESTING)
[ ] 4.1 Unit tests for strategymemory.py
    - Add tests (or extend existing ones) to validate:
      - StrategyCandidate / StrategyRetrievalRequest / StrategyFeedback Pydantic models instantiate correctly.
      - IStrategyMemoryService cannot be instantiated directly.
      - StrategyMemoryService passes through calls to a fake backend and raises clear errors if backend is None.

[ ] 4.2 Unit tests for PlanExecutor wiring
    - Add tests to existing PlanExecutor test module:
      - Construct PlanExecutor with strategy_memory=None:
          - maybe_apply_strategy returns None without calling service.
          - record_strategy_feedback and maybe_record_new_strategy return quickly, no errors.
      - Construct PlanExecutor with a FakeStrategyMemoryService:
          - maybe_apply_strategy calls retrieve_strategies with correct request, limit=1.
          - record_strategy_feedback passes expected StrategyFeedback (verify fields).
          - maybe_record_new_strategy passes serialized plan_payload correctly.

[ ] 4.3 Unit tests for AgentExecutorService wiring
    - Extend core/agents executor tests:
      - When strategy_memory=None, _record_task_strategy_feedback is a no-op.
      - When strategy_memory is a fake service, verify update_strategy_outcome is called
        with expected StrategyFeedback contents.

[ ] 4.4 Regression tests / existing suite
    - Run full test suite:
      - tests/test_imports.py to confirm new module strategymemory imports cleanly.
      - All orchestration and runtime tests to ensure constructor changes do not break wiring.
    - Confirm no new failing tests introduced by this change set.

----------------------------------------------------------------
PHASE 5 – RECURSIVE VERIFICATION
[ ] 5.1 Cross-check against TODO plan
    - Verify only the three files in the locked TODO plan were modified:
      - /l9/orchestration/strategymemory.py (new).
      - /l9/orchestration/planexecutor.py (diff inspected).
      - /l9/core/agents/executor.py (diff inspected).
    - Confirm that all planned methods and parameters are present with the exact names
      and signatures described in Phase 2.

[ ] 5.2 L9 invariants and patterns
    - Confirm new service follows L9 style:
      - Pydantic models for structured payloads.
      - Service interface + implementation pairing (IStrategyMemoryService + StrategyMemoryService).
      - Optional wiring via dependency injection, no global singletons.
    - Confirm there are no new circular imports in orchestration or core agents.

[ ] 5.3 Behavioural invariants
    - Confirm that when Strategy Memory is not configured:
      - All existing PlanExecutor and AgentExecutorService behaviours are identical to pre-change state.
    - Confirm that enabling Strategy Memory only introduces additional optional calls,
      without changing plan construction logic yet (no call sites added implicitly).

----------------------------------------------------------------
PHASE 6 – FINALIZATION
[ ] 6.1 Definition of Done (for this GMP slice)
    - Strategy Memory core interfaces and models exist in /l9/orchestration/strategymemory.py.
    - PlanExecutor and AgentExecutorService accept an optional IStrategyMemoryService dependency.
    - Helper methods for strategy retrieval, recording feedback, and registering new strategies
      are implemented and tested.
    - No existing code paths are altered to rely on Strategy Memory yet; behaviour is opt-in.

[ ] 6.2 Evidence summary
    - Record:
      - File diffs for the three touched modules.
      - Test suite results (with relevant test names) confirming green state.
      - Import graph checks showing no new cycles.

[ ] 6.3 FINAL DECLARATION
    - After all checkboxes above are verifiably [x]:
      - Declare verbatim: “All phases (0–6) complete. No assumptions. No drift.”
```
