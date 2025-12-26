module:
  id: "tool.registry"
  name: "Tool Registry + Dispatcher"
  profile: "orchestrator"

  purpose: >
    Provide a single, canonical OS-level tool contract for all L9 agents
    and integrations: register tools, validate arguments, enforce governance,
    dispatch execution, and persist deterministic execution traces.

  goals:
    - "Expose a uniform tool interface to all agents across all domains"
    - "Eliminate per-integration glue code and ad-hoc dispatch logic"
    - "Guarantee governance checks before any side-effect execution"
    - "Make every tool call auditable, replayable, and debuggable"

  non_goals:
    - "Implement domain tools themselves (Slack, Email, Mac, Web, etc.)"
    - "Contain agent reasoning or decision logic"
    - "Introduce new persistence layers outside the memory substrate"

  scale:
    family: "core"
    batch: "phase_1_P0"
    dependency_tier: 0
    rollout_order: 2

  repo:
    root_path: "l9/"
    enforce_relative_imports_from_root: true
    must_import_and_use:
      - "memory.substrate_service"
      - "memory.packet_envelope"
      - "governance.policy_engine"
    must_not_create:
      - "parallel tool registry"
      - "parallel schema validation stack"
      - "direct side effects bypassing governance"
    allowed_new_files:
      - "core/tools/registry.py"
      - "core/tools/dispatcher.py"
      - "core/tools/schemas.py"
      - "tests/test_tool_dispatch.py"
      - "docs/tools.md"
    allowed_modified_files: []

  schema_truth:
    tables:
      - "packet_store"
      - "tasks"
      - "knowledge_facts"
    notes: >
      Tool calls and outcomes are persisted as packet envelopes.
      Deferred or approval-gated actions may be represented as tasks.

  interfaces:
    inbound:
      - "tools.register(tool_def: ToolDef) -> None"
      - "tools.list(*, tags=None) -> list[ToolDef]"
      - "tools.get(tool_name: str) -> ToolDef | None"
      - "tools.validate(tool_name: str, args: dict) -> ValidationResult"
      - "tools.dispatch(tool_name: str, args: dict, context: ToolContext) -> ToolResult"
    outbound:
      - "governance.evaluate(action_intent, context) -> decision"
      - "memory.substrate_service.write_packet(envelope) -> result"
      - "tasks.create(...) optional (for gated or deferred execution)"

  orchestration:
    context_reads:
      - "thread_id / thread_uuid"
      - "principal (user or service identity)"
      - "role / permissions (if available)"
      - "approval_token (if provided)"
    aios_calls: []
    persistence_writes:
      - "packet_store: tool.call.request"
      - "packet_store: tool.call.decision"
      - "packet_store: tool.call.result"
      - "tasks: optional for approval-required actions"

  policies:
    auth_and_verification:
      mode: "internal_only"

    idempotency:
      enabled: true
      primary_key: "thread_id + tool_name + normalized_args_hash"
      fallback_key: "request_uuid"
      on_duplicate: "return_cached_result"

    error_policy:
      invalid_auth_or_signature: "raise_configuration_error"
      upstream_aios_failure: "n/a"
      side_effect_failure: "raise_typed_exception"

    invariants:
      - "All tool dispatches must pass schema validation first"
      - "All side-effect tools must pass governance evaluation"
      - "Every dispatch writes request, decision, and result packets"
      - "Denied tools never execute side effects"
      - "No domain adapters or business logic inside core/tools/*"

  acceptance:
    required:
      - "Tools are registered once and callable from any agent"
      - "Arguments are validated against declared schemas"
      - "Governance is deny-by-default for side-effect tools"
      - "All tool calls are persisted as deterministic envelopes"
      - "Registry supports discovery via stable names and tags"

  tests:
    scope:
      - "register(): rejects duplicate tool names"
      - "validate(): rejects missing or invalid arguments"
      - "dispatch(): invokes governance for side-effect tools"
      - "dispatch(): persists request/decision/result envelopes"
      - "idempotency: duplicate dispatch returns cached result"
      - "deny path: denied tool never executes, audit packet exists"

  observability:
    required_logs:
      - "tools.registered"
      - "tools.dispatch.started"
      - "tools.dispatch.decision"
      - "tools.dispatch.completed"
      - "tools.dispatch.failed"
    metrics:
      - "tools.dispatch.latency_ms"
      - "tools.dispatch.error_rate"
      - "tools.registry.size"
