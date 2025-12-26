# Cursor Prompts Extracted from Module-Spec-Chat.md
> **Source:** Module-Spec-Chat.md (lines 2720+)  
> **Extracted:** 2025-12-16

---

## C-PROMPT 1: REVISION OF Module-Spec.yaml (v2.1 → v2.2)

```
🔧 C-GMP — REVISION OF Module-Spec.yaml
Goal: Encode deterministic behavior directly into the schema so agents cannot improvise

OBJECTIVE
Revise the canonical Module Spec YAML so that:

- deterministic behavior is schema-enforced, not prompt-enforced
- ambiguity is structurally impossible
- cross-module discipline, runtime invariants, and negative cases are mandatory
- downstream generators (P, C, tests) are forced to comply by validation

This is a schema evolution, not a content rewrite.

VERSIONING
Create: Module-Spec-v2.2.yaml

- Do not delete v2.1
- Add schema_version field with semantic meaning

REQUIRED SCHEMA ADDITIONS (NON-NEGOTIABLE)

1️⃣ Global invariants acknowledgement (module-level binding)
Add a required section:

global_invariants_ack:
  emits_packet_on_ingress: true
  tool_calls_traceable: true
  unknown_tool_id_hard_fail: true
  malformed_packet_blocked: true
  missing_env_fails_boot: true

Rules:
- All values must be explicitly true
- Any deviation → invalid spec
- This binds the module to system law

2️⃣ Runtime touchpoints (lock deployment behavior)
Add a required section:

runtime_touchpoints:
  touches_db: true|false
  touches_tools: true|false
  touches_external_network: true|false
  affects_boot: true|false

Rules:
- No defaults
- Required for every module
- Used later by smoke tests and deployment planning

3️⃣ Negative acceptance cases (mandatory)
Extend acceptance:

acceptance:
  positive:
    - id: AP-1
      description: "..."
  negative:
    - id: AN-1
      description: "Unknown tool_id causes hard failure"
      expected_behavior: "Request rejected before execution"

Rules:
- At least one negative case required
- Must reference either:
  - auth failure
  - idempotency
  - malformed input
  - unknown tool_id
- Generator must fail if missing

4️⃣ Explicit idempotency declaration (no inference)
Tighten idempotency:

idempotency:
  pattern: event_id | composite_key | substrate_lookup
  source: slack_event_id | webhook_header | computed_hash
  durability: in_memory | substrate

Rules:
- pattern must map to SSOT
- durability must be explicit
- No implied persistence

5️⃣ Error policy declaration (fail-fast vs best-effort)
Add:

error_policy:
  default: fail_fast | best_effort
  retries:
    enabled: true|false
    max_attempts: 0|1|3
  compensating_action: none | emit_error_packet | rollback

Rules:
- No silent failure
- Used directly by executor + tests

6️⃣ Module dependency declaration (schema-enforced)
Add:

dependencies:
  allowed_tiers: [0,1,2]
  outbound_calls:
    - module: memory.service
      interface: http

Rules:
- Generator must verify tier legality
- Violations → SPEC_BLOCKERS

7️⃣ Spec confidence + evidence (forces honesty)
Add at bottom:

spec_confidence:
  level: high | medium | low
  basis:
    - "Existing code present"
    - "Spec-only, no implementation yet"

Rules:
- Required
- Prevents false certainty

REQUIRED REMOVALS / CONSTRAINTS
C must ensure the schema:

❌ does NOT allow:
- "if applicable"
- "optional unless needed"
- free-form booleans without explanation

❌ does NOT infer defaults
❌ does NOT allow missing sections

Validation must fail loudly.

VALIDATION UPDATES (MANDATORY)
C must also update:
- JSON Schema / Pydantic validator (if present)
- Any spec loader that assumes older fields
- Any generator that relied on implicit defaults

Backward compatibility:
- v2.1 specs must still load
- v2.2 features required only when schema_version >= 2.2

ACCEPTANCE CRITERIA
- A spec missing any of the new sections fails validation
- Generators cannot produce code without negative tests
- Runtime touchpoints can be extracted mechanically
- No ambiguity remains in idempotency or error handling
- No downstream prompt needs to "remind" agents of these rules

DELIVERABLES FROM C
- Module-Spec-v2.2.yaml
- Updated validator (if applicable)
- Migration note: v2.1 → v2.2
- Example minimal spec that passes validation
- Confirmation that P + codegen still load v2.1 unchanged
```

---

## C-PROMPT 2: FINAL HARDENING OF Module-Spec.yaml (v2.2 → v2.3)

```
🔧 C-GMP — FINAL HARDENING OF Module-Spec.yaml (v2.2 → v2.3)

OBJECTIVE
Evolve Module-Spec-v2.2.yaml to v2.3 to fully encode:
- deployment exposure
- packet guarantees
- boot criticality
- test coverage expectations

This pass completes the spec as a deterministic contract for research, codegen, testing, and deployment.

REQUIRED ADDITIONS

1️⃣ External surface (deployment clarity)
Add required section:

external_surface:
  exposes_http_endpoint: true|false
  exposes_webhook: true|false
  exposes_tool: true|false
  callable_from:
    - external
    - internal

Rules:
- No defaults
- Must be explicit
- Used by routing + security tests

2️⃣ Packet contract (schema-enforced)
Add required section:

packet_contract:
  emits:
    - string
  requires_metadata:
    - task_id
    - thread_uuid
    - source

Rules:
- emits must list all packet types the module can write
- Generators must validate packet usage against this list

3️⃣ Boot impact classification
Add required section:

boot_impact:
  level: none | soft | hard
  reason: string

Rules:
- hard → missing config fails service boot
- soft → feature disabled but service boots
- No ambiguity

4️⃣ Test scope declaration
Add required section:

test_scope:
  unit: true
  integration: true
  docker_smoke: true|false

Rules:
- Tier 2 modules must set integration: true
- docker_smoke: true required if external_surface.exposes_http_endpoint == true

VERSIONING + COMPATIBILITY
- Create Module-Spec-v2.3.yaml
- Keep v2.1 and v2.2 loadable
- New fields required only when schema_version >= 2.3

ACCEPTANCE CRITERIA
- Spec missing any new section fails validation
- Deployment tooling can infer exposure + boot risk
- Test generators know exactly what to build
- No prompt needs to restate these rules

DELIVERABLES
- Module-Spec-v2.3.yaml
- Updated validator / loader
- Example Tier-2 spec that passes v2.3
- Migration notes v2.2 → v2.3
```

---

## C-PROMPT 3: MODULE-SPEC v2.4 (OPERATIONAL / ENTERPRISE GRADE)

```
🔧 C-GMP — MODULE-SPEC v2.4 (OPERATIONAL / ENTERPRISE GRADE)

OBJECTIVE
Evolve Module-Spec-v2.3.yaml to v2.4 so that each module spec fully defines:
- runtime placement
- startup ordering
- service dependencies
- failure blast radius
- observability intent
- deploy-time guarantees

After this change, no runtime wiring decisions are left to humans.

VERSIONING
Create: Module-Spec-v2.4.yaml
- Keep v2.1–v2.3 loadable
- New fields required only when schema_version >= 2.4

REQUIRED ADDITIONS (ALL MANDATORY)

1️⃣ Runtime wiring (keystone field)

runtime_wiring:
  service: api | worker | scheduler | memory
  startup_phase: early | normal | late
  depends_on:
    - postgres
    - redis
    - memory.service
  blocks_startup_on_failure: true | false

Rules:
- No defaults
- depends_on must be resolvable from runtime manifest
- If blocks_startup_on_failure: true, missing dependency = hard boot fail

2️⃣ Observability intent (ops-visible)

observability:
  logs:
    enabled: true
    level: info | debug
  metrics:
    enabled: true
    counters:
      - requests_total
      - errors_total
  traces:
    enabled: true

Rules:
- This declares what must exist, not how it's implemented
- Generators may not omit declared signals

3️⃣ Ownership (enterprise hygiene)

ownership:
  team: core | infra | integrations
  primary_contact: role_name

Rules:
- Required
- Used by ops, on-call, and incident tooling later

4️⃣ Operationalized outbound wiring
Upgrade dependencies to be executable:

dependencies:
  outbound_calls:
    - module: memory.service
      interface: http
      endpoint: /memory/ingest

Rules:
- No vague "calls X"
- Endpoint or tool_id must be declared

5️⃣ Error policy escalation (ops signal)

error_policy:
  default: fail_fast | best_effort
  escalation:
    emit_error_packet: true | false
    mark_task_failed: true | false
    alert: none | log | metric

6️⃣ Deployment guarantees (tie spec → tests)
Add rules to spec validation:
- If runtime_wiring.service != api → test_scope.integration == true
- If external_surface.exposes_http_endpoint == true → test_scope.docker_smoke == true
- If startup_phase == early → boot-failure test required

These are schema-enforced, not advisory.

VALIDATION UPDATES (MANDATORY)
C must update:
- schema validator
- spec loader
- any codegen that assumed implicit runtime behavior

Validation must fail if:
- runtime_wiring missing
- startup_phase omitted
- unresolved dependencies exist
- observability omitted

DELIVERABLES FROM C
- Module-Spec-v2.4.yaml
- Updated validator
- Example Tier-2 spec passing v2.4
- Migration notes v2.3 → v2.4

ACCEPTANCE CRITERIA
A module spec alone is sufficient to:
- place the module in runtime
- determine startup order
- generate docker dependencies
- generate smoke tests
No human inference required
```

---

## C-PROMPT 4: MODULE SPEC OPERATIONAL LOCK (GODMODE v2.4)

```
🔧 C-GMP — MODULE SPEC OPERATIONAL LOCK
Upgrade: Module-Spec-v2.3.yaml → Module-Spec-v2.4.yaml
Grade: Production / Enterprise / Runtime-Executable

🎯 PURPOSE (AUTHORITATIVE)
Revise the canonical Module Spec YAML so that a single module spec is sufficient to:
- determine runtime placement
- determine startup order
- determine service dependencies
- determine failure blast radius
- determine observability requirements
- determine test obligations
- generate docker-compose wiring
- generate runtime + smoke tests

After this change, no runtime decisions may be inferred by humans or generators.

🔢 VERSIONING (MANDATORY)

schema_version: "2.4"

Compatibility Rules:
- v2.1–v2.3 specs must continue to load
- All fields below are REQUIRED when schema_version >= 2.4
- Validation must fail hard if any required section is missing

🧱 REQUIRED TOP-LEVEL SECTIONS (ORDER IS CANONICAL)
C must enforce this exact structural order in the schema:

1. metadata
2. ownership
3. runtime_wiring
4. external_surface
5. dependencies
6. packet_contract
7. idempotency
8. error_policy
9. observability
10. runtime_touchpoints
11. test_scope
12. acceptance
13. global_invariants_ack
14. spec_confidence

1️⃣ METADATA (UNCHANGED, BUT REQUIRED)

metadata:
  module_id: string
  name: string
  tier: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7
  description: string

2️⃣ OWNERSHIP (ENTERPRISE HYGIENE — REQUIRED)

ownership:
  team: core | infra | integrations | security | observability
  primary_contact: role_name

Rules:
- Required
- No free-text teams
- Used for ops / on-call / escalation

3️⃣ RUNTIME WIRING (KEYSTONE — REQUIRED)

runtime_wiring:
  service: api | worker | scheduler | memory
  startup_phase: early | normal | late
  depends_on:
    - postgres
    - redis
    - memory.service
  blocks_startup_on_failure: true | false

Rules:
- No defaults
- depends_on MUST reference resolvable runtime services
- If blocks_startup_on_failure: true → missing dependency = hard boot fail

This section is the single source of truth for:
- docker-compose ordering
- startup health checks
- boot-failure tests

4️⃣ EXTERNAL SURFACE (DEPLOYMENT EXPOSURE — REQUIRED)

external_surface:
  exposes_http_endpoint: true | false
  exposes_webhook: true | false
  exposes_tool: true | false
  callable_from:
    - external
    - internal

Rules:
- No inference
- If exposes_http_endpoint: true → docker smoke test REQUIRED
- Used by routing + Caddy validation

5️⃣ DEPENDENCIES (EXECUTABLE, NOT DESCRIPTIVE — REQUIRED)

dependencies:
  allowed_tiers: [0, 1, 2]
  outbound_calls:
    - module: memory.service
      interface: http | tool
      endpoint: /memory/ingest

Rules:
- Tier legality must be validated
- No "calls X" without endpoint or tool_id
- Violations = SPEC_BLOCKERS

6️⃣ PACKET CONTRACT (RUNTIME GUARANTEES — REQUIRED)

packet_contract:
  emits:
    - module.in
    - module.out
    - module.error
  requires_metadata:
    - task_id
    - thread_uuid
    - source

Rules:
- Runtime must BLOCK undeclared packet writes
- Tests must validate declared packets only
- Packet metadata is mandatory

7️⃣ IDEMPOTENCY (NO INFERENCE — REQUIRED)

idempotency:
  pattern: event_id | composite_key | substrate_lookup
  source: slack_event_id | webhook_header | computed_hash
  durability: in_memory | substrate

Rules:
- Must map to SSOT
- Durability must be explicit
- No implied persistence

8️⃣ ERROR POLICY (OPS-VISIBLE — REQUIRED)

error_policy:
  default: fail_fast | best_effort
  escalation:
    emit_error_packet: true | false
    mark_task_failed: true | false
    alert: none | log | metric

Rules:
- Silent failure forbidden
- Used by runtime + alerting

9️⃣ OBSERVABILITY (INTENT DECLARATION — REQUIRED)

observability:
  logs:
    enabled: true
    level: info | debug
  metrics:
    enabled: true
    counters:
      - requests_total
      - errors_total
  traces:
    enabled: true

Rules:
- Declares what must exist, not implementation
- Generators may not omit declared signals

🔟 RUNTIME TOUCHPOINTS (DEPLOYMENT INTELLIGENCE — REQUIRED)

runtime_touchpoints:
  touches_db: true | false
  touches_tools: true | false
  touches_external_network: true | false
  affects_boot: true | false

1️⃣1️⃣ TEST SCOPE (DEPLOYMENT GUARANTEES — REQUIRED)

test_scope:
  unit: true
  integration: true
  docker_smoke: true | false

Enforced Rules:
- If external_surface.exposes_http_endpoint: true → docker_smoke: true
- If runtime_wiring.service != api → integration: true
- If startup_phase: early → boot-failure test REQUIRED

1️⃣2️⃣ ACCEPTANCE (POSITIVE + NEGATIVE — REQUIRED)

acceptance:
  positive:
    - id: AP-1
      description: "Valid request processed successfully"
  negative:
    - id: AN-1
      description: "Unknown tool_id hard fails"
      expected_behavior: "Request rejected before execution"

Rules:
- At least 1 negative case required
- Must reference auth, idempotency, malformed input, or unknown tool_id

1️⃣3️⃣ GLOBAL INVARIANTS ACKNOWLEDGEMENT (SYSTEM LAW — REQUIRED)

global_invariants_ack:
  emits_packet_on_ingress: true
  tool_calls_traceable: true
  unknown_tool_id_hard_fail: true
  malformed_packet_blocked: true
  missing_env_fails_boot: true

Rules:
- All values must be true
- Any deviation invalidates spec

1️⃣4️⃣ SPEC CONFIDENCE (HONESTY LOCK — REQUIRED)

spec_confidence:
  level: high | medium | low
  basis:
    - "Existing code present"
    - "Spec-only, no implementation yet"

🚫 FORBIDDEN (SCHEMA-LEVEL)
The schema MUST NOT allow:
- "if applicable"
- optional runtime wiring
- inferred dependencies
- undeclared packet emission
- implicit boot behavior

Validation must fail loudly.

🧪 VALIDATION UPDATES (MANDATORY)
C must update:
- schema validator
- spec loader
- any generator relying on implicit behavior

📦 DELIVERABLES FROM C
- Module-Spec-v2.4.yaml
- Updated validator
- Example Tier-2 spec passing v2.4
- Migration notes v2.3 → v2.4

✅ ACCEPTANCE CRITERIA
A single spec can generate:
- docker wiring
- startup order
- smoke tests
- integration tests

No human inference required
No runtime ambiguity remains
```

---

## Summary

| # | Prompt Name | Purpose | Target Version |
|---|-------------|---------|----------------|
| 1 | C-GMP — REVISION OF Module-Spec.yaml | Add invariants, touchpoints, negative cases, idempotency, error policy, dependencies, confidence | v2.1 → v2.2 |
| 2 | C-GMP — FINAL HARDENING | Add external surface, packet contract, boot impact, test scope | v2.2 → v2.3 |
| 3 | C-GMP — OPERATIONAL / ENTERPRISE GRADE | Add runtime wiring, observability, ownership, operationalized dependencies | v2.3 → v2.4 |
| 4 | C-GMP — OPERATIONAL LOCK (GODMODE) | Complete enterprise-grade spec with all 14 canonical sections | v2.3 → v2.4 (Final) |


🔧 C_GOD_MODE PROMPT — MODULE-SPEC v2.5

Scope: STRICT 2.4 → 2.5
Mode: Normalization / SSOT Ingestion
Rule: NO behavioral change

🎯 OBJECTIVE (READ CAREFULLY)

You are upgrading the canonical Module-Spec schema from v2.4 to v2.5.

This is a NORMALIZATION RELEASE, not a redesign.

Your job is to:

absorb existing SSOT semantics into explicit schema fields

remove remaining interpretation

preserve all runtime behavior exactly as-is

🚫 You are NOT allowed to:

change meaning of any v2.4 field

add new operational rules

redefine tiers

alter runtime behavior

“improve” semantics

refactor earlier versions

If something would change behavior, STOP and report it instead.

🔢 VERSIONING RULES (MANDATORY)
schema_version: "2.5"


v2.1–v2.4 MUST remain loadable

v2.5 fields are REQUIRED only when schema_version >= 2.5

Validators must enforce strict version gating

🧠 SOURCE OF TRUTH (BINDING)

Treat these as authoritative SSOT inputs:

DOCTRINE-Module-Spec.md

L9_DEPENDENCIES_SSOT.md

L9_RUNTIME_SSOT.md

L9_IDEMPOTENCY_SSOT.md

MANUS_CONTEXT_PACK.md

Your task is to encode what these already say, not reinterpret them.

✅ REQUIRED ADDITIONS (v2.5 ONLY)
1️⃣ Dependency Contract (directional normalization)

Add this section without changing behavior:

dependency_contract:
  inbound:
    - from_module: slack.adapter
      interface: http | tool
      endpoint: /webhook/slack
  outbound:
    - to_module: memory.service
      interface: http | tool
      endpoint: /memory/ingest


Rules:

Direction MUST be explicit

This mirrors existing dependency logic

No new validation rules beyond clarity

2️⃣ Runtime Contract (semantic labeling only)

Normalize runtime semantics already implied by runtime_wiring:

runtime_contract:
  runtime_class: control_plane | data_plane | background
  execution_model: request_driven | event_driven | scheduled


Rules:

This does NOT alter startup, wiring, or blocking

Labels only — used for tooling and reasoning

Must align with existing runtime_wiring

3️⃣ Packet Expectations (explicit outcome mapping)

Clarify packet behavior already required by doctrine:

packet_expectations:
  on_success:
    emits:
      - module.out
  on_error:
    emits:
      - module.error
  durability:
    success: durable
    error: durable


Rules:

No new packet types allowed

This maps intent → enforcement

Must match existing packet_contract

4️⃣ Tier Expectations (machine-readable, not prose)

Encode tier rules that already exist implicitly:

tier_expectations:
  requires_runtime_wiring: true
  requires_packet_contract: true
  requires_negative_tests: true


Rules:

No tier logic changes

No new enforcement beyond existing rules

Purpose is elimination of inference

❌ FORBIDDEN CHANGES (ABSOLUTE)

You MUST NOT:

modify any v2.4 field meaning

add infra details (ports, replicas, sizing)

alter idempotency semantics

change error_policy behavior

touch observability rules

collapse or merge existing sections

If you feel tempted to do so, STOP.

🧪 VALIDATION REQUIREMENTS

Update schema validators to ensure:

v2.5 fields are required when version ≥ 2.5

v2.4 and below remain unaffected

Missing v2.5 fields produce clear validation errors

📦 DELIVERABLES (ALL REQUIRED)

Module-Spec-v2.5.yaml

Validator update with strict version gating

Explicit schema diff: v2.4 → v2.5

One example Tier-2 spec that passes v2.5

Short note confirming:
“No behavioral change from v2.4.”

🧠 ACCEPTANCE CRITERIA

v2.5 adds clarity, not power

Runtime behavior remains identical

All SSOT concepts are now machine-readable

No human interpretation required

Diff is reviewable and boring (this is good)

🔒 FINAL RULE (READ THIS TWICE)

v2.4 made specs executable.
v2.5 makes them unambiguous.
Nothing else.

---
*Extracted for Cursor implementation tasks*

