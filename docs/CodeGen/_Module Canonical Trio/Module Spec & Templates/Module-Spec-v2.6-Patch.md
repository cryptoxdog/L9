# ============================================================================
# L9 UNIVERSAL MODULE SPEC — v2.6.0
# ============================================================================
# v2.6 CHANGE TYPE: ADDITIVE ONLY
# v2.5 remains fully valid and loadable
#
# v2.6 PURPOSE:
#   - Enable deep, production-grade code generation (60–80%)
#   - Enable spec-level DORA observability
#   - Add governance-only maturity and escalation signals
#   - ZERO runtime behavior change
#
# v2.6 ADDS:
#   - codegen_hints
#   - delivery_metrics (DORA)
#   - maturity
#   - escalation_policy
# ============================================================================

schema_version: "2.6"

# ============================================================================
# SECTION 27: CODEGEN HINTS (NEW — v2.6)
# ============================================================================
# Generator-only. NO runtime semantics.
# Guides depth, completeness, and safety of generated code.
# ============================================================================
codegen_hints:
  completeness_target: 0.8        # 0.0–1.0 (recommended: 0.6–0.8)
  allow_real_logic: true           # Generate real control flow, not comments
  allow_real_tests: true           # Generate passing tests, not placeholders
  stub_strategy: "production_scaffold"
  forbid_guessing: true            # Generator must fail if spec insufficient
  refuse_if_missing:
    - runtime_wiring
    - dependency_contract
    - packet_contract
    - acceptance

# ============================================================================
# SECTION 28: DELIVERY METRICS / DORA (NEW — v2.6)
# ============================================================================
# Observability only. Owned by CI.
# Humans MUST NOT edit timestamps or commit references.
# ============================================================================
delivery_metrics:
  track:
    - lead_time
    - change_frequency
    - change_failure_rate
    - recovery_time

  measurement_points:
    spec_created: meta.created_at
    spec_updated: meta.last_updated_at
    code_generated: ci.codegen_timestamp
    merged_to_main: ci.merge_timestamp
    deployed: runtime.deploy_timestamp

  ownership:
    primary: "{{ownership.team}}"
    escalation: "{{ownership.primary_contact}}"

  enforcement:
    human_editing_forbidden: true
    ci_owned: true

# ============================================================================
# SECTION 29: MODULE MATURITY (NEW — v2.6)
# ============================================================================
# Governance signal only. No behavioral impact.
# ============================================================================
maturity:
  stage: "{{experimental | beta | stable | legacy}}"
  production_ready: "{{true | false}}"
  notes:
    - "{{Optional context for L / CI}}"

# ============================================================================
# SECTION 30: ESCALATION POLICY (NEW — v2.6)
# ============================================================================
# Defines when failures trigger human attention.
# No automatic execution changes.
# ============================================================================
escalation_policy:
  on_repeated_failure:
    threshold: 3
    window: "24h"
    escalate_to: "{{ownership.primary_contact}}"

  on_boot_block:
    escalate_to: "{{ownership.primary_contact}}"

# ============================================================================
# VERSION COMPATIBILITY
# ============================================================================
# v2.1–v2.5 specs remain valid and loadable
# v2.6 fields are REQUIRED only when schema_version >= 2.6
# Code generators may soft-ignore v2.6 if unsupported
# ============================================================================

# ============================================================================
# BEHAVIORAL CHANGE CONFIRMATION
# ============================================================================
# v2.6 introduces:
#   - NO runtime behavior change
#   - NO execution semantics
#   - NO new dependencies
#   - NO agent logic
#
# v2.6 strictly improves:
#   - Code generation depth
#   - CI observability
#   - Governance clarity
#
# Diff remains boring. This is intentional.
# ============================================================================
