# ============================================================
# L9 DOMAIN AGENT SPEC v1.0
# What: Deterministic spec for generating a new domain agent module in the L9 repo
# Does: Forces correct file placement, interfaces, wiring points, tests, docs, and runtime gates
# Use: Upload with L9_REPO_BINDING.yaml + PERPLEXITY_GEN_CONTRACT.yaml + your GEN_TEMPLATE.yaml
# ============================================================

l9_domain_agent_spec_v1:
  module_kind: domain_agent
  agent_name: "DOMAIN_AGENT_NAME"          # REQUIRED: snake_case, e.g. plastics_intake
  agent_class: "DomainAgent"              # REQUIRED: PascalCase, e.g. PlasticsIntakeAgent
  domain: "DOMAIN"                        # REQUIRED: e.g. plastics, legaltech, devops
  purpose: "ONE_SENTENCE_PURPOSE"         # REQUIRED: concise

  repo_binding:
    enforce: true
    sources:
      - tree.txt
      - api_surfaces.txt
      - imports.txt
      - function_signatures.txt
      - env_refs.txt
      - dependencies.txt
      - config_files.txt

  placement:
    rule: "MUST_MATCH_EXISTING_TREE"
    new_package_name: "l9/agents/DOMAIN_AGENT_NAME/"
    required_files:
      - "__init__.py"
      - "agent.py"            # agent class + core logic
      - "router.py"           # FastAPI router (optional if api_exposed=false)
      - "schemas.py"          # Pydantic IO models
      - "tools.py"            # tool wrappers / tool registry (if tools_enabled=true)
      - "memory_bridge.py"    # if uses_memory=true
      - "world_bridge.py"     # if uses_world_model=true
      - "policies.py"         # guardrails + escalation rules
      - "logger.py"           # structured logger config (or reuse shared logger if exists)
      - "health.py"           # health checks + readiness
      - "README.md"
      - "tests/test_agent.py"
      - "tests/test_router.py"
      - "tests/conftest.py"
    forbidden:
      - "new_top_level_dirs"
      - "l9/l9/"
      - "duplicate_entrypoints"

  interfaces:
    callable_surface:
      methods:
        - name: "run"
          signature: "async def run(self, task: DomainTask, ctx: DomainContext) -> DomainResult"
          required: true
        - name: "pre_process"
          signature: "async def pre_process(self, task: DomainTask, ctx: DomainContext) -> DomainTask"
          required: true
        - name: "post_process"
          signature: "async def post_process(self, result: DomainResult, ctx: DomainContext) -> DomainResult"
          required: true
    api_surface:
      api_exposed: true
      base_path: "/agents/DOMAIN_AGENT_NAME"
      endpoints:
        - method: POST
          path: "/run"
          request_model: "RunRequest"
          response_model: "RunResponse"
        - method: GET
          path: "/health"
          request_model: null
          response_model: "HealthResponse"

  data_contracts:
    pydantic_models:
      - DomainTask
      - DomainContext
      - DomainResult
      - RunRequest
      - RunResponse
      - HealthResponse
    status_codes:
      enum:
        - OK
        - RETRYABLE_ERROR
        - FATAL_ERROR
        - NEEDS_REVIEW
    error_handling:
      rule: "typed_exceptions + status_mapping"
      exceptions:
        - DomainAgentError
        - ValidationError
        - ExternalServiceError
        - PolicyViolationError

  capabilities:
    tools_enabled: true
    uses_memory: true
    uses_world_model: false
    uses_email: false
    uses_web: false
    uses_filesystem: true
    async_io: true

  integrations:
    logging:
      format: json
      include_fields: ["agent", "request_id", "trace_id", "task_id", "domain", "status"]
    config:
      env_only: true
      must_use_existing_env_refs: true
    dependencies:
      prefer_existing: true
      add_new_only_if_required: true

  governance:
    escalation:
      triggers:
        - "policy_violation"
        - "ambiguous_context"
        - "destructive_action_request"
        - "unknown_target_path"
      behavior: "return NEEDS_REVIEW with explanation"
    safety:
      forbid:
        - "hardcoded_secrets"
        - "unsafe_shell_exec"
        - "sql_string_concat"
      require:
        - "parameterized_queries_if_db_used"
        - "input_validation"
        - "rate_limit_if_external_calls"

  runtime:
    health_checks:
      required: true
      includes:
        - "module_import_ok"
        - "config_loaded"
        - "optional_dependency_probe"
    graceful_shutdown: true
    metrics:
      required: true
      track: ["latency_ms", "error_rate", "tasks_completed"]

  wiring:
    rule: "REGISTER_IN_REAL_ENTRYPOINT"
    must_emit:
      - "exact file+symbol where router is registered"
      - "exact import lines added"
      - "manifest.json with integration_points"

  tests:
    required:
      - "test_run_success_path"
      - "test_validation_rejects_bad_input"
      - "test_policy_escalation_returns_needs_review"
      - "test_router_run_endpoint"
      - "test_health_endpoint"
    db_optional:
      if_used: ["integration_test_with_test_container_or_mock_strategy"]
    commands_must_work:
      - "pytest -q"

  docs:
    readme:
      must_include:
        - "what this agent does"
        - "where it lives in repo"
        - "how to call run() (code example)"
        - "API usage examples (curl)"
        - "env vars used (exact names)"
        - "how to run tests"
        - "how to wire/register (where to look)"
        - "troubleshooting"

  output_requirements:
    must_return:
      - file_tree
      - all_file_contents
      - manifest.json
      - runbook.md
    forbid:
      - "guessing entrypoints"
      - "inventing env vars"
      - "inventing packages not in tree"

  placeholders_to_fill:
    - agent_name
    - agent_class
    - domain
    - purpose

  example_fill:
    agent_name: "plastics_intake"
    agent_class: "PlasticsIntakeAgent"
    domain: "plastics"
    purpose: "Extract and normalize inbound plastics leads into canonical intake records."
