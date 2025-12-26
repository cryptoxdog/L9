# SONAR DEEP RESEARCH — config_loader (FINAL)

## API Payload

```json
{
  "model": "sonar-deep-research",
  "messages": [
    {
      "role": "system", 
      "content": "You are a YAML specification generator for the L9 enterprise system. Output ONLY a valid YAML code block. No explanations, no commentary, no markdown prose. Start with ```yaml and end with ```. If you cannot find information for a field, use a sensible default with a comment."
    },
    {
      "role": "user",
      "content": "SEE_PROMPT_BELOW"
    }
  ],
  "temperature": 0.1,
  "max_tokens": 12000
}
```

---

## PROMPT

Research and generate a complete L9 Module-Spec-v2.5 YAML for a Python configuration loader module.

## MODULE IDENTITY

- module_id: config_loader
- name: Configuration Loader  
- tier: 0 (Core infrastructure - loads first, no L9 dependencies)
- description: Environment variable and YAML configuration management using Pydantic Settings v2

## RESEARCH THESE TOPICS

1. Pydantic Settings v2 — BaseSettings, SettingsConfigDict, env_prefix, nested models, Field validators
2. Python-dotenv — .env file loading, precedence with environment variables
3. PyYAML — safe_load patterns, schema validation
4. 12-Factor App — environment variable best practices
5. FastAPI dependency injection — lifespan hooks, app.state patterns
6. Fail-fast boot validation — exit(1) on missing required config

## OUTPUT: COMPLETE YAML SPEC

Generate a Module-Spec-v2.5 YAML with ALL these sections (26 total):

```yaml
schema_version: "2.5"

# SECTION 1: METADATA
metadata:
  module_id: "config_loader"
  name: "Configuration Loader"
  tier: "0"
  description: "<fill from research>"
  system: "L9"
  language: "python"
  runtime: "python>=3.11"

# SECTION 2: OWNERSHIP
ownership:
  team: "core"
  primary_contact: "platform_engineer"

# SECTION 3: RUNTIME WIRING
runtime_wiring:
  service: "api"
  startup_phase: "early"
  depends_on: []  # Tier 0 - no dependencies
  blocks_startup_on_failure: true

# SECTION 4: RUNTIME CONTRACT
runtime_contract:
  runtime_class: "control_plane"
  execution_model: "request_driven"

# SECTION 5: EXTERNAL SURFACE
external_surface:
  exposes_http_endpoint: false
  exposes_webhook: false
  exposes_tool: false
  callable_from: ["internal"]

# SECTION 6: DEPENDENCY CONTRACT
dependency_contract:
  inbound:
    - from_module: "all_l9_modules"
      interface: "python_import"
      endpoint: "config.settings.get_settings()"
  outbound: []

# SECTION 7: DEPENDENCIES
dependencies:
  allowed_tiers: []
  outbound_calls: []

# SECTION 8: PACKET CONTRACT
packet_contract:
  emits: []  # Tier 0 infrastructure - no packets
  requires_metadata: []

# SECTION 9: PACKET EXPECTATIONS
packet_expectations:
  on_success:
    emits: []
  on_error:
    emits: []
  durability:
    success: "not_applicable"
    error: "not_applicable"

# SECTION 10: IDEMPOTENCY
idempotency:
  pattern: "none"
  source: "not_applicable"
  durability: "not_applicable"

# SECTION 11: ERROR POLICY
error_policy:
  default: "fail_fast"
  retries:
    enabled: false
    max_attempts: 0
  escalation:
    emit_error_packet: false
    mark_task_failed: false
    alert: "log"
  validation_error:
    status: null  # No HTTP - crashes process
    action: "sys.exit(1)"
    log: "config_validation_failed"
  missing_env_var:
    status: null
    action: "sys.exit(1)"
    log: "required_env_var_missing"

# SECTION 12: OBSERVABILITY
observability:
  logs:
    enabled: true
    level: "info"
  metrics:
    enabled: true
    counters:
      - "config_load_total"
      - "config_validation_errors_total"
    histograms:
      - "config_load_duration_seconds"
  traces:
    enabled: false

# SECTION 13: RUNTIME TOUCHPOINTS
runtime_touchpoints:
  touches_db: false
  touches_tools: false
  touches_external_network: false
  affects_boot: true

# SECTION 14: TIER EXPECTATIONS
tier_expectations:
  requires_runtime_wiring: true
  requires_packet_contract: false
  requires_negative_tests: true

# SECTION 15: TEST SCOPE
test_scope:
  unit: true
  integration: false
  docker_smoke: true

# SECTION 16: ACCEPTANCE
acceptance:
  positive:
    - id: "AP-1"
      description: "<fill: valid env loads>"
      test: "test_valid_env_loads"
    - id: "AP-2"
      description: "<fill: YAML merges with env>"
      test: "test_yaml_config_merges"
    - id: "AP-3"
      description: "<fill: Pydantic validation passes>"
      test: "test_pydantic_validation_passes"
    - id: "AP-4"
      description: "<fill: get_settings singleton>"
      test: "test_settings_singleton"
  negative:
    - id: "AN-1"
      description: "<fill: missing required env crashes>"
      expected_behavior: "exit(1) with error message"
      test: "test_missing_required_env_crashes"
    - id: "AN-2"
      description: "<fill: invalid type crashes>"
      expected_behavior: "ValidationError with field"
      test: "test_invalid_type_crashes"

# SECTION 17: GLOBAL INVARIANTS ACK
global_invariants_ack:
  emits_packet_on_ingress: false
  tool_calls_traceable: false
  unknown_tool_id_hard_fail: false
  malformed_packet_blocked: false
  missing_env_fails_boot: true

# SECTION 18: SPEC CONFIDENCE
spec_confidence:
  level: "high"
  basis:
    - "Pydantic Settings v2 well-documented"
    - "12-Factor App is industry standard"

# SECTION 19: FILE MANIFEST
repo:
  root_path: "/Users/ib-mac/Projects/L9"
  allowed_new_files:
    - "config/__init__.py"
    - "config/settings.py"
    - "config/loader.py"
    - "tests/test_config_loader.py"
  allowed_modified_files:
    - "api/server.py"

# SECTION 20: INTERFACES
interfaces:
  inbound: []
  outbound: []

# SECTION 21: ENVIRONMENT VARIABLES
environment:
  required:
    - name: "DATABASE_URL"
      description: "<fill from research>"
    - name: "REDIS_URL"
      description: "<fill from research>"
  optional:
    - name: "LOG_LEVEL"
      description: "<fill from research>"
      default: "INFO"
    - name: "LOG_FORMAT"
      description: "<fill from research>"
      default: "json"

# SECTION 22: ORCHESTRATION
orchestration:
  validation:
    - "<fill: load .env steps>"
    - "<fill: parse env vars>"
    - "<fill: validate required fields>"
  context_reads: []
  aios_calls: []
  side_effects:
    - action: "Log config loaded"
      service: "structlog"
      packet_type: null

# SECTION 23: BOOT IMPACT
boot_impact:
  level: "hard"
  reason: "Missing/invalid config prevents system startup"

# SECTION 24: STANDARDS
standards:
  identity:
    canonical_identifier: "module_id"
  logging:
    library: "structlog"
    forbidden: ["logging", "print"]
  http_client:
    library: "httpx"
    forbidden: ["aiohttp", "requests"]

# SECTION 25: GOALS & NON-GOALS
goals:
  - "<fill: typed config access>"
  - "<fill: fail fast on missing>"
  - "<fill: .env support>"
  - "<fill: YAML nested config>"

non_goals:
  - "<fill: hot reload>"
  - "No new database tables"
  - "No new migrations"
  - "No parallel config systems"

# SECTION 26: NOTES FOR PERPLEXITY
notes_for_perplexity:
  - "Use Pydantic Settings v2 BaseSettings with SettingsConfigDict"
  - "Use @lru_cache for settings singleton"
  - "Load .env via SettingsConfigDict(env_file='.env')"
  - "Exit immediately on ValidationError during import"
  - "All fields typed - no Dict[str, Any]"
```

## CONSTRAINTS

1. Tier 0: depends_on MUST be empty (no L9 dependencies)
2. blocks_startup_on_failure: true (missing config = crash)
3. No packets (infrastructure module)
4. Logging: structlog only (FORBIDDEN: print, logging)
5. Fill ALL <fill:> placeholders with real values from research

## OUTPUT

Generate ONLY the completed YAML specification. No explanations.

---

# END OF PAYLOAD



