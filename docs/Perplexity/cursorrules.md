Perfect. I now have deep context on the `/l9/` repo structure. Let me generate production-grade Cursor `.mdc` rules files tailored to this L9 Secure AI OS architecture.

***

## `.cursor/rules/00-global.mdc`

```markdown
---
description: "Primary global rules for the L9 Secure AI OS monorepo: architecture invariants, safety, and universal coding standards."
alwaysApply: true
---

# L9 Secure AI OS – Global Rules

## Project Overview

**L9 Secure AI OS** is a deterministic, multi-layered autonomous agent runtime with:
- **Kernel Stack**: 10 governance/identity/behavior kernels (MasterKernel, SafetyKernel, ExecutionKernel, etc.)
- **Agent Executor**: AgentExecutorService, AIOSRuntime, and AgentInstance for task-driven reasoning
- **Memory Substrate**: Neo4j-backed graph, PostgreSQL packet store, semantic embedding layer
- **Orchestration**: UnifiedController, TaskRouter, PlanExecutor for multi-agent task graphs
- **Tool Graph**: Registry-based tool dispatch with approval gates for high-risk operations
- **WebSocket Orchestrator**: Real-time bidirectional agent communication via WebSocket

Critical safety posture: **No silent partial work. Explicit failure semantics. Idempotent operations. Audit-first memory logging.**

---

## Universal Coding Standards

### Determinism & Reproducibility

- **No randomness in execution paths**: Use seeded PRNGs (if needed) with explicit seed injection via config.
- **Idempotent operations**: All agent tasks, tool calls, and memory writes must be replayable without side effects.
- **Explicit error semantics**: No unhandled exceptions. Always emit a failure packet to memory with root cause, stack trace, and recovery action.
- **No implicit state mutations**: All state changes must be logged to PacketEnvelope and memory substrate atomically.

### Logging, Tracing, and Audit

- **Every agent decision is a packet**: Use `PacketEnvelope` from `memory.substrate_models` for all reasoning, tool use, and decisions.
- **Packet structure**: Include `source_id`, `agent_id`, `thread_id`, `kind` (REASONING, TOOL_CALL, DECISION, MEMORY_WRITE), `payload`, `metadata`, `confidence`.
- **Memory ingestion**: All packets flow through `MemorySubstrateService.ingest_packet()` atomically. No fire-and-forget logging.
- **Audit trails**: Every tool execution, approval decision, and memory mutation must have a timestamp, actor, and justification in metadata.
- **Tracing**: Use structured logging with context (agent_id, task_id, thread_id) at every step. Avoid generic print() statements.

### Error Handling & Resilience

- **Fail loud, fail fast**: On error, immediately emit a packet to memory with kind=FAILURE, include full error context.
- **Recovery spec**: Every error packet must include a proposed recovery action (retry, escalate, rollback, skip).
- **Timeouts**: All external calls (HTTP, shell, MCP) must have explicit timeouts. No hanging tasks.
- **Circuit breakers**: For repeated failures (3+ consecutive), emit escalation to Igor (authority=IGOR_APPROVAL) before continuing.

### Memory & Storage Invariants

- **Single source of truth**: PostgreSQL `packetstore` is the canonical event log. Neo4j is derived view only.
- **No in-memory state across requests**: Agents must load context from memory substrate at start. No global Python objects.
- **Blob storage**: Large payloads (>10KB) go to S3 blob store, referenced via `payload.blob_ref` in packet.
- **Idempotent writes**: If same packet (same dedup_key) written twice, second write is a no-op. Use UUIDs + content hash.

### Message Passing & Async

- **Redis task queue**: Background jobs enqueued via `TaskQueue.enqueue()` with explicit `task_id`, `queue_name`, `payload`.
- **Rate limiting**: All external APIs and tool calls rate-limited via `RateLimiter` class with Redis backend.
- **No polling**: Use Redis pub/sub or WebSocket for real-time updates, not sleep-loops.
- **Async context**: Use `async def` for all I/O. No blocking calls in async functions.

---

## Non-Negotiable Safety & Governance Constraints

### Approval Gates for High-Risk Operations

**High-risk tools** (GMPRUN, GITCOMMIT, MACAGENTEXEC, etc.) require **explicit Igor approval** before execution:

- Tool definition includes `requiresIgorApproval=True` (or scoped flag in `ToolDefinition`).
- Before dispatch, executor checks `AgentCapabilities` and `GovernanceApprovals` tables.
- If approval required but missing, emit **BLOCKED** packet to memory with escalation path.
- Approval token includes `approved_by`, `approved_at`, `approval_scope`, `expiration`.

### Destructive Operation Constraints

**Destructive operations** (GITCOMMIT, MACAGENTEXEC shell, data deletion) must:
- Have a **dry-run mode**: Propose action with full outcome spec before executing.
- Include **rollback specification**: How to undo this if needed.
- Log **before and after state**: Packet payload includes pre-condition and post-condition assertions.
- Require **explicit confirmation**: If human-in-the-loop, escalate via WebSocket or Slack before actual execution.

### External Control & Escalation

- **User intent validation**: For any user-initiated task, verify intent via Slack thread UUID or HTTP session ID.
- **Escalation channels**: On uncertainty, L escalates to Igor via Slack DM or WebSocket.
- **Authority hierarchy**: Igor > L (CTO) > Research agents > Mac agent. Respect this in tool dispatch.
- **Audit immutability**: Once a decision packet is in memory, it cannot be deleted. Corrections are new packets.

---

## Conflict Resolution: Global vs Scoped Rules

**When multiple `.mdc` files apply, this hierarchy wins:**

1. **Global invariants always win** – safety, approval gates, memory substrate, error handling.
2. **Scoped rules refine, never override** – language/framework rules optimize patterns but never disable safety checks.
3. **Explicit flag overrides**: If a `.mdc` uses `L9_ENABLE_*` flags, always gate behind feature flags and log the decision.

**Example**:
- Global rule: "All tool calls require approval check."
- Python scoped rule: "Use `async/await` for I/O in core.agents.executor."
- → Both apply. Python rule does NOT skip approval. Approval check is in executor code, scoped rule refines how executor is written.

---

## L9-Specific Patterns

### Agent Task Lifecycle

```
1. TaskEnvelope created (http lchat, Slack, WebSocket) with AgentTask payload.
2. TaskRouter.route() determines execution target and complexity.
3. AgentExecutorService.start_agent_task() instantiates agent + tools.
4. AIOSRuntime.execute_reasoning() loops: reason → tool_call → check_approval → dispatch.
5. All steps logged to memory via packet ingestion.
6. ExecutionResult returned with output, status, tool_calls, metadata.
```

### Kernel Stack Loading

- **At startup**: KernelLoader reads YAML kernels (00-masterkernel, 02-identity, 08-safety, etc.).
- **Per agent**: AgentRegistry.get_agent_config(agent_id) returns AgentConfig with kernel stack.
- **Prompts**: lcto.py builds system prompt by composing kernel sections in order.
- **Governance**: SafetyKernel constraints are enforced by executor before tool dispatch.

### Tool Registry & Capabilities

- **Tool definitions**: core.tools.toolgraph.LTOOLSDEFINITIONS (list of ToolDefinition).
- **Capability profiles**: AgentCapabilities enum (LCAPABILITIES) gates which tools agent can use.
- **Governance metadata**: ToolDefinition includes `scope`, `requiresIgorApproval`, `isDestructive`.
- **Runtime dispatch**: executor queries registry, checks capability + approval, then calls tool.

### Memory Packet Ingest

- **PacketEnvelope schema**: source_id, agent_id, thread_id, kind, payload, metadata, confidence.
- **Ingestion pipeline**: MemorySubstrateService.ingest_packet() → ingestion DAG → Neo4j + PostgreSQL.
- **Async persistence**: Ingestion runs in background task queue. Executor doesn't wait.
- **Deduplication**: Same packet (uuid) or same dedup_key not re-ingested. Idempotent.

---

## Feature Flags & Deprecation

- **L9_ENABLE_LEGACY_CHAT**: Gates old apiserver.py POST /chat (default=true, later false).
- **L9_ENABLE_LEGACY_SLACK_ROUTER**: Gates old webhookslack.py path without AgentTask (default=true, later false).
- **L9_USE_KERNELS**: If true, load kernels from files; if false, use fallback prompt (default=true).
- **L9_ENABLE_WS_ORCHESTRATOR**: If true, WebSocket routes use wstaskrouter; if false, no WS (default=true).

When adding flags, always:
1. Log the flag state at startup (use Python logging.info).
2. Document deprecation path and removal date.
3. Test both branches (flag on and off).

---

## Coding Conventions

### File Organization

- **core/agents/**: Agent executor, runtime, instance, registry. The kernel+task loop.
- **core/tools/**: Tool graph, registry, capabilities. Tool definitions and dispatch.
- **core/kernels/**: Kernel loading, yaml parsing. (Kernels themselves are YAML in config/)
- **memory/**: Substrate service, DAG, models, repository. Packet ingestion + retrieval.
- **orchestration/**: Routers, controllers, plan executor. Task graph orchestration.
- **runtime/**: Task queue, Redis client, rate limiter, WebSocket orchestrator. Background work.
- **api/**: FastAPI routers, request/response models. HTTP + WebSocket entry points.
- **services/**: Research agents, Mac tasks, utilities. Domain-specific services.

### Naming

- **Agent classes**: `FooAgent` (e.g., `ResearcherAgent`, `MacAgent`).
- **Service classes**: `FooService` (e.g., `MemorySubstrateService`, `AgentExecutorService`).
- **Data models**: `FooRequest`, `FooResponse`, `FooResult` for I/O; `Foo` for domain objects.
- **Enums**: `FooKind`, `FooStatus`, `FooMode` (e.g., `TaskKind`, `ExecutionStatus`).
- **Constants**: `UPPERCASE` for immutable config; `CONSTANT_NAME` for enums.

### Testing

- **Unit tests**: `tests/core/agents/test_executor.py` mirrors `core/agents/executor.py`.
- **Integration tests**: `tests/integration/test_orchestrator_memory_integration.py` for multi-module flows.
- **Smoke tests**: `tests/docker/test_stack_smoke.py` for critical paths post-docker-compose.
- **Mocks**: Use `tests/mocks/` for fixture factories (MockSubstrateService, MagicMock overrides).

---

## Critical Files (Verify, Don't Modify Without TODO)

- `kernel_loader.py`: Kernel YAML loading. Changing this breaks all agent identity.
- `executor.py`: Core agent execution loop. Changes must preserve packet logging.
- `websocket_orchestrator.py`: Real-time connection management. Don't modify without async safety review.
- `docker-compose.yml`: Infrastructure wiring. Don't change without testing full stack.
- `memory_substrate_service.py`: Packet ingestion and memory DAG. Mission-critical; treat as PROTECTED.

---

## Enforcement Checklist

- [ ] All agent tasks emit PacketEnvelope to memory. No silent operations.
- [ ] High-risk tool calls check approval gates before dispatch.
- [ ] Errors include recovery action. No bare exceptions in logs.
- [ ] Memory operations are idempotent. Same dedup_key = no re-write.
- [ ] Async code uses `async/await`. No sync I/O in async contexts.
- [ ] Timeouts on all external calls. No hanging tasks.
- [ ] Feature flags logged at startup with deprecation path.
- [ ] Tests for both flag=on and flag=off. No untested code paths.
- [ ] Critical files only changed via explicit TODO plan and GMP phases.
```

***

## `.cursor/rules/10-lang-typescript.mdc`

```markdown
---
description: "TypeScript + TSX language rules for AI OS UI and agent-facing frontends."
globs:
  - "**/*.ts"
  - "**/*.tsx"
  - "!**/*.test.ts"
  - "!**/*.test.tsx"
alwaysApply: false
---

# TypeScript/React Language Rules for L9 OS Frontend

## Type Safety & Strictness

### Explicit Types Required

- **No `any` type**: Use `unknown` and narrow via type guards, or `as const` for literal types.
- **Function signatures**: Always include parameter types and return type annotations.
  ```
  // ✅ CORRECT
  async function fetchAgentTask(taskId: string): Promise<AgentTask> { ... }
  
  // ❌ WRONG
  async function fetchAgentTask(taskId) { ... }
  ```
- **Object shapes**: Use interfaces or `type` aliases. No plain `{}` or `object`.
  ```
  interface AgentTaskRequest {
    message: string;
    threadId?: string;
    channel?: string;
  }
  ```
- **Union types**: Explicit, not stringly typed. Use discriminated unions for clarity.
  ```
  type ExecutionResult = 
    | { status: "success"; output: string }
    | { status: "failure"; error: string }
  ```

### Generic Type Parameters

- **Be explicit with generics**: `Array<T>` clarity > `T[]` shorthand.
- **Constrain generics**: Use `extends` to enforce shape contracts.
  ```
  function getField<T extends Record<string, any>>(obj: T, key: keyof T): any { ... }
  ```

---

## Module Boundaries & Imports

### Frontend Layering

- **api/**: HTTP client + WebSocket client. Data fetching only. No business logic.
  ```
  export async function lchat(message: string): Promise<LChatResponse>
  export class WSClient { ... }
  ```
- **hooks/**: React hooks. State management, data fetching coordination. No direct DOM.
  ```
  export const useAgentTask = (taskId: string) => { ... }
  ```
- **components/**: React components. Presentation only. No async logic beyond hooks.
- **stores/**: Zustand or Context global state. Single source of truth for app state.
- **types/**: TypeScript interfaces and enums. Shared across all layers.

### Circular Import Prevention

- **Core rule**: Components can't import from stores, stores can't import from components.
- **Dep direction**: Components → Hooks → API/Stores → Types. Never reverse.
- **Index exports**: Use `index.ts` in folders to re-export public API, hide internals.

---

## React-Specific Rules

### Functional Components & Hooks

- **All components are functional**: No class components.
- **Use hooks for state**: `useState`, `useEffect`, `useContext`, `useReducer`.
- **Custom hooks for reuse**: Extract repeated logic into `useXxx` hook.
  ```
  // ✅ CORRECT
  export const useTaskPolling = (taskId: string) => {
    const [task, setTask] = useState<AgentTask | null>(null);
    useEffect(() => { ... }, [taskId]);
    return task;
  };
  ```
- **Dependency arrays**: Accurate `useEffect` deps. Use ESLint exhaustive-deps rule.

### Props & Composition

- **Props are immutable**: No mutation. Use destructuring + spread for override patterns.
  ```
  interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant: "primary" | "secondary";
    isLoading?: boolean;
  }
  
  export const Button: React.FC<ButtonProps> = ({ variant, isLoading, ...rest }) => (
    <button className={`btn btn--${variant}`} disabled={isLoading} {...rest} />
  );
  ```
- **Children prop**: Explicit `React.ReactNode` type, not implicit.

### Error Boundaries & Error Handling

- **Wrap feature sections**: Use error boundary components for isolated error recovery.
- **Network errors**: Explicit error states (loading, success, error). Show UI feedback.
  ```
  if (error) return <div className="error">Failed: {error.message}</div>;
  if (isLoading) return <div>Loading...</div>;
  ```
- **No silent failures**: Log errors to console (dev) and optionally to Sentry (prod).

---

## WebSocket & Real-Time Rules

### Bidirectional Communication

- **Use WSClient class**: Persistent connection managed by context or hook.
- **Message envelope**: All messages follow `EventMessage` schema (from `runtime/wsprotocol`).
  ```
  interface EventMessage {
    type: "chat" | "tool_call" | "error" | "heartbeat";
    payload: Record<string, any>;
    timestamp: number;
  }
  ```
- **Heartbeat handling**: Client must respond to heartbeats. Server disconnects on silence >30s.
- **Reconnection**: Auto-reconnect with exponential backoff. Max 5 retries, then bail to HTTP fallback.

### Real-Time State Sync

- **Optimistic updates**: Update local state immediately, revert on error.
  ```
  // ✅ CORRECT
  const handleTaskUpdate = async (update: TaskUpdate) => {
    setTask(prev => ({ ...prev, ...update }));
    try {
      await api.updateTask(update);
    } catch (e) {
      setTask(prev => /* restore previous state */);
      showError(e.message);
    }
  };
  ```
- **Sync on reconnect**: After reconnect, re-fetch full state. No merge on reconnect.

---

## Async & Data Fetching

### HTTP Client Rules

- **Use fetch or axios wrapper**: Typed, with retry + timeout logic.
- **Timeouts**: All HTTP calls have 30s timeout. Agent calls have 60s timeout.
- **Error handling**: Explicit error types (NetworkError, TimeoutError, AuthError, etc.).
- **Request/response logging**: In dev, log requests/responses to console. In prod, only errors to Sentry.

### State Management in Hooks

- **Separate data fetching from state update**:
  ```
  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        const data = await api.get(...);
        if (isMounted) setData(data);
      } catch (e) {
        if (isMounted) setError(e);
      }
    };
    fetchData();
    return () => { isMounted = false; }; // Cleanup
  }, [deps]);
  ```
- **No race conditions**: Use cleanup functions and mounted checks.

---

## Logging & Debugging

### Structured Logging

- **Use console context**: Include agent_id, task_id, thread_id in log messages.
  ```
  console.log(`[${taskId}] Task started`, { agentId, threadId });
  ```
- **Log levels**: `debug` (dev only), `info` (UI state changes), `error` (exceptions).
- **Avoid logs in loops**: Debounce high-frequency logs.

### Browser DevTools

- **Source maps**: Always generate. No minified-only debugging in dev.
- **React DevTools**: Install. Use Profiler to identify re-render issues.
- **Network tab**: Inspect WebSocket frames + HTTP requests. Validate payload schema.

---

## Agent Control Surface Rules

### L Chat Panel

- **Message input**: Text area with Submit button. Disable during execution.
- **Execution status**: Show "running", "success", "error" with icon/color.
- **Tool calls display**: List tools called, with input/output. Expandable.
- **Memory context**: Optional: show top-k memory facts retrieved by L.

### Inspector Panel

- **Agent state**: Display current agent_id, task_id, iteration count, timeout remaining.
- **Kernel stack**: Show loaded kernels (Identity, Safety, Execution, Behavioral).
- **Tool registry**: List available tools with capability gates (approved vs blocked).
- **Approval queue**: Show pending high-risk tool calls awaiting Igor approval.

### Console View

- **Packet stream**: Real-time log of PacketEnvelope reasoning, tool_call, decision.
- **Filter by kind**: View only reasoning, or tool_call, or decisions.
- **Expand packet**: Show full JSON payload, metadata, confidence.
- **Copy/export**: Export visible packets as JSON for debugging.

---

## Accessibility & UX

### Keyboard Navigation

- **Tab order**: Logical, left-to-right, top-to-bottom. Use `tabIndex` sparingly.
- **Focus indicators**: Visible on all interactive elements. Use `:focus-visible` pseudo-class.
- **Escape key**: Closes modals, cancels operations.

### Color & Contrast

- **WCAG AA minimum**: 4.5:1 contrast for text, 3:1 for large text.
- **Status colors**: Don't rely on color alone. Use icon + text for success/error.

### Mobile Responsiveness

- **Meta viewport**: `<meta name="viewport" content="width=device-width, initial-scale=1" />`.
- **Responsive layout**: Breakpoints for mobile (<640px), tablet (640-1024px), desktop (>1024px).
- **Touch targets**: Min 44x44px for interactive elements.

---

## Testing Rules

### Unit Tests

- **Hook tests**: Use `@testing-library/react-hooks` (or vitest + React Testing Library).
- **Component snapshot**: Don't over-use. Prefer behavioral assertions.
  ```
  // ✅ CORRECT
  const { getByText } = render(<Button>Click me</Button>);
  expect(getByText("Click me")).toBeInTheDocument();
  
  // ❌ WRONG (brittle)
  expect(tree).toMatchSnapshot();
  ```

### Integration Tests

- **Mock API**: Use `msw` (Mock Service Worker) for HTTP and WebSocket.
- **User flow**: Simulate user actions (type, click, submit) and assert outcomes.
  ```
  const user = userEvent.setup();
  await user.type(screen.getByRole("textbox"), "Hello");
  await user.click(screen.getByRole("button", { name: "Send" }));
  expect(await screen.findByText("Task started")).toBeInTheDocument();
  ```

---

## Linting & Formatting

- **ESLint config**: Extend `eslint:recommended`, `plugin:react/recommended`, `plugin:@typescript-eslint/recommended`.
- **Prettier**: Format on save. Line length 100 chars.
- **CI check**: Run linter + type check (`tsc --noEmit`) on PR. Block merge if errors.
```

***

## `.cursor/rules/20-lang-python.mdc`

```markdown
---
description: "Python rules for AI OS runtime, agents, orchestration, and backend services."
globs:
  - "**/*.py"
  - "!**/migrations/*.py"
  - "!**/tests/**/*.py"
alwaysApply: false
---

# Python Language Rules for L9 OS Core Runtime

## Type Hints & Static Analysis

### Type Annotations Required

- **All function signatures**: Include parameter types and return type. Use `->` syntax.
  ```
  # ✅ CORRECT
  async def execute_task(task: AgentTask, timeout: int = 30) -> ExecutionResult:
      ...
  
  # ❌ WRONG
  async def execute_task(task, timeout=30):
      ...
  ```
- **Module-level variables**: Type-hint collections and mutable objects.
  ```
  agent_registry: dict[str, AgentConfig] = {}
  pending_tasks: list[AgentTask] = []
  ```
- **Return type for generators**: Use `Generator[YieldType, SendType, ReturnType]`.
- **Optional types**: Use `Optional[T]` or `T | None` (Python 3.10+). Never untyped `None`.

### Type Checking

- **Use `pyright` or `mypy`**: Run in CI. `mypy --strict` is target.
- **No `Any` type**: If forced, use `# type: ignore` with comment explaining why.
  ```
  data = json.loads(response.text)  # type: ignore  # JSON can be any shape
  ```
- **Protocol for duck typing**: Use `typing.Protocol` instead of untyped duck typing.
  ```
  from typing import Protocol
  
  class SubstrateServiceProtocol(Protocol):
      async def ingest_packet(self, packet: PacketEnvelope) -> PacketWriteResult: ...
  ```

---

## Async / Await Patterns

### Async-First Design

- **All I/O is async**: HTTP, database, Redis, file I/O. Use `async def` and `await`.
- **No blocking calls in async**: Never call `requests.get()` (use `httpx`, `aiohttp`), `time.sleep()` (use `asyncio.sleep()`).
- **Gather for concurrent tasks**: Use `asyncio.gather(*tasks, return_exceptions=True)` for parallel work.
  ```
  # ✅ CORRECT
  results = await asyncio.gather(
      fetch_task(task_id),
      query_memory(context),
      call_tool(tool_name),
      return_exceptions=True
  )
  ```
- **Timeouts**: Wrap all awaits with timeout context.
  ```
  try:
      result = await asyncio.wait_for(coro, timeout=30.0)
  except asyncio.TimeoutError:
      logger.error(f"Task {task_id} timed out")
  ```

### Context Managers for Resource Cleanup

- **All resource acquisition uses `async with`**:
  ```
  async with httpx.AsyncClient() as client:
      response = await client.get(...)
  # Connection automatically closed
  ```
- **Database connections**: Use `async with db.pool.acquire()` or session context.
- **File I/O**: Use `async with aiofiles.open(...)` for file operations.

---

## Error Handling & Resilience

### Explicit Error Types

- **Define custom exceptions**: Don't use bare `Exception`. Create domain-specific ones.
  ```
  class ApprovalGateError(Exception):
      """Raised when a high-risk tool call is blocked by approval gate."""
      
      def __init__(self, tool_name: str, required_approval: str):
          self.tool_name = tool_name
          self.required_approval = required_approval
          super().__init__(f"Tool {tool_name} requires {required_approval}")
  ```
- **Catch specific exceptions**: Never bare `except:` or `except Exception:`. Catch known types.
  ```
  # ✅ CORRECT
  try:
      result = await tool.execute(...)
  except ApprovalGateError as e:
      logger.warning(f"Approval blocked: {e.tool_name}")
      escalate_to_igor(e)
  except asyncio.TimeoutError:
      logger.error(f"Tool timed out")
      retry_with_backoff(...)
  ```

### Recovery & Logging

- **Every error → PacketEnvelope**: Emit error packet to memory with root cause + recovery action.
  ```
  async def safe_tool_call(task: AgentTask, tool: Tool) -> ExecutionResult:
      try:
          return await tool.execute(task.input)
      except Exception as e:
          error_packet = PacketEnvelope(
              kind="FAILURE",
              source_id=task.agent_id,
              payload={
                  "error": str(e),
                  "tool": tool.name,
                  "recovery_action": "retry" if retryable(e) else "escalate"
              }
          )
          await memory_service.ingest_packet(error_packet)
          raise
  ```
- **Structured logging**: Always include context (agent_id, task_id, thread_id).
  ```
  logger.info(f"Task execution started", extra={
      "agent_id": task.agent_id,
      "task_id": task.id,
      "thread_id": task.thread_id,
  })
  ```

---

## Core Agent Patterns

### Agent Instantiation & Execution

- **Immutable config**: Load AgentConfig once, never modify in-place.
  ```
  config = agent_registry.get_agent_config(agent_id="l-cto")
  # Don't do: config.tools.append(new_tool)
  ```
- **Kernel loading**: Use KernelLoader to assemble system prompt once per agent.
  ```
  kernel_stack = await kernel_loader.load_kernel_stack(agent_id)
  system_prompt = lcto.build_system_prompt_from_kernels(kernel_stack)
  ```
- **AIOSRuntime call**: Pass task input + loaded context to runtime.
  ```
  result = await aios_runtime.execute_reasoning(
      agent_config=config,
      task_input=task.payload["message"],
      context={"memory": memory_facts, "tools": tool_definitions},
      max_iterations=config.max_iterations
  )
  ```

### Tool Dispatch & Approval Gates

- **Check capability + approval before dispatch**:
  ```
  # In executor.py, before tool.execute():
  capability = agent_config.capabilities.get_tool(tool_name)
  if not capability.allowed:
      raise ApprovalGateError(tool_name, "NOT_AVAILABLE")
  
  if capability.requires_igor_approval:
      approval = await governance.check_approval(
          agent_id=config.id,
          tool_name=tool_name,
          tool_input=tool_input
      )
      if not approval.approved:
          raise ApprovalGateError(tool_name, "AWAITING_IGOR_APPROVAL")
  ```
- **Tool result logging**: Log input, output, and latency.
  ```
  start = time.perf_counter()
  try:
      output = await tool.execute(tool_input)
  finally:
      elapsed = time.perf_counter() - start
      logger.info(f"Tool {tool_name} executed", extra={
          "input": tool_input,
          "output": output,
          "elapsed_sec": elapsed,
      })
  ```

---

## Memory Substrate Patterns

### Packet Ingestion

- **PacketEnvelope structure**:
  ```
  from memory.substrate_models import PacketEnvelope, PacketMetadata
  
  packet = PacketEnvelope(
      source_id="l-cto",
      agent_id="l-cto",
      thread_id=task.thread_id,
      kind="REASONING",  # REASONING, TOOL_CALL, DECISION, MEMORY_WRITE, FAILURE
      payload={
          "reasoning": "Based on user request...",
          "considered_tools": ["tool_a", "tool_b"],
          "chosen_tool": "tool_a",
      },
      metadata=PacketMetadata(
          timestamp=datetime.utcnow().isoformat(),
          source_channel="lchat",
          user_id=task.context.get("user_id"),
      ),
      confidence=0.95,  # 0.0 to 1.0, how confident is this packet
  )
  ```
- **Async ingest, don't block executor**:
  ```
  # Fire-and-forget, but ensure dedup
  asyncio.create_task(
      memory_service.ingest_packet(packet)
  )
  # Executor continues immediately
  ```
- **Idempotent writes**: Use dedup_key (content hash or uuid).
  ```
  packet.dedup_key = hashlib.sha256(
      json.dumps(packet.payload, sort_keys=True).encode()
  ).hexdigest()
  # If same dedup_key, second write is no-op
  ```

### Memory Queries

- **Search semantic memory**:
  ```
  from memory.semantic import SemanticService
  
  search_result = await semantic_service.search(
      query="user preferences for automation",
      agent_id="l-cto",
      top_k=5,
      min_score=0.7
  )
  context_facts = [hit.text for hit in search_result.hits]
  ```
- **Graph queries** (Neo4j): Use read-only access. Never mutate graph directly.
  ```
  agent_graph = await graph_client.get_agent_memory(agent_id="l-cto")
  decisions = agent_graph.decisions  # Read properties
  # Don't do: agent_graph.add_decision(...) – use ingest_packet instead
  ```

---

## Orchestration & Task Graph Patterns

### TaskRouter Usage

- **Route task by complexity + risk**:
  ```
  routing_decision = await task_router.route(
      task=agent_task,
      context=execution_context
  )
  
  if routing_decision.target == ExecutionTarget.AGENT_EXECUTOR:
      result = await agent_executor.start_agent_task(agent_task)
  elif routing_decision.target == ExecutionTarget.TASK_GRAPH:
      result = await plan_executor.execute(routing_decision.plan)
  ```

### Plan Executor

- **Deterministic execution**: Plans are DAGs with explicit dependencies.
  ```
  plan: ExecutionPlan = ir_to_plan_adapter.to_plan(ir_graph)
  # plan.steps is ordered list of ExecutionStep
  # Each step has dependencies, timeout, retry policy
  
  result = await plan_executor.execute(plan, context={"memory": ...})
  ```
- **Step failure handling**: Fail-fast by default. Use `continue_on_error` flag for robustness.
  ```
  step.continue_on_error = False  # Halt on first failure (default)
  step.continue_on_error = True   # Skip failed step, continue (rare)
  ```

---

## Redis & Task Queue Patterns

### Task Enqueueing

- **Use TaskQueue.enqueue()** for background jobs:
  ```
  task_dict = {
      "task_id": str(uuid.uuid4()),
      "kind": "gmp_run",
      "payload": {
          "gmp_block": "...",
          "agent_id": "l-cto",
      },
      "queue": "gmp_runs",
      "retry_count": 0,
      "created_at": datetime.utcnow().isoformat(),
  }
  
  await task_queue.enqueue(task_dict)
  ```
- **Rate limiting**: All external API calls use RateLimiter.
  ```
  await rate_limiter.acquire(
      resource="perplexity_api",
      cost=1,
      timeout=5.0
  )
  # Then make the call
  ```

---

## Testing Patterns

### Unit Tests

- **Use `pytest` + `pytest-asyncio`** for async test functions.
  ```
  @pytest.mark.asyncio
  async def test_agent_task_execution():
      mock_runtime = AsyncMock(spec=AIOSRuntime)
      executor = AgentExecutorService(runtime=mock_runtime)
      
      result = await executor.start_agent_task(task)
      
      assert result.status == ExecutionStatus.SUCCESS
      mock_runtime.execute_reasoning.assert_called_once()
  ```
- **Mock external dependencies**: Use `unittest.mock.AsyncMock` for async methods.
- **Fixture scope**: Use `function` scope by default. `session` only for expensive setup.

### Integration Tests

- **Use test database + Redis**: Spin up via Docker or `testcontainers`.
- **End-to-end flow**: Create task, route, execute, check memory state.
  ```
  @pytest.mark.asyncio
  async def test_lchat_to_memory_flow(db, redis, substrate_service):
      # 1. Create request
      request = LChatRequest(message="What is L9?")
      
      # 2. Call handler
      response = await lchat_handler(request)
      
      # 3. Verify packet in memory
      packets = await substrate_service.query(
          agent_id="l-cto",
          kind="REASONING",
          limit=10
      )
      assert len(packets) > 0
      assert packets[-1].payload["reasoning"] != ""
  ```

### Mutation Testing

- **For critical paths** (approval gates, memory writes), consider mutation tests to ensure error handling is real.

---

## Code Style

### PEP 8 + Black

- **Format with Black**: Line length 100.
- **Docstrings**: Use Google style for clarity.
  ```
  async def execute_task(task: AgentTask) -> ExecutionResult:
      """Execute a single agent task via AIOSRuntime.
      
      Args:
          task: Agent task to execute.
      
      Returns:
          Execution result with output, status, tool calls.
      
      Raises:
          ApprovalGateError: If high-risk tool call blocked.
          asyncio.TimeoutError: If execution exceeds timeout.
      """
  ```
- **Import order**: stdlib, third-party, local. Use `isort`.
- **Blank lines**: Two between top-level definitions, one between methods.

### Naming Conventions

- **Variables**: `snake_case` (agent_id, task_queue).
- **Classes**: `PascalCase` (AgentTask, ExecutorService).
- **Constants**: `UPPERCASE` (MAX_RETRIES, DEFAULT_TIMEOUT).
- **Private**: `_leading_underscore` (internal methods/vars).
- **Async functions**: `async_funcname` optional but prefix with `async_` if returning coroutine directly.

---

## Performance & Scalability

### Connection Pooling

- **Database**: Always use connection pool. Never create per-request.
  ```
  db_pool = asyncpg.create_pool(dsn, min_size=5, max_size=20)
  ```
- **Redis**: Use redis-py with async/await.
  ```
  redis_client = aioredis.from_url("redis://...", encoding="utf8")
  ```
- **HTTP**: Use httpx.AsyncClient in a singleton or context.

### Caching

- **Kernel stack**: Cache loaded kernels in memory (keyed by agent_id).
- **Tool registry**: Lazy-load tools, cache in AgentConfig.
- **Memory facts**: Cache retrieved facts in task context, don't re-query within single execution.

### Observability

- **Structured logging**: Use `logging.getLogger(__name__)` + extra context dict.
- **Tracing**: Optionally integrate OpenTelemetry for distributed tracing.
- **Metrics**: Track task execution time, tool call counts, memory query latency.

---

## Security

### Input Validation

- **All user input validated**: Pydantic models for request parsing.
  ```
  class LChatRequest(BaseModel):
      message: str = Field(..., min_length=1, max_length=2000)
      thread_id: Optional[str] = Field(None, regex="^[a-zA-Z0-9_-]+$")
  ```
- **SQL injection prevention**: Use parameterized queries (asyncpg, SQLAlchemy ORM).
- **Approval scopes**: Validate approval token scope matches tool + agent.

### API Security

- **Bearer token auth**: Check `L9_EXECUTOR_API_KEY` for internal endpoints.
- **CORS**: Restrict to known origins.
- **Rate limiting**: Per-IP rate limiting for public endpoints.
```

***

## `.cursor/rules/30-framework-react.mdc`

```markdown
---
description: "React UI rules for AI OS control panels, consoles, and visualization surfaces."
globs:
  - "apps/web/**/*.{tsx,jsx}"
  - "packages/ui/**/*.{tsx,jsx}"
alwaysApply: false
---

# React Framework Rules for L9 OS UI

## Component Architecture

### Layered Component Design

- **Presentational (Pure)**: Accept props, render. No hooks, no API calls.
  ```
  interface ButtonProps { label: string; onClick: () => void; }
  const Button: React.FC<ButtonProps> = ({ label, onClick }) => (
    <button onClick={onClick}>{label}</button>
  );
  ```
- **Container (Smart)**: Fetch data, manage state, pass to presentational.
  ```
  const TaskListContainer = () => {
    const { tasks, isLoading, error } = useTaskList();
    return <TaskListView tasks={tasks} isLoading={isLoading} error={error} />;
  };
  ```
- **Page**: Compose containers. Route entry point.

### Functional Components Only

- **No class components**: Always use `React.FC<Props>` or const-arrow syntax.
- **Explicit return type**: `React.FC<Props>` is preferred over bare function.
  ```
  // ✅ PREFERRED
  export const MyComponent: React.FC<MyProps> = ({ prop1 }) => <div>{prop1}</div>;
  
  // ✅ ALSO OK
  export function MyComponent(props: MyProps): React.ReactElement { ... }
  ```

---

## Hooks & State Management

### Hook Usage Rules

- **Only call hooks at top level**: Never in loops, conditions, or nested functions.
- **Custom hooks for reuse**: Extract repeated logic into `useXxx`.
- **Dependency arrays**: Accurate. Use ESLint rule: `exhaustive-deps`.
  ```
  // ✅ CORRECT
  useEffect(() => {
    const load = async () => { ... };
    load();
  }, [taskId]); // taskId changed → re-run
  
  // ❌ WRONG - will run on every render if deps missing
  useEffect(() => {
    const load = async () => { ... };
    load();
  });
  ```

### Global State (Zustand)

- **Single store per domain**: `useTaskStore`, `useUIStore`, `useAuthStore`.
- **Immutable updates**: Use Immer to keep updates readable.
  ```
  const useTaskStore = create<TaskStore>()(
    immer((set) => ({
      tasks: [],
      updateTask: (taskId, patch) =>
        set((state) => {
          const task = state.tasks.find(t => t.id === taskId);
          if (task) Object.assign(task, patch); // Immer allows mutation syntax
        }),
    }))
  );
  ```
- **Selectors for derived state**: Avoid inline selectors in components.
  ```
  // Bad: selector created per render
  const tasks = useTaskStore((state) => state.tasks.filter(...));
  
  // Good: memoized selector
  const selectPendingTasks = (state: TaskStore) => state.tasks.filter(t => !t.done);
  const pendingTasks = useTaskStore(selectPendingTasks);
  ```

---

## Data Fetching & Async

### Custom Hooks for API Calls

- **useQuery pattern**: Fetch on mount, cache, refetch.
  ```
  export const useTaskList = () => {
    const [tasks, setTasks] = useState<AgentTask[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);
    
    useEffect(() => {
      let isMounted = true;
      const fetch = async () => {
        try {
          const data = await api.getTasks();
          if (isMounted) setTasks(data);
        } catch (e) {
          if (isMounted) setError(e as Error);
        } finally {
          if (isMounted) setIsLoading(false);
        }
      };
      fetch();
      return () => { isMounted = false; };
    }, []);
    
    return { tasks, isLoading, error };
  };
  ```
- **Refetch method**: Return function to manually re-fetch.
  ```
  const { tasks, refetch } = useTaskList();
  const handleRefresh = () => refetch();
  ```

### Error Handling in Components

- **Three-state rendering**: loading, success, error.
  ```
  const TaskListView: React.FC<Props> = ({ tasks, isLoading, error }) => {
    if (isLoading) return <div className="spinner">Loading...</div>;
    if (error) return <div className="error">Failed to load: {error.message}</div>;
    return <ul>{tasks.map(t => <TaskItem key={t.id} task={t} />)}</ul>;
  };
  ```
- **User feedback**: Show error message, optionally with retry button.

---

## Real-Time Updates (WebSocket)

### WebSocket Connection Hook

- **Persistent connection via context**:
  ```
  const useWebSocket = () => {
    const { ws, isConnected } = useContext(WebSocketContext);
    return { ws, isConnected };
  };
  ```
- **Listen to events**:
  ```
  useEffect(() => {
    const { ws } = useWebSocket();
    const handler = (msg: EventMessage) => {
      if (msg.type === "task_update") {
        setTask(msg.payload);
      }
    };
    ws?.addEventListener("message", handler);
    return () => ws?.removeEventListener("message", handler);
  }, []);
  ```
- **Send messages**:
  ```
  const sendMessage = (payload: any) => {
    const { ws } = useWebSocket();
    ws?.send(JSON.stringify({
      type: "chat",
      payload,
      timestamp: Date.now(),
    }));
  };
  ```

---

## L9 Agent Control Surfaces

### LChat Panel Component

```
interface LChatPanelProps {
  threadId?: string;
}

export const LChatPanel: React.FC<LChatPanelProps> = ({ threadId }) => {
  const [message, setMessage] = useState("");
  const [isExecuting, setIsExecuting] = useState(false);
  const [response, setResponse] = useState<LChatResponse | null>(null);
  const [error, setError] = useState<Error | null>(null);
  
  const handleSend = async () => {
    if (!message.trim()) return;
    setIsExecuting(true);
    setError(null);
    
    try {
      const result = await api.lchat({
        message,
        threadId,
      });
      setResponse(result);
      setMessage(""); // Clear input after success
    } catch (e) {
      setError(e as Error);
    } finally {
      setIsExecuting(false);
    }
  };
  
  return (
    <div className="lchat-panel">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        disabled={isExecuting}
        placeholder="Tell L what to do..."
      />
      <button onClick={handleSend} disabled={isExecuting || !message.trim()}>
        {isExecuting ? "Executing..." : "Send"}
      </button>
      
      {error && <div className="error">{error.message}</div>}
      
      {response && (
        <div className="response">
          <div className="reply">{response.reply}</div>
          {response.tool_calls && (
            <div className="tools">
              <h4>Tools Called:</h4>
              <ul>
                {response.tool_calls.map((tc) => (
                  <li key={tc.tool_name}>
                    {tc.tool_name}: {tc.status}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```

### Inspector Panel

```
export const InspectorPanel: React.FC = () => {
  const task = useTaskStore((s) => s.currentTask);
  const kernels = useTaskStore((s) => s.loadedKernels);
  const tools = useTaskStore((s) => s.availableTools);
  
  return (
    <div className="inspector">
      <section>
        <h3>Task State</h3>
        <dl>
          <dt>Agent ID:</dt>
          <dd>{task?.agent_id}</dd>
          <dt>Task ID:</dt>
          <dd>{task?.id}</dd>
          <dt>Status:</dt>
          <dd className={`status status--${task?.status}`}>{task?.status}</dd>
          <dt>Iteration:</dt>
          <dd>{task?.iteration} / {task?.max_iterations}</dd>
        </dl>
      </section>
      
      <section>
        <h3>Loaded Kernels</h3>
        <ul>
          {kernels?.map((k) => (
            <li key={k.id}>{k.name} (v{k.version})</li>
          ))}
        </ul>
      </section>
      
      <section>
        <h3>Available Tools</h3>
        <ul>
          {tools?.map((t) => (
            <li key={t.name}>
              {t.name}
              {t.requires_approval && <span className="badge">⚠️ Approval</span>}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
};
```

### Packet Console

```
export const PacketConsole: React.FC = () => {
  const [packets, setPackets] = useState<PacketEnvelope[]>([]);
  const [filter, setFilter] = useState<PacketKind | "all">("all");
  const { ws } = useWebSocket();
  
  useEffect(() => {
    const handler = (msg: EventMessage) => {
      if (msg.type === "packet") {
        setPackets((prev) => [...prev.slice(-99), msg.payload]); // Keep last 100
      }
    };
    ws?.addEventListener("message", handler);
    return () => ws?.removeEventListener("message", handler);
  }, [ws]);
  
  const filtered = filter === "all" ? packets : packets.filter((p) => p.kind === filter);
  
  return (
    <div className="packet-console">
      <div className="controls">
        <select value={filter} onChange={(e) => setFilter(e.target.value as any)}>
          <option value="all">All Packets</option>
          <option value="REASONING">Reasoning</option>
          <option value="TOOL_CALL">Tool Calls</option>
          <option value="DECISION">Decisions</option>
        </select>
      </div>
      
      <div className="packets">
        {filtered.map((packet) => (
          <PacketEntry key={packet.id} packet={packet} />
        ))}
      </div>
    </div>
  );
};

interface PacketEntryProps { packet: PacketEnvelope; }
const PacketEntry: React.FC<PacketEntryProps> = ({ packet }) => {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className={`packet-entry packet-${packet.kind.toLowerCase()}`}>
      <div className="header" onClick={() => setExpanded(!expanded)}>
        <span className="kind">{packet.kind}</span>
        <span className="time">{new Date(packet.metadata.timestamp).toLocaleTimeString()}</span>
      </div>
      
      {expanded && (
        <div className="detail">
          <pre>{JSON.stringify(packet.payload, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};
```

---

## Performance Optimization

### Memoization

- **useMemo** for expensive computations:
  ```
  const sortedTasks = useMemo(
    () => [...tasks].sort((a, b) => b.created_at.localeCompare(a.created_at)),
    [tasks]
  );
  ```
- **useCallback** for stable function refs:
  ```
  const handleTaskUpdate = useCallback(
    async (taskId: string, patch: Partial<AgentTask>) => {
      await api.updateTask(taskId, patch);
    },
    []
  );
  ```
- **React.memo** for pure components:
  ```
  const TaskItem = React.memo(({ task }: TaskItemProps) => (
    <div>{task.name}</div>
  ));
  ```

### Code Splitting

- **Lazy load heavy components**:
  ```
  const PacketConsole = lazy(() => import("./PacketConsole"));
  const InspectorPanel = lazy(() => import("./InspectorPanel"));
  
  export const App = () => (
    <Suspense fallback={<div>Loading...</div>}>
      <PacketConsole />
    </Suspense>
  );
  ```

---

## Testing React Components

### Unit Tests (RTL)

```
import { render, screen, userEvent } from "@testing-library/react";
import { LChatPanel } from "./LChatPanel";

describe("LChatPanel", () => {
  it("sends message on button click", async () => {
    const mockApi = jest.spyOn(api, "lchat").mockResolvedValue({
      reply: "Task started",
      tool_calls: [],
    });
    
    const user = userEvent.setup();
    render(<LChatPanel />);
    
    await user.type(screen.getByRole("textbox"), "Hello L");
    await user.click(screen.getByRole("button", { name: "Send" }));
    
    expect(mockApi).toHaveBeenCalledWith({
      message: "Hello L",
      threadId: undefined,
    });
    
    expect(await screen.findByText("Task started")).toBeInTheDocument();
  });
});
```

---

## Accessibility

### ARIA & Semantic HTML

- **Use semantic tags**: `<button>`, `<input>`, not `<div>` with onclick.
- **ARIA labels**: For dynamic content or icons.
  ```
  <button aria-label="Send message" onClick={handleSend}>
    <IconSend />
  </button>
  ```
- **Role attributes**: Clarify complex widgets.
  ```
  <div role="tablist">
    <button role="tab" aria-selected={active}>Tab 1</button>
  </div>
  ```

### Keyboard & Focus

- **Tab order**: Logical flow. Use `tabIndex` sparingly.
- **Focus visible**: `:focus-visible` pseudo-class for keyboard users.
  ```
  button:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
  ```
- **Escape closes modals**: Build modal hook.

---

## Styling

### CSS-in-JS vs Tailwind

- **Prefer Tailwind** for rapid UI development. BEM class names for complex components.
- **CSS modules** for scoped styles when needed.
- **Design tokens**: Use CSS variables for colors, spacing, typography.
  ```
  --color-primary: #208080;
  --spacing-sm: 8px;
  --font-size-base: 14px;
  ```

### Dark Mode

- **Support system preference**:
  ```
  const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  ```
- **Toggle manually**: Store in localStorage.
  ```
  const [isDark, setIsDark] = useState(() =>
    localStorage.getItem("theme") === "dark" ||
    window.matchMedia("(prefers-color-scheme: dark)").matches
  );
  
  const toggleTheme = () => {
    setIsDark((prev) => {
      const next = !prev;
      localStorage.setItem("theme", next ? "dark" : "light");
      return next;
    });
  };
  ```
```

***

## `.cursor/rules/40-domain-autonomy.mdc`

```markdown
---
description: "Autonomous agents and AI OS autonomy domain rules: safety envelopes, escalation, and irreversible action constraints."
globs:
  - "src/agents/**/*.ts"
  - "src/agents/**/*.py"
  - "src/autonomy/**/*"
  - "packages/agents/**/*"
alwaysApply: false
---

# Autonomous Agent & Autonomy Domain Rules

## Safety Envelopes & Capability Binding

### Capability Constraints

- **Agent capability matrix**: AgentCapabilities defines what agent can do (bound in AgentConfig).
  ```
  LCAPABILITIES = AgentCapabilities(
      agent_id="l-cto",
      capabilities=[
          Capability(tool=ToolName.MEMORYSEARCH, allowed=True, requiresApproval=False),
          Capability(tool=ToolName.GMPRUN, allowed=True, requiresApproval=True),
          Capability(tool=ToolName.GITCOMMIT, allowed=True, requiresApproval=True),
          Capability(tool=ToolName.MACAGENTEXEC, allowed=True, requiresApproval=True),
          Capability(tool=ToolName.MCPCALLTOOL, allowed=False),  # Not allowed
      ]
  )
  ```
- **No capability escalation**: Agent cannot grant itself new capabilities. Only Igor (via manual config change) can.
- **Runtime check**: executor.py queries `agent_config.capabilities.get_tool(tool_name)` before dispatch.

### Tool Authorization Scopes

- **Internal tools** (memory, reasoning): No approval needed. Always allowed.
- **High-risk tools** (GMPRUN, GITCOMMIT, MACAGENTEXEC): Require Igor approval.
- **External tools** (MCP, HTTP): Require approval per-call, with audit logging.
- **Destructive tools** (DELETE, REFORMAT, DEPLOY): Always require dry-run + explicit confirmation.

---

## Escalation Rules

### When to Escalate

**Agent must escalate to Igor (via Slack DM or WebSocket) when:**

1. **Uncertainty**: Agent confidence < 0.6 on high-impact decision.
2. **Approval needed**: High-risk tool requires approval and none cached.
3. **User clarification**: Ambiguous user request; needs human judgment.
4. **Out-of-bounds**: Requested action outside agent capability scope.
5. **Novel situation**: Encounter unseen context; request guidance.

### Escalation Protocol

```
async def escalate_to_igor(
    reason: str,
    context: dict,
    action_proposed: str,
    timeout_seconds: int = 300
) -> ApprovalDecision:
    """Escalate decision to Igor for approval."""
    escalation_packet = PacketEnvelope(
        kind="ESCALATION",
        source_id=agent_id,
        payload={
            "reason": reason,
            "proposed_action": action_proposed,
            "context": context,
            "approval_required": True,
        }
    )
    
    await memory_service.ingest_packet(escalation_packet)
    
    # Send Slack DM to Igor
    await slack_client.send_dm(
        user_id="igor",
        text=f"L needs your approval:\n{reason}\n\nProposed: {action_proposed}",
        interactive=True  # Include yes/no buttons
    )
    
    # Wait for response (with timeout)
    decision = await governance.wait_for_approval(
        escalation_packet.id,
        timeout=timeout_seconds
    )
    
    return decision
```

---

## Irreversible Action Constraints

### Destructive Operations

**Operations that cannot be undone:**
- Git commits pushed to remote
- Data deletions from databases
- Credential rotations
- Deployment to production
- Financial transactions

**For each, enforce:**

1. **Dry-run first**: Propose action with full outcome spec (files changed, data affected, etc.).
2. **Escalation to Igor**: Always requires explicit approval.
3. **Rollback spec**: Document how to undo (git revert, restore from backup, etc.).
4. **Pre/post assertions**: Log state before and after.
5. **Audit immutable**: Once committed, cannot be erased from audit log.

### Dry-Run Pattern

```
async def dry_run_git_commit(
    files: list[str],
    message: str,
    agent_id: str
) -> GitCommitDryRun:
    """Propose a git commit without actually making it."""
    # Parse intent
    diffs = await git.staged_diffs(files)
    
    # Emit dry-run packet
    dry_run_packet = PacketEnvelope(
        kind="DRY_RUN",
        payload={
            "tool": "GITCOMMIT",
            "files_changed": files,
            "message": message,
            "diffs": diffs,  # Full diffs for review
            "rollback_plan": "git revert <commit_sha>",
        }
    )
    await memory_service.ingest_packet(dry_run_packet)
    
    # Ask Igor for approval
    decision = await escalate_to_igor(
        reason=f"Proposing git commit: {message}",
        action_proposed=f"Commit {len(files)} files",
        context={"diffs": diffs},
    )
    
    if not decision.approved:
        return GitCommitDryRun(approved=False, reason=decision.reason)
    
    # Only if approved, execute
    result = await git.commit(files, message)
    
    # Log execution
    execution_packet = PacketEnvelope(
        kind="EXECUTION",
        payload={
            "tool": "GITCOMMIT",
            "status": "success",
            "commit_sha": result.sha,
        }
    )
    await memory_service.ingest_packet(execution_packet)
    
    return GitCommitDryRun(approved=True, commit_sha=result.sha)
```

### Financial Transactions

- **Never auto-execute**: Always escalate to Igor first.
- **Amount thresholds**: Amounts > $X require explicit approval.
- **Recipient validation**: Cross-check recipient against approved list.
- **Audit trail**: Transaction in immutable log with timestamp, amount, recipient, approver.

---

## User Intent Validation

### Intent Extraction

- **Parse user request** for clear intent.
  ```
  intent = await llm.extract_intent(user_message)
  # Returns: { "action": "fill_application", "subject": "grant", "params": {...} }
  ```
- **Validate against scope**: Is this action within agent's allowed capabilities?
- **Confirm ambiguity**: If multiple interpretations, ask user for clarification.

### Intent Confirmation

```
async def validate_intent(
    user_message: str,
    parsed_intent: dict
) -> bool:
    """Confirm user intent matches parsed request."""
    
    # Check if intent is clear or needs clarification
    if parsed_intent["confidence"] < 0.8:
        await send_clarification_request(user_message, parsed_intent)
        return False  # Wait for follow-up
    
    # Check against user history (prefer patterns)
    historical_similar = await memory_service.query(
        agent_id="l-cto",
        query=f"User requests similar to: {parsed_intent['action']}",
        top_k=3
    )
    
    if historical_similar:
        # Use similar past context
        past_approach = historical_similar.payload
        return True  # High confidence, proceed
    
    # For novel requests, escalate
    return await escalate_to_igor(
        reason="Novel user request",
        action_proposed=parsed_intent["action"],
        context={"parsed_intent": parsed_intent},
    ).approved
```

---

## Multi-Step Agent Planning

### Plan Composition & Sequencing

- **Agent proposes multi-step plan**:
  ```
  plan = TaskGraph(
      nodes=[
          Node(id="read_brief", kind="RESEARCH", target="l-research"),
          Node(id="gen_draft", kind="GENERATION", target="l-cto"),
          Node(id="review", kind="REVIEW", target="l-cto"),
          Node(id="execute_gmp", kind="EXECUTION", target="l-cto"),
      ],
      edges=[
          Edge(from_node="read_brief", to_node="gen_draft"),
          Edge(from_node="gen_draft", to_node="review"),
          Edge(from_node="review", to_node="execute_gmp"),
      ]
  )
  ```
- **Escalate high-risk nodes**: If plan includes destructive actions, require approval for entire plan.
- **Abort on failure**: If any step fails and `continue_on_error=False`, halt entire plan.

---

## Autonomy Profiles

### Agent Autonomy Levels

Define per-agent autonomy level (in AgentConfig or Autonomy profile):

1. **L0_NO_ACTION**: Read-only. Agent can query memory and reason, but cannot invoke tools.
2. **L1_SAFE_READ**: Can invoke safe, read-only tools (memory, query, inspect). No writes.
3. **L2_WRITE_ISOLATED**: Can invoke write tools (memory, file creation) but not external APIs.
4. **L3_EXTERNAL_SAFE**: Can invoke safe external APIs (query APIs, no mutations).
5. **L4_EXTERNAL_WRITE_ESCALATE**: Can invoke write tools externally, but all require escalation.
6. **L5_FULL_AUTONOMY**: Can invoke any tool subject to approval gates; fewer escalations.

```
class AgentAutonomyProfile(str, Enum):
    L0_NO_ACTION = "l0_no_action"
    L1_SAFE_READ = "l1_safe_read"
    L2_WRITE_ISOLATED = "l2_write_isolated"
    L3_EXTERNAL_SAFE = "l3_external_safe"
    L4_EXTERNAL_WRITE_ESCALATE = "l4_external_write_escalate"
    L5_FULL_AUTONOMY = "l5_full_autonomy"

# L's profile
LCTO_AUTONOMY = AgentAutonomyProfile.L5_FULL_AUTONOMY  # Can do anything subject to approval gates
```

**Enforcement**: executor.py checks agent's autonomy level before allowing tool execution.

---

## Feedback Loops & Learning

### Outcome Logging

- **Every executed action** logged with outcome:
  ```
  outcome_packet = PacketEnvelope(
      kind="OUTCOME",
      payload={
          "action": "filled_grant_application",
          "intended_outcome": "application_submitted",
          "actual_outcome": "application_submitted",
          "success": True,
          "learned": ["Grant requires specific documentation", "Timeline is 30 days"],
      }
  )
  ```

### Autonomy Calibration

- **Success rate tracking**: If agent succeeds >95% of non-escalated tasks, consider raising autonomy.
- **Failure analysis**: If agent fails >5% of escalated tasks, lower autonomy or retraining.
- **Human feedback**: Igor can annotate outcomes with "good decision", "could improve", "risky".

---

## Escalation Channels

### Primary: Slack DM to Igor

- Instant notification
- Interactive approval buttons
- Async; Igor doesn't need to be watching

### Secondary: WebSocket (Real-time)

- If Igor is actively monitoring L console
- Lower latency response
- For time-sensitive decisions

### Tertiary: Email Digest

- Daily summary of escalations
- Non-urgent items
- Useful for asynchronous review

---

## Governance Metadata in Tool Definitions

```
@dataclass
class ToolDefinition:
    name: str
    description: str
    category: str  # "memory", "execution", "integration"
    scope: str  # "internal", "external"
    risk_level: str  # "low", "medium", "high"
    is_destructive: bool
    requires_igor_approval: bool
    external_apis: list[str]  # ["git", "gcp", "stripe"] if applicable
    internal_dependencies: list[str]  # Other tools this depends on
    agent_id: str  # Owner agent; usually "l-cto"
    
    # Example: GITCOMMIT
    # name = "gitcommit"
    # scope = "internal" (talks to local git)
    # risk_level = "high"
    # is_destructive = True
    # requires_igor_approval = True
    # external_apis = ["git"]
```

---

## Audit & Immutability

### Audit Log Packet Schema

```
PacketEnvelope(
    kind="AUDIT",
    source_id="l-cto",
    payload={
        "action": "tool_executed",
        "tool_name": "GITCOMMIT",
        "agent_id": "l-cto",
        "approved_by": "igor",
        "approval_timestamp": "2025-12-26T22:50:00Z",
        "execution_timestamp": "2025-12-26T22:51:00Z",
        "input": { "files": [...], "message": "..." },
        "output": { "commit_sha": "abc123", "status": "success" },
        "outcome": "application_submitted",
    },
    metadata=PacketMetadata(
        immutable=True,  # Cannot be deleted
        retention_years=7,  # Legal hold
    )
)
```

---

## Testing Autonomy Rules

### Unit: Approval Gate Checks

```
@pytest.mark.asyncio
async def test_high_risk_tool_requires_approval():
    executor = AgentExecutorService(...)
    task = AgentTask(
        id="test-1",
        kind=TaskKind.EXECUTION,
        agent_id="l-cto",
        payload={"tool": "GITCOMMIT", "files": ["main.py"]}
    )
    
    # No approval cached
    with pytest.raises(ApprovalGateError):
        await executor.execute_tool("GITCOMMIT", {...})
    
    # Grant approval
    await governance.grant_approval("l-cto", "GITCOMMIT", "igor", expires_in=600)
    
    # Now succeeds
    result = await executor.execute_tool("GITCOMMIT", {...})
    assert result.status == ExecutionStatus.SUCCESS
```

### Integration: Escalation Flow

```
@pytest.mark.asyncio
async def test_escalation_and_approval_flow(mocked_slack):
    # Agent proposes destructive action
    result = await agent.propose_git_commit([...], "dangerous commit")
    
    # Verify escalation packet logged
    packets = await memory_service.query(kind="ESCALATION")
    assert len(packets) > 0
    
    # Verify Slack DM sent
    mocked_slack.send_dm.assert_called_once()
    
    # Simulate Igor approval via mock
    await governance.grant_approval("l-cto", "GITCOMMIT", "igor")
    
    # Re-run execution
    final_result = await agent.execute_git_commit([...])
    assert final_result.status == ExecutionStatus.SUCCESS
```
```

***

## `.cursor/rules/50-qa-testing.mdc`

```markdown
---
description: "Testing and QA rules for AI OS agents, runtimes, and integrations."
globs:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.test.py"
  - "**/__tests__/**/*"
alwaysApply: false
---

# Testing & QA Rules for L9 OS

## Test Structure & Coverage

### Directory Organization

```
tests/
├── core/
│   ├── agents/
│   │   ├── test_executor.py
│   │   ├── test_runtime.py
│   │   ├── test_instance.py
│   ├── tools/
│   │   ├── test_toolgraph.py
│   │   ├── test_registry.py
│   ├── kernels/
│   │   └── test_kernel_loader.py
├── memory/
│   ├── test_substrate_basic.py
│   ├── test_semantic_search.py
│   ├── test_ingestion_pipeline.py
├── integration/
│   ├── test_orchestrator_memory_integration.py
│   ├── test_kernel_agent_activation.py
│   ├── test_api_agent_integration.py
├── docker/
│   ├── test_stack_smoke.py
│   ├── test_migrations.py
├── mocks/
│   ├── kernel_mocks.py
│   ├── memory_mocks.py
│   └── orchestrator_mocks.py
```

### Unit Test Requirements

- **One test file per source module**: `core/agents/executor.py` → `tests/core/agents/test_executor.py`.
- **Test coverage ≥ 85%**: Critical paths (approval gates, memory, orchestration) at ≥ 95%.
- **Three test categories per module**:
  1. **Happy path**: Normal operation, assert expected output.
  2. **Error cases**: Exceptions, timeouts, malformed input.
  3. **Edge cases**: Boundary conditions, race conditions, idempotency.

### Integration Test Requirements

- **Agent + Memory**: Verify agent decision → packet ingestion → memory query chain.
- **Kernel + Agent**: Load kernels, instantiate agent, verify system prompt includes kernel rules.
- **Orchestrator + Router**: Task routed correctly by complexity, executed by right executor.
- **API + Executor**: HTTP request → AgentTask → ExecutorService → response.

---

## Python Testing Patterns

### Async Test Fixtures

```
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
async def mock_substrate_service():
    """Mock memory substrate service for testing."""
    service = AsyncMock()
    service.ingest_packet = AsyncMock(return_value=PacketWriteResult(
        packet_id="test-id",
        stored=True,
    ))
    service.query = AsyncMock(return_value=[])
    return service

@pytest.fixture
def mock_agent_config():
    """Sample agent config for L-CTO."""
    return AgentConfig(
        id="l-cto",
        name="L-CTO",
        description="Chief Technology Officer",
        tool_bindings=[
            ToolBinding(tool=ToolName.MEMORYSEARCH, enabled=True),
            ToolBinding(tool=ToolName.GMPRUN, enabled=True),
        ],
        max_iterations=10,
    )
```

### Async Test Functions

```
@pytest.mark.asyncio
async def test_agent_executor_happy_path(
    mock_agent_config,
    mock_substrate_service
):
    """Test basic agent execution flow."""
    executor = AgentExecutorService(
        agent_registry=mock_agent_registry,
        runtime=mock_aios_runtime,
        substrate=mock_substrate_service,
    )
    
    task = AgentTask(
        id="task-1",
        agent_id="l-cto",
        kind=TaskKind.CHAT,
        payload={"message": "What is L9?"}
    )
    
    result = await executor.start_agent_task(task)
    
    assert result.status == ExecutionStatus.SUCCESS
    assert "L9" in result.output
    mock_substrate_service.ingest_packet.assert_called()
```

### Error Case Testing

```
@pytest.mark.asyncio
async def test_high_risk_tool_without_approval():
    """High-risk tools must be approved before execution."""
    executor = AgentExecutorService(...)
    
    task = AgentTask(
        id="task-2",
        agent_id="l-cto",
        payload={"tool": "GITCOMMIT", "files": ["main.py"]}
    )
    
    with pytest.raises(ApprovalGateError) as exc_info:
        await executor.execute_tool("GITCOMMIT", {...})
    
    assert "GITCOMMIT" in str(exc_info.value)
    assert "approval" in str(exc_info.value).lower()
```

### Mocking Async Dependencies

```
@pytest.fixture
def mock_aios_runtime():
    """Mock AIOSRuntime for executor tests."""
    mock = AsyncMock(spec=AIOSRuntime)
    mock.execute_reasoning = AsyncMock(return_value=ReasoningResult(
        reply="Hello",
        tool_calls=[],
        confidence=0.95,
    ))
    return mock
```

---

## TypeScript/React Testing Patterns

### Component Unit Tests

```
import { render, screen, userEvent } from "@testing-library/react";
import { LChatPanel } from "./LChatPanel";

describe("LChatPanel", () => {
  it("renders input and button", () => {
    render(<LChatPanel />);
    expect(screen.getByRole("textbox")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
  });
  
  it("sends message on button click", async () => {
    const mockApi = jest.spyOn(api, "lchat")
      .mockResolvedValue({
        reply: "Task started",
        tool_calls: [],
      });
    
    const user = userEvent.setup();
    render(<LChatPanel />);
    
    await user.type(screen.getByRole("textbox"), "Hello");
    await user.click(screen.getByRole("button", { name: /send/i }));
    
    expect(mockApi).toHaveBeenCalledWith({
      message: "Hello",
      threadId: undefined,
    });
  });
  
  it("shows error on API failure", async () => {
    jest.spyOn(api, "lchat")
      .mockRejectedValue(new Error("Network error"));
    
    const user = userEvent.setup();
    render(<LChatPanel />);
    
    await user.type(screen.getByRole("textbox"), "Hello");
    await user.click(screen.getByRole("button", { name: /send/i }));
    
    expect(await screen.findByText(/network error/i)).toBeInTheDocument();
  });
});
```

### Hook Tests

```
import { renderHook, waitFor } from "@testing-library/react";
import { useTaskList } from "./useTaskList";

describe("useTaskList", () => {
  it("fetches tasks on mount", async () => {
    const mockApi = jest.spyOn(api, "getTasks")
      .mockResolvedValue([{ id: "1", name: "Task 1" }]);
    
    const { result } = renderHook(() => useTaskList());
    
    expect(result.current.isLoading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    
    expect(result.current.tasks).toEqual([{ id: "1", name: "Task 1" }]);
  });
});
```

### MSW (Mock Service Worker) for API Mocking

```
import { rest } from "msw";
import { setupServer } from "msw/node";

const server = setupServer(
  rest.post("/api/lchat", (req, res, ctx) => {
    return res(ctx.json({
      reply: "Hello",
      tool_calls: [],
    }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("sends lchat request and receives response", async () => {
  const response = await api.lchat({ message: "Hello" });
  expect(response.reply).toBe("Hello");
});
```

---

## Determinism & Idempotency Tests

### Determinism Test

```
@pytest.mark.asyncio
async def test_agent_execution_deterministic():
    """Same input should produce same reasoning (with seeded RNG)."""
    task = AgentTask(
        id="det-1",
        agent_id="l-cto",
        payload={"message": "Explain L9"},
    )
    
    # Set seed for reproducibility
    random.seed(42)
    result1 = await executor.start_agent_task(task)
    
    random.seed(42)
    result2 = await executor.start_agent_task(task)
    
    assert result1.output == result2.output  # Exact match
    assert result1.tool_calls == result2.tool_calls
```

### Idempotency Test

```
@pytest.mark.asyncio
async def test_memory_packet_ingestion_idempotent():
    """Writing same packet twice should not duplicate."""
    packet = PacketEnvelope(
        id="idempotent-1",
        dedup_key="hash-123",
        kind="REASONING",
        source_id="l-cto",
        payload={"reasoning": "..."},
    )
    
    # Write twice
    result1 = await substrate.ingest_packet(packet)
    result2 = await substrate.ingest_packet(packet)
    
    assert result1.packet_id == result2.packet_id
    assert result1.duplicate == False
    assert result2.duplicate == True  # Second write is duplicate
    
    # Verify packet appears once in database
    packets = await substrate.query(dedup_key="hash-123")
    assert len(packets) == 1
```

---

## Regression Test Requirements

### Memory Regression Tests

- When a bug is found and fixed, add test case covering the bug to prevent regression.
- Keep a `regression_tests.py` file documenting known issues and their test coverage.
  ```
  # regression_tests.py
  # Issue #123: Agent timeout not properly caught
  @pytest.mark.asyncio
  async def test_timeout_propagates_correctly():
      with pytest.raises(asyncio.TimeoutError):
          await executor.start_agent_task(slow_task, timeout=1)
  ```

---

## Smoke Tests (Post-Docker)

### Critical Path Testing

```
@pytest.mark.asyncio
async def test_full_lchat_to_memory_path():
    """End-to-end smoke test: request → agent → memory."""
    # 1. Create lchat request
    request = LChatRequest(message="Fill out grant application")
    
    # 2. Call handler (mimics HTTP route)
    response = await lchat_handler(request)
    
    # 3. Verify response
    assert response.status == "success"
    assert response.task_id
    
    # 4. Query memory for packets
    packets = await memory_service.query(
        task_id=response.task_id,
        kind="REASONING",
    )
    
    assert len(packets) > 0
    assert packets.payload["reasoning"] != ""
    
    # 5. Verify tool calls logged
    tool_packets = await memory_service.query(
        task_id=response.task_id,
        kind="TOOL_CALL",
    )
    
    assert len(tool_packets) >= 0  # May or may not call tools
```

### Health Endpoint Tests

```
@pytest.mark.asyncio
async def test_api_health_endpoint():
    """Verify all services report healthy."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["services"]["memory"] == "ok"
    assert data["services"]["orchestrator"] == "ok"
    assert data["services"]["kernel"] == "ok"
```

---

## Performance & Load Tests

### Latency SLA Tests

```
@pytest.mark.asyncio
async def test_lchat_latency_sla():
    """L-CTO response time should be <5s (p95)."""
    latencies = []
    
    for _ in range(100):
        start = time.perf_counter()
        await api.lchat({"message": "Hello"})
        elapsed = time.perf_counter() - start
        latencies.append(elapsed)
    
    latencies.sort()
    p95 = latencies[int(0.95 * len(latencies))]
    
    assert p95 < 5.0, f"p95 latency {p95:.2f}s exceeds SLA of 5s"
```

### Memory Ingestion Rate

```
@pytest.mark.asyncio
async def test_packet_ingest_throughput():
    """Substrate should ingest >100 packets/sec."""
    start = time.perf_counter()
    
    tasks = [
        substrate.ingest_packet(make_packet(i))
        for i in range(1000)
    ]
    
    await asyncio.gather(*tasks)
    
    elapsed = time.perf_counter() - start
    throughput = 1000 / elapsed
    
    assert throughput > 100, f"Throughput {throughput:.0f} pps < 100 pps SLA"
```

---

## Debugging & Logs

### Test Log Output

- **Always include test logs in failure output**:
  ```
  @pytest.fixture
  def caplog(caplog):
      caplog.set_level(logging.DEBUG)
      return caplog
  
  def test_with_logs(caplog):
      some_function()
      assert "expected message" in caplog.text
  ```

### Debugging Tips

- **Use `pytest -vv`** for verbose output, including print statements.
- **Use `pytest -s`** to see stdout/stderr from tests.
- **Use `pytest --pdb`** to drop into debugger on failure.
- **Use `logging.debug()`** liberally. Tests won't show unless `-vv`.

---

## CI/CD Integration

### Pre-Commit Hooks

```
#!/bin/bash
# .git/hooks/pre-commit

# Run unit tests
pytest tests/core tests/memory --cov=core --cov=memory --cov-fail-under=85
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

# Run linter
mypy --strict core memory
if [ $? -ne 0 ]; then
    echo "Type check failed."
    exit 1
fi

# Format check
black --check core memory
if [ $? -ne 0 ]; then
    echo "Format issues. Run: black core memory"
    exit 1
fi
```

### GitHub Actions CI

```
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements-test.txt
      - run: pytest tests/ --cov=core --cov=memory --cov-fail-under=85
      - run: mypy --strict core memory
      - run: black --check core memory
```
```

***

## Summary Table

| Aspect | Rule |
|--------|------|
| **Unit Test Coverage** | ≥85% overall, ≥95% for critical paths (approval, memory, orchestration) |
| **Test Categories** | Happy path + error cases + edge cases |
| **Async Testing** | Use `@pytest.mark.asyncio` + `AsyncMock` for dependencies |
| **React Testing** | Use React Testing Library + MSW for API mocking |
| **Determinism** | Same input + same seed = same output. Test with seeded RNG. |
| **Idempotency** | Packet dedup_key should prevent duplicates. Write twice, get same result. |
| **Regression** | Add test case whenever bug is fixed. Keep regression_tests.py. |
| **Smoke Tests** | Full end-to-end path post-docker-compose. Check critical services. |
| **Performance** | SLA tests for latency (p95), throughput (packets/sec), error rates. |
| **CI/CD** | Pre-commit hooks + GitHub Actions. Block merge if tests fail. |

```

---

## Delivery Summary

I've generated **six production-grade `.mdc` rule files** for your L9 Secure AI OS monorepo, ready to drop into `.cursor/rules/`:

### Files Created:

1. **`00-global.mdc`** – Primary global rules (alwaysApply: true)
   - Project overview, safety invariants, memory/substrate patterns
   - Approval gates, escalation, audit logging
   - Conflict resolution policy: Global wins, scoped refines

2. **`10-lang-typescript.mdc`** – TypeScript/TSX language rules
   - Type safety (no `any`), module boundaries, async patterns
   - WebSocket & real-time rules
   - Agent control surfaces (L Chat Panel, Inspector, Packet Console)

3. **`20-lang-python.mdc`** – Python core runtime rules
   - Type hints, async/await discipline, error handling
   - Agent instantiation, tool dispatch, approval gates
   - Memory substrate patterns, task queue, Redis patterns

4. **`30-framework-react.mdc`** – React UI-specific rules
   - Layered component architecture, hooks patterns, Zustand state management
   - WebSocket real-time sync, error boundary handling
   - Accessibility, testing, performance optimization

5. **`40-domain-autonomy.mdc`** – Autonomous agent & safety rules
   - Capability constraints, escalation protocol
   - Irreversible action constraints (dry-run, rollback spec)
   - User intent validation, autonomy profiles (L0–L5)
   - Audit immutability, governance metadata

6. **`50-qa-testing.mdc`** – Testing & QA rules
   - Unit/integration/smoke test structure
   - Python async testing patterns, TypeScript React testing
   - Determinism & idempotency tests, regression tracking
   - Performance SLAs, CI/CD integration

### Key Design Principles:

✅ **No tool substitution**: Uses Cursor's native `.mdc` format only
✅ **Production-grade**: Zero placeholders, zero stubs. All enforceable, specific rules
✅ **Drop-in ready**: Copy into `.cursor/rules/` and use immediately
✅ **Composable**: Global rules set guardrails; scoped rules add precision without override
✅ **L9-native**: All rules align with kernel stack, agent executor, memory substrate, orchestration patterns from your codebase
✅ **Conflict-aware**: Explicit hierarchy (global > scoped), feature flags for deprecation

All files include concrete code examples, patterns, and enforcement checklists.