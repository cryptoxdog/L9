spec_kind: agentic_pipeline_pattern
version: 1

pattern:
  description: >
    Canonical pattern for multi-stage, agentic pipelines with risk-based approvals,
    governed memory, and CI/PR integration. Reusable for any L9 subsystem.

  metadata:
    fields:
      name: string
      uid: string
      domain: string          # e.g., code_mutation, tools, auth
      criticality: string     # low | medium | high
      agents:                 # roles involved
        - string
      parameters:             # env/secret-driven configuration
        key: string           # e.g., repo_url, api_base_url

  stage_interface:
    fields:
      id: string
      uid: string
      name: string
      role: string            # CoderAgent | QAAgent | RiskEngine | GitWorker | Orchestrator
      goals_ref: [string]     # references to goals uids
      input_contract:
        - name: string
          type: string
          required: bool
      output_contract:
        - name: string
          type: string
          required: bool
      preconditions: [string]
      postconditions: [string]
      memory_interactions:
        reads:
          - segment: string
            predicate: string
        writes:
          - segment: string
            packet_type: string
      external_calls:
        - system: string      # e.g., LLM, GitHub, DB, Tool
          contract: string    # summary of API/behavior

  risk_model_schema:
    levels:
      - id: string            # low | medium | high
        uid: string
        approval_level: string    # auto_qa | auto_architect | manual_human
        conditions: [string]     # predicates on verification outputs
    scoring:
      inputs: [string]           # e.g., VerificationReport fields
      rules: [string]            # declarative risk additions
      mapping: [string]          # score→approval level
      range: [int,int]

  memory_schema:
    segment_fields:
      - name: string
        uid: string
        immutable: bool
        max_age_days: int
        packet_types: [string]
        search_strategy: string   # vector | structured | hybrid
        invariants: [string]      # segment-level constraints

  github_integration_schema:
    workflows:
      - path: string
        uid: string
        triggers: [string]       # events (issue, pull_request, workflow_run, etc.)
        jobs: [string]           # logical job names
    branch_protection:
      branch: string
      required_status_checks: [string]
      require_reviews:
        min_approvals: int
      disallow: [string]         # e.g., direct_pushes, force_pushes

  phases_schema:
    # Generic process used before implementation for any subsystem
    phases:
      - id: P0
        uid: phase.design_scope_lock
        name: DesignAndScopeLock
        steps:
          - id: RequirementsElicitation
            description: Gather safety, approval, integration requirements.
          - id: PipelineArchitectureDraft
            description: Draft multi-stage pipeline (Generation, Verification, Approval, Mutation, CI/PR).
          - id: FrontierComparisonLoop
            description: >
              Compare draft against frontier-lab patterns (multi-agent, defense-in-depth,
              multi-stage verification) and patch design.
          - id: DeterministicTODOPlan
            description: Enumerate files, responsibilities, tests, workflows, memory segments.
          - id: PlanApproval
            description: Require explicit approval before implementation (scope lock).
      - id: P1
        uid: phase.impl_ci
        name: ImplementationAndCI
        steps:
          - Implement code per TODO
          - Add tests and CI workflows
          - Validate against invariants

  files_schema:
    # Contract for mapping stages to concrete files
    file_fields:
      - path: string
        uid: string
        role: string            # schema | stage_impl | helper | integration | api_surface
        implements_stage: string|null
        implements_entities: [string]|null
        guarantees: [string]
        tests_required: [string]

  observability_schema:
    metrics:
      - id: string
        source_segment: string
        description: string
    logs:
      expectations:
        - id: string
          description: string

  validation_schema:
    invariants:
      - id: string
        description: string
        type: string            # cross_segment | in_stage | file_contract
        query: string           # abstract query/DSL
    ci_assertions:
      - id: string
        description: string
        check: string           # abstract check/DSL

  lifecycle_schema:
    versioning:
      current_version: int
      change_policies:
        - breaking_change_requires: string   # e.g., new_version
        - minor_change_requires: string      # e.g., review.frontier_comparison
    migration:
      from_versions: [int]
      steps: [string]
