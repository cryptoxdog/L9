# **Module Spec YAML (SPEC)**

GENERATION_GATES:
  spec_preflight:
    fail_if_missing_required_keys: true
    output_only_on_failure: ["SPEC_BLOCKERS.yaml"]
  change_budget:
    max_new_files: 3
    max_modified_files: 4
    max_net_loc: 450
  output_files_only:
    enforce_allowed_new_files_only: true
    enforce_allowed_modified_files: true
  required_artifacts_before_code:
    - PLAN.yaml
    - DEPENDENCY_BINDINGS.yaml
    - FAILURE_MODES.md
    - ACCEPTANCE_TRACE.md
  self_scan_forbidden_patterns: true
module_spec:

id: "{{module_id}}"

name: "{{module_name}}"

system: "L9"

owner: "Boss"

language: "python"

runtime: "python>=3.11"

purpose: "{{purpose_one_liner}}"

goals:

- "{{goal_1}}"

- "{{goal_2}}"

non_goals:

- "{{non_goal_1}}"

- "No new schema/migrations"

- "No duplicate stacks (db/models/logger/exceptions/config)"

repo_bindings:

root_path: "{{repo_root_path}}"

must_import_and_use:

{{must_import_and_use_list_yaml}}

must_not_create:

- "parallel database layer"

- "parallel models layer"

- "parallel logger/exceptions layer"

- "parallel config system"

allowed_new_files_only:

{{allowed_new_files_only_yaml}}

allowed_modified_files:

{{allowed_modified_files_yaml}}

schema_truth:

tables:

{{schema_truth_tables_yaml}}

notes: "{{schema_notes}}"

interfaces:

inbound:

{{inbound_interfaces_yaml}}

outbound:

{{outbound_interfaces_yaml}}

orchestration:

context_reads:

{{context_reads_yaml}}

aios_calls:

- name: "chat"

endpoint: "/chat"

timeout_seconds: {{aios_chat_timeout}}

- name: "embeddings_optional"

endpoint: "/memory/embeddings"

enabled: {{embeddings_enabled}}

persistence_writes:

{{persistence_writes_yaml}}

policies:

auth_and_verification:

{{auth_policy_yaml}}

idempotency:

enabled: {{idempotency_enabled}}

primary_key: "{{dedupe_primary}}"

fallback_key: "{{dedupe_fallback}}"

on_duplicate: "{{dedupe_behavior}}"

error_policy:

invalid_auth_or_signature: "{{policy_invalid_auth}}"

upstream_aios_failure: "{{policy_aios_failure}}"

side_effect_failure: "{{policy_side_effect_fail}}"

acceptance_criteria:

required:

{{acceptance_required_yaml}}

forbidden:

- "introduces new tables"

- "duplicates memory substrate code"

- "adds unrelated scaffolding"

tests:

scope:

{{tests_scope_yaml}}

must_not_require:

- "real external APIs"

- "real production DB"

observability:

required_logs:

{{required_logs_yaml}}

metrics:

{{metrics_yaml}}

