spec_kind: agentic_pipeline_pattern

pattern:
  description: >
    Generic pattern for multi-stage, agentic pipelines with risk-based approval,
    governed memory, and CI/PR integration. This section is reusable across L9 subsystems.

  stage_interface:
    fields:
      id: {type: string}
      uid: {type: string}
      name: {type: string}
      role: {type: string}          # e.g., CoderAgent, QAAgent, RiskEngine, GitWorker
      input_contract:
        - name: string
          type: string
          required: bool
      output_contract:
        - name: string
          type: string
          required: bool
      preconditions:                # logical predicates on inputs or prior stages
        - string
      postconditions:               # guarantees this stage must uphold
        - string
      memory_interactions:
        reads:
          - segment: string
            predicate: string
        writes:
          - segment: string
            packet_type: string
      external_calls:
        - system: string            # e.g., LLM, GitHub, DB, Tool
          contract: string          # summary of expected request/response

  risk_model_schema:
    levels:
      - id: string                 # low, medium, high
        approval_level: string     # auto_qa, auto_architect, manual_human
        conditions:                # predicates on verification outputs
          - string
    scoring:
      inputs:
        - string                   # e.g., VerificationReport.passed
      rules:
        - string                   # declarative English or DSL
      mapping:
        - string                   # score→level rules

  memory_schema:
    segment_fields:
      - name: string
        immutable: bool
        max_age_days: int
        packet_types: [string]
        search_strategy: string    # vector | structured | hybrid
        invariants:
          - string

  github_integration_schema:
    workflows_fields:
      - path: string
        triggers: [string]
        jobs: [string]
    branch_protection_fields:
      branch: string
      required_status_checks: [string]
      require_reviews:
        min_approvals: int
      disallow: [string]

  validation_schema:
    invariants:
      - id: string
        description: string
        type: string                # cross_segment | in_stage | file_contract
        query: string               # DSL or pseudo-query
    ci_assertions:
      - id: string
        description: string
        check: string               # DSL for automated checks

instance:
  metadata:
    name: L9 Code Mutation & GitHub Integration
    uid: subsystem.code_mutation.github
    version: 1
    domain: code_mutation
    criticality: high
    agents:
      - coder
      - qa
      - architect
      - human_cto
    parameters:
      repo_url: ${env:REPO_URL}
      default_branch: ${env:DEFAULT_BRANCH:main}
      l9_api_base_url: ${secret:L9_API_BASE_URL}
      github_token: ${secret:GITHUB_TOKEN}

  goals:
    - uid: goal.safe_agentic_mutation
      name: SafeAgenticCodeMutation
      description: >
        Allow coding agents to generate and apply code changes without direct IDE
        or main-branch access, via sandboxed repos and Git-based workflows.
    - uid: goal.risk_based_approval
      name: RiskBasedApprovalGovernance
      description: >
        Classify changes into risk tiers and map to approvals (QA, Architect, Human).
    - uid: goal.github_integration_as_code
      name: GitHubIntegrationAsCode
      description: >
        Encode triggers, checks, and auto-merge logic as GitHub Actions and branch-protection rules.
    - uid: goal.memory_governed_artifacts
      name: MemoryGovernedArtifacts
      description: >
        Persist every stage artifact in structured memory segments for audit and analysis.
    - uid: goal.frontier_parity_design
      name: FrontierParityDesign
      description: >
        Compare design and TODO plan against frontier AI lab patterns and integrate improvements.

  phases:
    - id: P0
      uid: phase.design_scope_lock
      name: DesignAndScopeLock
      description: >
        Produce and validate a deterministic TODO plan, enriched by a frontier-lab
        comparison step, before any repo code is written.
      steps:
        - id: P0.1
          name: RequirementsElicitation
          actions:
            - Extract safety, approval, and integration requirements from user prompts.
            - Identify constraints on Git/GitHub, memory, and agents.
        - id: P0.2
          name: PipelineArchitectureDraft
          actions:
            - Draft stages: Generation, Verification, Approval, Mutation, CI/PR.
        - id: P0.3
          name: FrontierComparisonLoop
          description: >
            Compare draft architecture with frontier-lab patterns, then patch design.
          checklist:
            - distinct_roles_for_generation_and_review: true
            - defense_in_depth_guardrails:
                - sandbox
                - guardrails
                - branch_protection
                - manual_override
            - multi_stage_verification:
                - static_analysis
                - tests
                - security_scan
          outcomes:
            - must_acknowledge_gaps: true
            - must_record_decisions: true
        - id: P0.4
          name: DeterministicTODOPlan
          actions:
            - Enumerate files, responsibilities, tests, workflows, memory segments.
        - id: P0.5
          name: PlanApproval
          actions:
            - Require explicit user approval before implementation (scope lock).

    - id: P1
      uid: phase.impl_ci
      name: ImplementationAndCI
      description: >
        Implement TODO as Python modules, tests, workflows, and docs respecting
        governance, guardrails, and spec.

  risk_model:
    levels:
      - id: low
        uid: risk.low
        approval_level: auto_qa
        conditions:
          - VerificationReport.passed == true
          - VerificationReport.breaking_changes.has_breaking_changes == false
          - VerificationReport.coverage_pct >= 80
          - VerificationReport.test_results.security_scan.success == true
      - id: medium
        uid: risk.medium
        approval_level: auto_architect
        conditions:
          - risk_score > 10
          - risk_score <= 50
      - id: high
        uid: risk.high
        approval_level: manual_human
        conditions:
          - risk_score > 50
    scoring:
      inputs:
        - VerificationReport.passed
        - VerificationReport.breaking_changes.has_breaking_changes
        - VerificationReport.coverage_pct
        - VerificationReport.test_results.security_scan.success
      rules:
        - if VerificationReport.passed == false then risk_score += 30
        - if VerificationReport.breaking_changes.has_breaking_changes == true then risk_score += 40
        - if VerificationReport.coverage_pct < 80 then risk_score += min(20, (80 - coverage_pct) / 2)
        - if VerificationReport.test_results.security_scan.success == false then risk_score += 25
      mapping:
        - if risk_score <= 10 then approval_level = auto_qa
        - if 10 < risk_score <= 50 then approval_level = auto_architect
        - if risk_score > 50 then approval_level = manual_human
      range: [0,100]

  pipeline:
    stages:
      - id: S1
        uid: stage.code_mutation.generation
        name: Generation
        role: CoderAgent
        goals_ref:
          - goal.safe_agentic_mutation
          - goal.memory_governed_artifacts
        component: l9/core/code_mutation/generation.py
        input_contract:
          - {name: task_id, type: str, required: true}
          - {name: bug_description, type: str, required: true}
          - {name: target_files, type: list[str], required: true}
        output_contract:
          - {name: GenerationResult, type: entity.GenerationResult, required: true}
        preconditions:
          - repo_url is reachable
        postconditions:
          - GenerationResult persisted in generation_artifacts
        memory_interactions:
          reads: []
          writes:
            - segment: generation_artifacts
              packet_type: code_generation
        external_calls:
          - system: LLM
            contract: generate_fix_plan(bug_description, file_contents) -> fix_plan

      - id: S2
        uid: stage.code_mutation.verification
        name: Verification
        role: QAAgent
        goals_ref:
          - goal.safe_agentic_mutation
          - goal.memory_governed_artifacts
        component: l9/core/code_mutation/verification.py
        input_contract:
          - {name: generation_payload, type: dict, required: true}
        output_contract:
          - {name: VerificationReport, type: entity.VerificationReport, required: true}
        preconditions:
          - GenerationResult exists for task_id
        postconditions:
          - VerificationReport persisted in generation_artifacts
        memory_interactions:
          reads:
            - segment: generation_artifacts
              predicate: type == code_generation AND task_id == $task_id
          writes:
            - segment: generation_artifacts
              packet_type: verification_report
        external_calls:
          - system: local_sandbox
            contract: pytest, ruff, mypy, bandit, coverage

      - id: S3
        uid: stage.code_mutation.approval
        name: Approval
        role: RiskEngine+Architect+Human
        goals_ref:
          - goal.risk_based_approval
          - goal.frontier_parity_design
        component: l9/core/code_mutation/approval.py
        input_contract:
          - {name: VerificationReport, type: entity.VerificationReport, required: true}
        output_contract:
          - {name: ApprovalRequirement, type: entity.ApprovalRequirement, required: true}
          - {name: ApprovalResult, type: entity.ApprovalResult, required: true}
        preconditions:
          - VerificationReport exists for task_id
        postconditions:
          - ApprovalRequirement and ApprovalResult persisted
        memory_interactions:
          reads:
            - segment: generation_artifacts
              predicate: type == verification_report AND task_id == $task_id
          writes:
            - {segment: generation_artifacts, packet_type: approval_requirement}
            - {segment: generation_artifacts, packet_type: approval_decision}
        external_calls:
          - system: ArchitectAgent(optional)
            contract: review(VerificationReport, ApprovalRequirement) -> decision

      - id: S4
        uid: stage.code_mutation.mutation
        name: Mutation
        role: GitWorker
        goals_ref:
          - goal.safe_agentic_mutation
          - goal.github_integration_as_code
        component: l9/core/code_mutation/mutations.py
        input_contract:
          - {name: GenerationResult, type: entity.GenerationResult, required: true}
          - {name: ApprovalResult, type: entity.ApprovalResult, required: true}
        output_contract:
          - {name: MutationResult, type: entity.MutationResult, required: true}
        preconditions:
          - ApprovalResult.approved == true
        postconditions:
          - MutationResult persisted in code_mutations
          - PR created on GitHub (success case)
        memory_interactions:
          reads:
            - segment: generation_artifacts
              predicate: type == approval_decision AND task_id == $task_id
          writes:
            - segment: code_mutations
              packet_type: mutation_applied|mutation_failed
        external_calls:
          - system: guardrails
            contract: validate_changes(generated_code)
          - system: git
            contract: clone, checkout, add, commit, push
          - system: github
            contract: create_pull_request(branch_name, title, body)

      - id: S5
        uid: stage.code_mutation.github_ci
        name: GitHubCIAndAutoMerge
        role: GitHubActions+L9
        goals_ref:
          - goal.github_integration_as_code
          - goal.risk_based_approval
        component: l9/integration/github_integration.py
        input_contract:
          - {name: GitHub events, type: webhook/workflow_run, required: true}
        output_contract:
          - {name: auto_merge_decision, type: str, required: false}
        preconditions:
          - Branch protection configured
          - L9 API reachable
        postconditions:
          - Low-risk PRs auto-merged after checks
        memory_interactions:
          reads:
            - segment: generation_artifacts
              predicate: type == approval_decision AND task_id == $task_id
          writes: []
        external_calls:
          - system: L9_API
            contract: GET /api/v1/pr/{pr_number}/approval-level -> {approval_level}
          - system: GitHub
            contract: merge_pull_request(pr_number, method=squash)

  memory:
    segments:
      - name: generation_artifacts
        uid: segment.generation_artifacts
        immutable: true
        max_age_days: 30
        packet_types:
          - code_generation
          - verification_report
          - approval_requirement
          - approval_decision
        search_strategy: vector
        invariants:
          - For any task_id, there may be multiple code_generation and verification_report,
            but approval_decision must reflect the latest requirement.
      - name: code_mutations
        uid: segment.code_mutations
        immutable: true
        max_age_days: 90
        packet_types:
          - mutation_applied
          - mutation_failed
        search_strategy: structured
        invariants:
          - For a given task_id + commit_sha, at most one mutation_applied.

  files:
    - path: l9/schemas/code_mutation.py
      uid: file.schemas.code_mutation
      role: schema
      implements_entities:
        - GenerationResult
        - VerificationReport
        - ApprovalRequirement
        - ApprovalResult
        - MutationResult
      guarantees:
        - enums_validated
        - total_checks_positive
      tests_required:
        - tests/unit/test_code_mutation_schemas.py

    - path: l9/core/code_mutation/sandbox.py
      uid: file.core.code_mutation.sandbox
      role: helper
      implements_stage: null
      guarantees:
        - commands_time_bounded
        - sandbox_cleanup_on_exit
      tests_required:
        - tests/unit/test_sandbox.py

    - path: l9/core/code_mutation/generation.py
      uid: file.core.code_mutation.generation
      role: stage_impl
      implements_stage: stage.code_mutation.generation
      guarantees:
        - never_mutates_real_repo
        - always_persists_GenerationResult
      tests_required:
        - tests/unit/test_generation.py

    - path: l9/core/code_mutation/verification.py
      uid: file.core.code_mutation.verification
      role: stage_impl
      implements_stage: stage.code_mutation.verification
      guarantees:
        - runs_all_configured_checks
        - persists_VerificationReport
      tests_required:
        - tests/unit/test_verification.py

    - path: l9/core/code_mutation/approval.py
      uid: file.core.code_mutation.approval
      role: stage_impl
      implements_stage: stage.code_mutation.approval
      guarantees:
        - risk_scoring_deterministic
        - approval_levels_match_risk_model
      tests_required:
        - tests/unit/test_approval_workflow.py

    - path: l9/core/code_mutation/guardrails.py
      uid: file.core.code_mutation.guardrails
      role: safety
      implements_stage: null
      guarantees:
        - protected_files_blocked
        - forbidden_patterns_blocked
      tests_required:
        - tests/unit/test_guardrails.py

    - path: l9/core/code_mutation/mutations.py
      uid: file.core.code_mutation.mutations
      role: stage_impl
      implements_stage: stage.code_mutation.mutation
      guarantees:
        - guardrails_run_before_git_operations
        - approval_required_before_mutation
      tests_required:
        - tests/integration/test_mutations.py

    - path: l9/integration/github_integration.py
      uid: file.integration.github_integration
      role: integration
      implements_stage: stage.code_mutation.github_ci
      guarantees:
        - auto_merge_only_when_approved_and_checks_passed
      tests_required:
        - tests/integration/test_github_integration.py

    - path: l9/api/routes/code_mutation.py
      uid: file.api.routes.code_mutation
      role: api_surface
      implements_stage: null
      guarantees:
        - validates_inputs
        - wires_to_stages_correctly
      tests_required:
        - tests/integration/test_code_mutation_routes.py

  github_integration:
    workflows:
      - path: .github/workflows/l9-auto-generation.yml
        uid: ghwf.auto_generation
        triggers:
          - issues.labeled == auto-fix
        jobs:
          - call_l9_coder_agent
      - path: .github/workflows/l9-pr-checks.yml
        uid: ghwf.pr_checks
        triggers:
          - pull_request
          - push(main)
        jobs:
          - unit-tests
          - lint-and-types
          - integration-tests
      - path: .github/workflows/l9-auto-merge.yml
        uid: ghwf.auto_merge
        triggers:
          - workflow_run(L9 PR Checks).conclusion == success
        jobs:
          - evaluate-and-merge

    branch_protection:
      branch: main
      required_status_checks:
        - "L9 PR Checks / unit-tests"
        - "L9 PR Checks / lint-and-types"
        - "L9 PR Checks / integration-tests"
      require_reviews:
        min_approvals: 1
        for_high_risk_only: true
      disallow:
        - direct_pushes
        - force_pushes

  observability:
    metrics:
      - id: metric.generation.success_rate
        source_segment: generation_artifacts
        description: Fraction of GenerationResults with test_result.success == true
      - id: metric.mutation.success_rate
        source_segment: code_mutations
        description: Fraction of MutationResult.success == true
      - id: metric.approval.risk_distribution
        source_segment: generation_artifacts
        description: Distribution of ApprovalRequirement.risk_score and approval_level
    logs:
      expectations:
        - id: log.stage_transitions
          description: Log entering/exiting each stage with task_id and outcome

  validation:
    invariants:
      - id: inv.no_mutation_without_approval
        description: No mutation_applied without prior approved approval_decision
        type: cross_segment
        query: >
          FOR EACH packet IN code_mutations WHERE type == "mutation_applied":
            REQUIRE EXISTS packet2 IN generation_artifacts
              WHERE packet2.type == "approval_decision"
                AND packet2.task_id == packet.task_id
                AND packet2.approval_result.approved == true
      - id: inv.high_risk_not_auto_merged
        description: High-risk changes must not be auto-merged
        type: in_stage
        query: >
          FOR EACH PR auto-merged:
            REQUIRE latest ApprovalRequirement.risk_score <= 50
    ci_assertions:
      - id: ci.each_stage_has_tests
        description: Each pipeline stage must have at least one test file
        check: >
          FOR EACH stage IN pipeline.stages:
            REQUIRE EXISTS file IN files
              WHERE file.implements_stage == stage.uid
                AND file.tests_required IS NOT EMPTY

  lifecycle:
    versioning:
      current_version: 1
      change_policies:
        - breaking_change_requires: new_version
        - minor_change_requires: review.frontier_comparison
    migration:
      from_versions: [0]
      steps:
        - ensure_new_memory_segments_created
        - backfill_task_id_pr_links
        - update_branch_protection_with_new_checks

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | TOO-OPER-011 |
| **Component Name** | Agentic Pipeline Pattern.V1.0 |
| **Module Version** | 1.0.0 |
| **Created At** | 2026-01-08T03:17:26Z |
| **Created By** | L9_DORA_Injector |
| **Layer** | operations |
| **Domain** | tools |
| **Type** | schema |
| **Status** | active |
| **Governance Level** | medium |
| **Compliance Required** | True |
| **Audit Trail** | True |
| **Purpose** | Documentation for agentic pipeline pattern.v1.0 |

---
