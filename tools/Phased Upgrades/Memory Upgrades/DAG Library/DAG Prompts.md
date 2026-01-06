<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Make what I need to instantiate and execute on these:

Represent your reasoning flow as a DAG and let an orchestrator agent follow it step by step.
•	Codify the whole thing as a reusable “pipeline pattern” plus prompt templates, so CA and other L9 agents can execute the same architecture-and-governance strategy automatically.

You need three things: a DAG spec, an orchestrator contract, and prompt templates. Together they let L9 agents reuse your architecture-and-governance pattern automatically.[^1][^2]

***

## 1) DAG spec for your reasoning flow

Use this as a reusable YAML artifact (not tied to code-mutation only):

```yaml
spec_kind: l9_agentic_dag
version: 1

dag:
  uid: dag.l9.architecture_pipeline
  name: L9 Architecture & Governance Pipeline
  description: >
    Multi-stage reasoning and implementation DAG for designing, scoping,
    implementing, and validating L9 subsystems with frontier-grade governance.

  nodes:
    - id: N1
      uid: node.requirements_elicitation
      name: RequirementsElicitation
      kind: reasoning
      role: ArchitectAgent
      inputs:
        - type: user_prompts
      outputs:
        - type: requirements_doc
          schema: requirements_schema.v1
      next: [node.pipeline_architecture_draft]

    - id: N2
      uid: node.pipeline_architecture_draft
      name: PipelineArchitectureDraft
      kind: reasoning
      role: ArchitectAgent
      inputs:
        - type: requirements_doc
      outputs:
        - type: pipeline_draft
          schema: pipeline_schema.v1
      next: [node.frontier_comparison_loop]

    - id: N3
      uid: node.frontier_comparison_loop
      name: FrontierComparisonLoop
      kind: reasoning
      role: ArchitectAgent
      inputs:
        - type: pipeline_draft
      outputs:
        - type: pipeline_refined
          schema: pipeline_schema.v1
        - type: frontier_gap_report
          schema: gap_report_schema.v1
      next: [node.todo_plan]

    - id: N4
      uid: node.todo_plan
      name: DeterministicTODOPlan
      kind: reasoning
      role: ArchitectAgent
      inputs:
        - type: pipeline_refined
      outputs:
        - type: todo_plan
          schema: todo_schema.v1
      next: [node.plan_approval]

    - id: N5
      uid: node.plan_approval
      name: PlanApproval
      kind: governance
      role: HumanOrApproverAgent
      inputs:
        - type: todo_plan
      outputs:
        - type: plan_approval
          schema: approval_schema.v1
      decision:
        on_approved: [node.implementation]
        on_rejected: [node.todo_plan]

    - id: N6
      uid: node.implementation
      name: Implementation
      kind: implementation
      role: CoderAgent
      inputs:
        - type: todo_plan
        - type: plan_approval
      outputs:
        - type: impl_artifacts
          schema: impl_schema.v1
      next: [node.validation]

    - id: N7
      uid: node.validation
      name: Validation
      kind: validation
      role: QAAgent
      inputs:
        - type: impl_artifacts
        - type: todo_plan
      outputs:
        - type: validation_report
          schema: validation_schema.v1
      next: []

  schemas:
    requirements_schema.v1:
      fields:
        - name: goals
          type: list[str]
        - name: constraints
          type: list[str]
        - name: risks
          type: list[str]

    pipeline_schema.v1:
      fields:
        - name: stages
          type: list[dict]
        - name: risk_model
          type: dict
        - name: memory_model
          type: dict

    gap_report_schema.v1:
      fields:
        - name: frontier_gaps
          type: list[str]
        - name: mitigations
          type: list[str]

    todo_schema.v1:
      fields:
        - name: files
          type: list[dict]   # {path, role, action}
        - name: tests
          type: list[dict]
        - name: workflows
          type: list[dict]

    approval_schema.v1:
      fields:
        - name: approved
          type: bool
        - name: approver
          type: str
        - name: notes
          type: str

    impl_schema.v1:
      fields:
        - name: generated_files
          type: list[dict]   # {path, content}
        - name: updated_files
          type: list[dict]

    validation_schema.v1:
      fields:
        - name: passed
          type: bool
        - name: issues
          type: list[str]
        - name: recommendations
          type: list[str]
```

You can reuse this DAG for any L9 subsystem by just changing the **content** of artifacts, not the structure.

***

## 2) Orchestrator contract for L9

This is what the orchestrator agent (or service) needs to do for any DAG like the above:

- Input:
    - `dag_uid` (e.g., `dag.l9.architecture_pipeline`).
    - `subsystem_name` (e.g., `code_mutation`).
    - `user_prompts` (raw requirements from you).
- Behavior (high-level):

1. Load DAG spec by `dag_uid`.
2. Start at nodes with no prerequisites (`RequirementsElicitation`).
3. For each node:
        - Build context from:
            - Inputs specified in the DAG.
            - Previous nodes’ outputs.
            - Repo/memory state as needed.
        - Call the appropriate agent/tool with a **node-specific prompt template**.
        - Validate the result against the node’s schema.
        - Persist the output (e.g., into a `design_artifacts` segment).
        - Decide next node(s) based on `next` or `decision` fields.

You can describe this orchestrator in a short YAML/contract:

```yaml
orchestrator_spec:
  uid: orchestrator.l9.architecture_pipeline
  input:
    - name: dag_uid
      type: string
    - name: subsystem_name
      type: string
    - name: user_prompts
      type: list[str]
  behavior:
    - load_dag_by_uid
    - resolve_start_nodes
    - for_each_node_in_topological_order:
        - assemble_context_from_previous_outputs_and_repo_state
        - select_agent_by_role(node.role)
        - select_prompt_template_by_node_uid(node.uid)
        - call_agent_with_context_and_template
        - validate_output_against_node_schema
        - persist_output_to_memory
        - schedule_next_nodes_based_on_node.next_or_decision
```


***

## 3) Prompt templates for each node (pipeline pattern)

These are reusable templates the orchestrator uses per node.

### N1: RequirementsElicitation (ArchitectAgent)

```text
You are the Architect agent for the L9 OS.

Task:
- Read the user's prompts and extract:
  - Goals
  - Constraints
  - Risks

Output:
- A JSON object with schema requirements_schema.v1:
  {
    "goals": [ ... ],
    "constraints": [ ... ],
    "risks": [ ... ]
  }

User prompts:
{{ user_prompts }}
```


### N2: PipelineArchitectureDraft

```text
You are the Architect agent.

Task:
- Design an agentic pipeline for subsystem "{{ subsystem_name }}", given:
  - Requirements:
    {{ requirements_doc }}

- Define:
  - Stages (Generation, Verification, Approval, Mutation, CI/PR or equivalents)
  - Risk model
  - Memory model

Output:
- JSON matching pipeline_schema.v1:
  {
    "stages": [...],
    "risk_model": {...},
    "memory_model": {...}
  }
```


### N3: FrontierComparisonLoop

```text
You are the Architect agent with knowledge of frontier AI lab practices.

Task:
- Compare this pipeline draft against frontier patterns:
  - Dedicated generator and reviewer agents.
  - Multi-stage verification (tests, static analysis, security).
  - Defense-in-depth (sandbox, guardrails, branch protection, manual override).

Input pipeline draft:
{{ pipeline_draft }}

Output:
1) A refined pipeline (pipeline_schema.v1), incorporating improvements.
2) A frontier gap report (gap_report_schema.v1) describing gaps and mitigations.

Return JSON:
{
  "pipeline_refined": { ... },
  "frontier_gap_report": { ... }
}
```


### N4: DeterministicTODOPlan

```text
You are the Architect agent.

Task:
- Turn the refined pipeline into a deterministic TODO plan for subsystem "{{ subsystem_name }}":
  - Files to create/update (path, role, brief responsibility).
  - Tests to add.
  - Workflows/CI to add.
- Be specific but do not generate code here.

Input refined pipeline:
{{ pipeline_refined }}

Output:
- JSON matching todo_schema.v1:
  {
    "files": [...],
    "tests": [...],
    "workflows": [...]
  }
```


### N5: PlanApproval (Human or ApproverAgent)

For the human, this is just a UI. For an ApproverAgent, you can use:

```text
You are the Approver agent representing the CTO.

Task:
- Review this TODO plan for subsystem "{{ subsystem_name }}":
  {{ todo_plan }}

- Decide whether to approve or request changes.

Output JSON (approval_schema.v1):
{
  "approved": true/false,
  "approver": "L" or "CTO" or similar,
  "notes": "short rationale"
}
```


### N6: Implementation (CoderAgent)

```text
You are the Coder agent.

Task:
- Implement the TODO plan for subsystem "{{ subsystem_name }}":
  {{ todo_plan }}

Constraints:
- Follow L9 style and invariants.
- Only modify files listed in the TODO.
- Produce production-grade code, not pseudocode.

Output:
- JSON matching impl_schema.v1:
  {
    "generated_files": [{"path": "...", "content": "..."}, ...],
    "updated_files": [{"path": "...", "content": "..."}, ...]
  }
```


### N7: Validation (QAAgent)

```text
You are the QA agent.

Task:
- Validate the implementation artifacts for subsystem "{{ subsystem_name }}":
  {{ impl_artifacts }}

- Check:
  - Tests defined in the TODO are present.
  - Basic static checks and consistency with the pipeline.

Output:
- JSON matching validation_schema.v1:
  {
    "passed": true/false,
    "issues": [...],
    "recommendations": [...]
  }
```


***

## How to use this in practice

- To start a new subsystem:

1) Supply:
        - The **pattern DAG YAML**.
        - The **orchestrator spec**.
        - These **node prompt templates**.
2) Call your orchestrator with:
        - `dag_uid: dag.l9.architecture_pipeline`.
        - `subsystem_name: "your_subsystem"`.
        - `user_prompts: [...]` (your high-level requirements).
3) Let it walk N1→N7, using agents and templates, producing:
        - Requirements doc.
        - Pipeline spec.
        - Frontier gap report.
        - TODO plan.
        - Approval.
        - Implementation artifacts.
        - Validation report.

This gives CA and the rest of L9 a repeatable way to **copy your architecture-and-governance reasoning pattern** and apply it to any new subsystem.
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://dev.to/ivan_holovach_f2abf13a514/a-dag-based-approach-to-llm-workflow-orchestration-1i98

[^2]: https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/workflow-for-prompt-chaining.html

[^3]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/05b609da-007a-430b-981e-e1f6d610cdd6/i-need-help-with-my-dockercomp-hjS70i6oR9Ovs.UASQ5aSQ.md

[^4]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/1f806849-c152-4e58-9488-a6fd2e1b0aec/wiring_map.txt

[^5]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/f410b847-1f19-40ab-b1a5-507e319249ef/tree.txt

[^6]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/9da3c987-d8a9-4651-b880-8a43e3291900/tool_catalog.txt

[^7]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/d0c6091d-9a72-4774-93f2-50834e4c076d/singleton_registry.txt

[^8]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/427ce514-206f-44a6-9703-cfb070dd9741/orchestrator_catalog.txt

[^9]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/45ea34f5-bb45-4d83-9dfd-679fd7f88a3c/kernel_catalog.txt

[^10]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/f8584309-6c1f-4b8f-9153-2f324399b1cb/imports.txt

[^11]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/ec4dd61b-c2cd-4f2d-aedd-f2d5e17a5be3/function_signatures.txt

[^12]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/ac875518-1388-4780-8e35-e48008965537/event_types.txt

[^13]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/eb6064b6-c51f-4689-9733-3f082be26e71/env_refs.txt

[^14]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/f47f9ff5-ad8b-4dff-b0c0-8d1ebaa3c951/entrypoints.txt

[^15]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/c9f8012a-b7d4-4c6b-beb2-7c63d1881f23/dependencies.txt

[^16]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/f33e17c7-10d8-4f9c-b92c-4d1e7520989e/config_files.txt

[^17]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/f07fa794-2b80-4bdd-b0ad-92021002263e/class_definitions.txt

[^18]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/fae9bc47-a20c-4b47-97ba-36f62b6d38f8/architecture.txt

[^19]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/dd6092af-2909-4ea3-bfa7-e978908ab085/api_surfaces.txt

[^20]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_28a5acba-b23e-4b01-9740-de9323d1c6c6/60c76ef9-fda9-45ea-8839-e371a8a4077e/agent_catalog.txt

[^21]: https://ppl-ai-file-upload.s3.amazonaws.com/connectors/dropbox/id:AodXdp68OMMAAAAAABPV4w/eae88eed-ccd5-4cd2-af34-1b10fa4a3ed6/health.py

[^22]: https://ppl-ai-file-upload.s3.amazonaws.com/connectors/dropbox/id:AodXdp68OMMAAAAAABPV5Q/dc6b6ba5-40f9-4be3-8e6c-f0920e35b314/memory.py

