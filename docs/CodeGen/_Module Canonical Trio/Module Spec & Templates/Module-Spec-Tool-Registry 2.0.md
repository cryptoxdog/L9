module:
  id: "tool.registry"
  name: "Tool Registry + Dispatcher"
  system: "L9"
  owner: "core-os"
  language: "python"
  runtime: "python>=3.11"
  version: "1.0.0"

purpose: >
  Provide a single OS-level tool system for L9 that enables deterministic
  tool discovery, schema validation, governance enforcement, execution
  dispatch, and full auditability for all agents and integrations.

goals:
  - "One canonical tool interface shared by all agents"
  - "Deterministic, auditable tool selection and execution"
  - "Schema-first validation for every tool invocation"
  - "Governance-first execution for any side-effect"
  - "Replayable, persistent execution traces"

non_goals:
  - "Implement domain tools (Slack, Email, Mac, Web)"
  - "Contain agent reasoning or planning logic"
  - "Execute side effects without governance approval"
  - "Introduce new persistence layers outside substrate"

repo:
  root_path: "l9/"
  allowed_new_files:
    - "core/tools/schemas.py"
    - "core/tools/registry.py"
    - "core/tools/selector.py"
    - "core/tools/dispatcher.py"
    - "tests/test_tool_dispatch.py"
    - "tests/test_tool_selector.py"
    - "docs/tools.md"
    - "docs/tool_selection_contract.md"
    - "contracts/tools/TOOL_SELECTION_CONTRACT.yaml"
  allowed_modified_files: []
  must_import_and_use:
    - "memory.substrate_service"
    - "memory.packet_envelope"
    - "governance.policy_engine"
  must_not_create:
    - "parallel tool registry"
    - "parallel schema validation stack"
    - "parallel tool selector modules"
    - "direct side effects bypassing governance"

interfaces:
  inbound:
    - name: "tools.register"
      signature: "(tool_def: ToolDef) -> None"
    - name: "tools.list"
      signature: "(*, tags=None, side_effects=None) -> list[ToolDef]"
    - name: "tools.get"
      signature: "(tool_name: str) -> ToolDef | None"
    - name: "tools.validate"
      signature: "(tool_name: str, args: dict) -> ValidationResult"
    - name: "tools.select"
      signature: "(intent: dict, context: ToolContext, candidates=None) -> ToolSelection"
    - name: "tools.dispatch"
      signature: "(tool_name: str, args: dict, context: ToolContext) -> ToolResult"

orchestration:
  context_reads:
    - "thread_id / thread_uuid"
    - "principal_id"
    - "role (optional)"
    - "approval_token (optional)"
  aios_calls: []
  persistence_writes:
    - "packet_store: tool.select.request"
    - "packet_store: tool.select.result"
    - "packet_store: tool.call.request"
    - "packet_store: tool.call.decision"
    - "packet_store: tool.call.result"
    - "packet_store: tool.call.failed"
    - "tasks: tool.call.pending_approval (optional)"

idempotency:
  enabled: true
  primary_key: "thread_id + tool_name + normalized_args_hash"
  fallback_key: "request_uuid"
  on_duplicate: "return_cached_result"

error_policy:
  invalid_auth_or_signature: "raise_configuration_error"
  upstream_aios_failure: "n/a"
  side_effect_failure: "raise_typed_exception"

schema_truth:
  tables:
    - "packet_store"
    - "tasks"
    - "knowledge_facts"
  notes: >
    Tool selection, governance decisions, and execution outcomes are
    persisted as immutable packet envelopes. Deferred executions may
    create tasks while still emitting decision packets.

data_contracts:
  tool_def:
    required_fields:
      - "name (domain.action)"
      - "description"
      - "tags"
      - "args_schema"
      - "side_effects"
      - "risk"
  tool_selection:
    required_fields:
      - "intent_summary"
      - "candidate_tools"
      - "selected_tool"
      - "args"
      - "why_selected"
      - "expected_side_effects"
      - "rollback_plan"
      - "confidence"
    invariants:
      - "selected_tool must exist in registry"
      - "selected_tool must be in candidate_tools"
      - "args must validate against selected tool schema"

acceptance:
  required:
    - "Tools are registered once and discoverable via tags"
    - "Selector emits a persisted ToolSelection record"
    - "Selector never selects unregistered tools"
    - "Dispatch validates args before governance"
    - "Side-effect tools are deny-by-default"
    - "Every dispatch persists request + decision + result packets"
    - "Idempotent calls return cached results"

observability:
  required_logs:
    - "tools.registered"
    - "tools.select.started"
    - "tools.select.completed"
    - "tools.dispatch.started"
    - "tools.dispatch.decision"
    - "tools.dispatch.completed"
    - "tools.dispatch.failed"
  metrics:
    - "tools.select.latency_ms"
    - "tools.dispatch.latency_ms"
    - "tools.dispatch.error_rate"
    - "tools.registry.size"

notes_for_perplexity:
  generation_rules:
    - "Do not invent tools or schemas"
    - "Selector must not use LLM reasoning"
    - "All side effects require governance allow"
    - "Emit packets for selection and dispatch"
