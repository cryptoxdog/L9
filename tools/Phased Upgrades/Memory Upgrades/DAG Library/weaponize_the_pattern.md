**Codifying and “weaponizing” the pattern for agents**

To make agents actually use this pattern:

- Turn the pattern into a **prompt + control spec**:
  - Prompt template:
    - “You are an architect agent. Follow these stages: [list nodes]. At each stage:
       1) Read current spec.
       2) Produce output in JSON with this schema: {...}.
       3) Stop after stage N and wait for the orchestrator.”
  - Control spec (your YAML pattern) tells the orchestrator:
    - Which agent to call per stage.
    - What schema to expect.
    - What validations to run.
- Build a small **orchestrator** in L9:
  - Reads the DAG/pattern.
  - For each node:
    - Assembles the input context (previous outputs + repo state).
    - Calls the appropriate agent/tool with the right prompt template.
    - Validates the output against the schema in the pattern.
    - Writes artifacts to memory segments.
- Reuse across subsystems:
  - For a new subsystem (e.g., tools, auth, memory retrieval), you:
    - Fill `metadata`, `goals`, and `pipeline.stages` instance data.
    - Keep `pattern` and DAG logic the same.
  - The orchestrator can run the same high-level cycle (design → frontier review → TODO → approval → implementation → validation) for any subsystem, not just code mutation.