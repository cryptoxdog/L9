# **Cursor GMP (Wire-in + Finish + Track Changes)**

cursor_gmp:

id: "{{gmp_id}}"

objective: >

Wire the module into the existing L9 repo with minimal diffs, honoring repo bindings,

and ensuring every changed file is tracked and test-verified.

invariants:

- "No new schema/migrations"

- "Do not modify shared substrate/services unless SPEC explicitly allows"

- "All changes must be enumerated and git-tracked"

- "Minimal diff; no refactors unless required to pass gates"

file_plan:

add:

{{files_to_add_yaml}}

modify_if_needed:

{{files_to_modify_yaml}}

forbidden:

{{forbidden_files_yaml}}

wiring_steps:

{{wiring_steps_yaml}}

verification_gates:

commands:

{{verify_commands_yaml}}

required_checks:

- "imports resolve"

- "routes/entrypoints reachable"

- "unit tests pass"

- "idempotency works (if enabled)"

- "persistence writes hit correct existing tables"

git_discipline:

required_outputs:

- "git status --porcelain"

- "git diff --stat"

- "list_of_files_added"

- "list_of_files_modified"

- "tests_run + results"

commit_message_template: "{{commit_message_template}}"

integration_notes:

aios:

- "Use existing AIOS helpers if present; otherwise implement thin wrapper local to module files."

memory:

- "Adapter bends to existing memory APIs; do not reshape memory layer."

rollback:

- "If gates fail, revert to last green commit and re-apply minimal patch."

# **How we use these for 10+ modules (repeatable factory flow)**

- For each module, we generate three filled artifacts:
    1. PSGP.<module>.txt (Perplexity codegen contract)
    2. SPEC.<module>.yaml (binding truth + acceptance)
    3. GMP.<module>.yaml (Cursor wire-in protocol)
- 
- Output discipline:
    1. PSGP strictly controls what files Perplexity is allowed to touch
    2. SPEC defines truth + constraints
    3. GMP forces minimal diffs + tracked changes + gates
- 

If you want, I’ll also give you a single “Module Pack Header” block (common keys + default policies) you can paste at the top of every SPEC to reduce drift.
