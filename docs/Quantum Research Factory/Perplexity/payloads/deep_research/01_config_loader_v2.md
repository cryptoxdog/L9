# SONAR DEEP RESEARCH — config_loader (HARDENED v2)

## API Payload

```json
{
  "model": "sonar-deep-research",
  "messages": [{"role": "user", "content": "SEE_PROMPT_BELOW"}],
  "temperature": 0.1,
  "max_tokens": 12000
}
```

---

## PROMPT

---

# ROLE

You are P-Prompt, the L9 specification engine. Your ONLY job is to output a complete Module-Spec-v2.5 YAML file. NO commentary. NO explanations. NO markdown outside the YAML block.

# OUTPUT FORMAT (BINDING)

```
Output MUST be:
1. A single YAML code block
2. Starting with: ```yaml
3. Ending with: ```
4. Containing ALL 26 sections from Module-Spec-v2.5
5. ZERO text outside the code block
```

# MODULE BLOCK (INSERT INTO SPEC)

```yaml
module_id: config_loader
name: Configuration Loader
tier: 0
description: Environment and YAML configuration management with Pydantic Settings v2. Provides typed access to all L9 configuration. Fails fast on missing required environment variables at boot time.
scope: Core infrastructure - loads before everything else. No L9 dependencies allowed.
```

# L9 SYSTEM CONTEXT

```yaml
system: L9
core_protocol: PacketEnvelope
memory: PostgreSQL + pgvector  
cache: Redis
logging: structlog (FORBIDDEN: print, logging module)
http_client: httpx (FORBIDDEN: requests, aiohttp)
startup_tiers: 0-7 (lower = earlier)
root_path: /Users/ib-mac/Projects/L9
python_version: ">=3.11"
```

# RESEARCH REQUIREMENTS (USE TO FILL SPEC VALUES)

Research these topics to populate spec fields with REAL production values:

1. **Pydantic Settings v2** — BaseSettings, SettingsConfigDict, env_prefix, nested models, validators
2. **Python-dotenv** — load_dotenv(), .env precedence, env_file in SettingsConfigDict
3. **YAML config loading** — PyYAML safe_load, schema validation patterns
4. **12-Factor App** — environment variable best practices, secret handling
5. **FastAPI lifespan** — startup hooks, dependency injection via app.state
6. **Fail-fast boot** — ValidationError catching, exit(1) on missing required vars

# TIER 0 CONSTRAINTS (BINDING)

```yaml
tier_0_rules:
  - depends_on: []  # MUST be empty - Tier 0 has no L9 dependencies
  - blocks_startup_on_failure: true  # Missing config = hard crash
  - emits_packets: false  # Infrastructure modules don't emit packets
  - startup_phase: early  # Loads first
  - external_surface: none  # No HTTP endpoints, no webhooks
```

# MODULE-SPEC-v2.5 TEMPLATE (FILL ALL SECTIONS)

```yaml
# ============================================================================
# L9 MODULE SPEC — config_loader v2.5.0
# ============================================================================
schema_version: "2.5"

# SECTION 1: METADATA (REQUIRED)
metadata:
  module_id: "config_loader"
  name: "Configuration Loader"
  tier: "0"
  description: "{{FILL: one-line description}}"
  system: "L9"
  language: "python"
  runtime: "python>=3.11"

# SECTION 2: OWNERSHIP (REQUIRED)
ownership:
  team: "core"
  primary_contact: "platform_engineer"

# SECTION 3: RUNTIME WIRING (REQUIRED)
runtime_wiring:
  service: "api"
  startup_phase: "early"
  depends_on: []  # Tier 0 - no dependencies
  blocks_startup_on_failure: true

# SECTION 4: RUNTIME CONTRACT (REQUIRED)
runtime_contract:
  runtime_class: "control_plane"
  execution_model: "request_driven"

# SECTION 5: EXTERNAL SURFACE (REQUIRED)
external_surface:
  exposes_http_endpoint: false
  exposes_webhook: false
  exposes_tool: false
  callable_from: ["internal"]

# SECTION 6: DEPENDENCY CONTRACT (REQUIRED)
dependency_contract:
  inbound:
    - from_module: "all_modules"
      interface: "python_import"
      endpoint: "config.settings.get_settings()"
  outbound: []  # Tier 0 calls nothing

# SECTION 7: DEPENDENCIES (REQUIRED)
dependencies:
  allowed_tiers: []  # Tier 0 - no tier dependencies
  outbound_calls: []  # No outbound calls

# SECTION 8: PACKET CONTRACT (REQUIRED)
packet_contract:
  emits: []  # Infrastructure module - no packets
  requires_metadata: []

# SECTION 9: PACKET EXPECTATIONS (REQUIRED)
packet_expectations:
  on_success:
    emits: []
  on_error:
    emits: []
  durability:
    success: "best_effort"
    error: "best_effort"

# SECTION 10: IDEMPOTENCY (REQUIRED)
idempotency:
  pattern: "none"
  source: "not_applicable"
  durability: "not_applicable"

# SECTION 11: ERROR POLICY (REQUIRED)
error_policy:
  default: "fail_fast"
  retries:
    enabled: false
    max_attempts: 0
  escalation:
    emit_error_packet: false
    mark_task_failed: false
    alert: "log"
  # Tier 0 specific: validation errors crash boot
  validation_error:
    action: "exit(1)"
    log: "config_validation_failed"
  missing_env_var:
    action: "exit(1)"  
    log: "required_env_var_missing"

# SECTION 12: OBSERVABILITY (REQUIRED)
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

# SECTION 13: RUNTIME TOUCHPOINTS (REQUIRED)
runtime_touchpoints:
  touches_db: false
  touches_tools: false
  touches_external_network: false
  affects_boot: true

# SECTION 14: TIER EXPECTATIONS (REQUIRED)
tier_expectations:
  requires_runtime_wiring: true
  requires_packet_contract: false  # Tier 0 infra
  requires_negative_tests: true

# SECTION 15: TEST SCOPE (REQUIRED)
test_scope:
  unit: true
  integration: false
  docker_smoke: true

# SECTION 16: ACCEPTANCE (REQUIRED)
acceptance:
  positive:
    - id: "AP-1"
      description: "{{FILL: Valid .env loads successfully}}"
      test: "test_valid_env_loads"
    - id: "AP-2"  
      description: "{{FILL: YAML config merges with env}}"
      test: "test_yaml_config_merges"
    - id: "AP-3"
      description: "{{FILL: Pydantic validation passes for valid config}}"
      test: "test_pydantic_validation_passes"
    - id: "AP-4"
      description: "{{FILL: get_settings() returns singleton}}"
      test: "test_settings_singleton"
  negative:
    - id: "AN-1"
      description: "{{FILL: Missing required env var crashes boot}}"
      expected_behavior: "exit(1) with clear error message"
      test: "test_missing_required_env_crashes"
    - id: "AN-2"
      description: "{{FILL: Invalid type in env var crashes boot}}"
      expected_behavior: "ValidationError with field name"
      test: "test_invalid_type_crashes"

# SECTION 17: GLOBAL INVARIANTS ACKNOWLEDGEMENT (REQUIRED)
global_invariants_ack:
  emits_packet_on_ingress: false  # Tier 0 infra exception
  tool_calls_traceable: false  # No tool calls
  unknown_tool_id_hard_fail: false  # No tools
  malformed_packet_blocked: false  # No packets
  missing_env_fails_boot: true  # CRITICAL for config_loader

# SECTION 18: SPEC CONFIDENCE (REQUIRED)
spec_confidence:
  level: "high"
  basis:
    - "Pydantic Settings v2 patterns well-documented"
    - "12-Factor App is industry standard"

# SECTION 19: FILE MANIFEST (REQUIRED)
repo:
  root_path: "/Users/ib-mac/Projects/L9"
  allowed_new_files:
    - "config/__init__.py"
    - "config/settings.py"
    - "config/loader.py"
    - "tests/test_config_loader.py"
  allowed_modified_files:
    - "api/server.py"

# SECTION 20: INTERFACES (REQUIRED)
interfaces:
  inbound: []  # No HTTP interfaces
  outbound: []  # No outbound calls

# SECTION 21: ENVIRONMENT VARIABLES (REQUIRED)
environment:
  required:
    - name: "DATABASE_URL"
      description: "PostgreSQL connection string"
    - name: "REDIS_URL"
      description: "Redis connection string"
    # {{FILL: Add more required vars from research}}
  optional:
    - name: "LOG_LEVEL"
      description: "Logging level"
      default: "INFO"
    - name: "LOG_FORMAT"
      description: "json or console"
      default: "json"
    # {{FILL: Add more optional vars}}

# SECTION 22: ORCHESTRATION FLOW (REQUIRED)
orchestration:
  validation:
    - "Load .env file if present (python-dotenv)"
    - "Parse environment variables into Pydantic model"
    - "Validate all required fields present"
    - "Validate types and constraints"
  context_reads: []  # No context reads
  aios_calls: []  # No AIOS calls
  side_effects:
    - action: "Log config loaded"
      service: "structlog"
      packet_type: null

# SECTION 23: BOOT IMPACT (REQUIRED)
boot_impact:
  level: "hard"
  reason: "Missing or invalid configuration prevents system startup"

# SECTION 24: MANDATORY STANDARDS (REQUIRED)
standards:
  identity:
    canonical_identifier: "module_id"
  logging:
    library: "structlog"
    forbidden: ["logging", "print"]
  http_client:
    library: "httpx"
    forbidden: ["aiohttp", "requests"]

# SECTION 25: GOALS & NON-GOALS (REQUIRED)
goals:
  - "Provide typed, validated configuration access"
  - "Fail fast on missing required environment variables"
  - "Support .env files for local development"
  - "Support YAML config for complex nested settings"

non_goals:
  - "Hot-reload configuration at runtime"
  - "No new database tables"
  - "No new migrations"
  - "No parallel memory/logging/config systems"

# SECTION 26: NOTES FOR PERPLEXITY (REQUIRED)
notes_for_perplexity:
  - "Use Pydantic Settings v2 BaseSettings with SettingsConfigDict"
  - "Use @lru_cache for settings singleton pattern"
  - "Load .env via SettingsConfigDict(env_file='.env')"
  - "All fields must be typed - no Dict[str, Any]"
  - "Exit immediately on ValidationError during import"
```

# INSTRUCTIONS

1. Research the topics listed in RESEARCH REQUIREMENTS
2. Fill ALL {{FILL: ...}} placeholders with REAL values from your research
3. Add any additional environment variables, acceptance tests, or config fields discovered
4. Output ONLY the completed YAML - no explanations, no commentary
5. The YAML must be valid and parseable

# BEGIN OUTPUT

Output the complete Module-Spec-v2.5 YAML now:

---

# END OF PAYLOAD



