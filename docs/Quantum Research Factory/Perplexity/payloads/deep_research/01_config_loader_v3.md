# SONAR DEEP RESEARCH — config_loader (v3 - Perplexity Compliant)

## API Payload

```json
{
  "model": "sonar-deep-research",
  "messages": [
    {"role": "system", "content": "You are a YAML specification generator. Output ONLY valid YAML code blocks. No explanations, no markdown prose, no commentary. If you cannot find information, state that clearly in a YAML comment."},
    {"role": "user", "content": "SEE_PROMPT_BELOW"}
  ],
  "temperature": 0.1,
  "max_tokens": 12000
}
```

---

## PROMPT

---

Generate a production-ready L9 Module-Spec-v2.5 YAML for a Python configuration loader module.

# MODULE IDENTITY

- module_id: config_loader
- name: Configuration Loader  
- tier: 0 (loads first, no dependencies)
- purpose: Environment variable and YAML configuration management using Pydantic Settings v2

# RESEARCH THESE TOPICS TO FILL THE SPEC

1. Pydantic Settings v2 BaseSettings patterns for environment variable binding
2. Python-dotenv .env file loading with SettingsConfigDict
3. Fail-fast validation patterns that crash on missing required env vars
4. FastAPI dependency injection for configuration singletons
5. 12-Factor App environment variable best practices

# YAML SPEC SECTIONS TO GENERATE (ALL 26 REQUIRED)

Generate a complete YAML with these sections:
- metadata (module_id, name, tier, description, system, language, runtime)
- ownership (team, primary_contact)
- runtime_wiring (service, startup_phase, depends_on, blocks_startup_on_failure)
- runtime_contract (runtime_class, execution_model)
- external_surface (exposes_http_endpoint, exposes_webhook, exposes_tool, callable_from)
- dependency_contract (inbound, outbound)
- dependencies (allowed_tiers, outbound_calls)
- packet_contract (emits, requires_metadata) - empty for Tier 0
- packet_expectations (on_success, on_error, durability)
- idempotency (pattern, source, durability)
- error_policy (default, retries, escalation, validation_error, missing_env_var)
- observability (logs, metrics, traces)
- runtime_touchpoints (touches_db, touches_tools, touches_external_network, affects_boot)
- tier_expectations (requires_runtime_wiring, requires_packet_contract, requires_negative_tests)
- test_scope (unit, integration, docker_smoke)
- acceptance (positive tests, negative tests)
- global_invariants_ack
- spec_confidence (level, basis)
- repo (root_path, allowed_new_files, allowed_modified_files)
- interfaces (inbound, outbound) - empty for Tier 0
- environment (required vars, optional vars)
- orchestration (validation, context_reads, aios_calls, side_effects)
- boot_impact (level, reason)
- standards (identity, logging, http_client)
- goals, non_goals
- notes_for_perplexity

# CONSTRAINTS

- Tier 0 module: depends_on must be empty, no packet emission
- blocks_startup_on_failure: true (missing config = crash)
- logging library: structlog (FORBIDDEN: print, logging module)
- http_client: httpx (FORBIDDEN: requests, aiohttp)
- root_path: /Users/ib-mac/Projects/L9

# OUTPUT

Output ONLY the complete YAML specification. Start with ```yaml and end with ```. No other text.

---

# END OF PAYLOAD



