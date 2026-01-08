code_mutation_memory_spec:
  goals:
    - id: M1
      name: FullAuditability
      summary: Persist every agentic code-change artifact as structured records.
    - id: M2
      name: ClearDataContracts
      summary: Use typed schemas and segments to separate proposal, verification, approval, mutation.
    - id: M3
      name: SegmentGovernance
      summary: Enforce governance via immutable memory segments with strict packet types and retention.

  entities:
    GenerationResult:
      purpose: Canonical record of Coder output from sandbox.
      fields:
        task_id: {type: str, required: true, description: External task/issue id}
        sandbox_id: {type: str, required: true, description: Sandbox instance id}
        generated_code:
          type: dict[str,str]
          required: true
          description: Map of file_path -> full new file contents
        explanation:
          type: str
          required: true
          description: Why the change was made and what it does
        breaking_changes:
          type: bool
          required: true
          default: false
          description: Self-assessed breaking-change flag
        tests_needed:
          type: list[str]
          required: true
          default: []
          description: Tests that should be added/updated
        git_diff:
          type: str
          required: true
          description: Unified diff for proposed changes
        test_result:
          type: dict[str,any]
          required: true
          default: {}
          description: Smoke test result (success, stdout, stderr, exit_code)
        created_at:
          type: datetime
          required: true
          default: now_utc
      invariants:
        - generated_code may be empty only on sandbox error
        - task_id must be stable across all stages for the same change

    VerificationReport:
      purpose: QA assessment of a GenerationResult.
      fields:
        task_id: {type: str, required: true}
        passed: {type: bool, required: true}
        passed_checks: {type: int, required: true, description: Number of checks that passed}
        total_checks: {type: int, required: true, description: Total checks run}
        issues:
          type: list[str]
          required: true
          default: []
          description: Blocking problems discovered by QA
        recommendations:
          type: list[str]
          required: true
          default: []
          description: Non-blocking suggestions
        test_results:
          type: dict[str,any]
          required: true
          default: {}
          description: Per-check result payloads (unit/integration/static/security/coverage)
        breaking_changes:
          type: dict[str,any]
          required: true
          default: {}
          description: Breaking-change analysis (has_breaking_changes, details, source)
        created_at:
          type: datetime
          required: true
          default: now_utc
      derived:
        coverage_pct:
          type: float|null
          source: test_results.coverage.coverage_pct
      invariants:
        - total_checks > 0
        - passed implies len(issues) == 0

    ApprovalRequirement:
      purpose: Risk-scored requirement for approval level.
      fields:
        risk_score:
          type: int
          required: true
          range: [0,100]
          description: Overall risk (higher == riskier)
        approval_level:
          type: enum
          required: true
          allowed: [auto_qa, auto_architect, manual_human]
        reasons:
          type: list[str]
          required: true
          default: []
          description: Human-readable rationale for risk/level
      invariants:
        - approval_level ∈ {auto_qa, auto_architect, manual_human}

    ApprovalResult:
      purpose: Concrete approval decision before mutation.
      fields:
        approved: {type: bool, required: true}
        approved_by:
          type: str|null
          required: false
          description: Logical approver id (QA_Agent, Architect_Agent, human id)
        approval_type:
          type: enum
          required: true
          allowed: [automatic, semi_automatic, manual_pending, manual_final]
        message:
          type: str|null
          required: false
          description: Short message for logs/audit
        timestamp:
          type: datetime
          required: true
          default: now_utc
        review_notes:
          type: str|null
          required: false
          description: Extended review notes
      invariants:
        - approved == true implies approval_type in [automatic, semi_automatic, manual_final]

    MutationResult:
      purpose: Record of a repository mutation attempt.
      fields:
        task_id: {type: str, required: true}
        success: {type: bool, required: true}
        branch_name: {type: str|null, required: false}
        commit_sha: {type: str|null, required: false}
        pr_number: {type: int|null, required: false}
        pr_url: {type: str|null, required: false}
        error:
          type: str|null
          required: false
          description: Error string if success == false
        created_at:
          type: datetime
          required: true
          default: now_utc
      invariants:
        - success == true implies commit_sha != null and branch_name != null

  segments:
    generation_artifacts:
      purpose: Store all pre-mutation artifacts (generation, verification, approval).
      immutable: true
      max_packet_age_days: 30
      scope: global
      required_authority_level: 0
      write_authority_level: 1
      search_strategy: vector
      packet_types_allowed:
        - code_generation       # payload: GenerationResult
        - verification_report   # payload: VerificationReport
        - approval_requirement  # payload: ApprovalRequirement
        - approval_decision     # payload: ApprovalResult
      usage:
        writes:
          - stage: generation
            type: code_generation
            payload:
              task_id: GenerationResult.task_id
              generation: GenerationResult.json
          - stage: verification
            type: verification_report
            payload:
              task_id: VerificationReport.task_id
              report: VerificationReport.json
          - stage: approval_requirement
            type: approval_requirement
            payload:
              task_id: ApprovalRequirement.task_id (via VerificationReport.task_id)
              requirement: ApprovalRequirement.dict
          - stage: approval_decision
            type: approval_decision
            payload:
              task_id: ApprovalResult.task_id
              approval_result: ApprovalResult.dict
        reads:
          - pattern: ByTask
            key: task_id
            goal: Reconstruct generation→verification→approval timeline
      invariants:
        - Every mutation_applied in code_mutations must have at least one prior code_generation, verification_report, approval_decision for same task_id.

    code_mutations:
      purpose: Store effects of mutations against real repo.
      immutable: true
      max_packet_age_days: 90
      scope: global
      required_authority_level: 0
      write_authority_level: 1
      search_strategy: structured
      packet_types_allowed:
        - mutation_applied  # payload: MutationResult (success true)
        - mutation_failed   # payload: MutationResult (success false)
      usage:
        writes:
          - stage: mutation
            type: mutation_applied
            condition: MutationResult.success == true
            payload:
              task_id: MutationResult.task_id
              mutation: MutationResult.json
          - stage: mutation
            type: mutation_failed
            condition: MutationResult.success == false
            payload:
              task_id: MutationResult.task_id
              mutation: MutationResult.json
        reads:
          - pattern: ByTask
            key: task_id
            goal: See branch/commit/PR for a given task
          - pattern: Reporting
            goal: Count failures, success rate, time-to-merge
      invariants:
        - For any task_id, there may be multiple mutation_failed but at most one terminal mutation_applied for a given commit_sha.

  write_paths:
    generation_stage:
      component: CoderAgentCodeGeneration._persist_generation
      segment: generation_artifacts
      packet_type: code_generation
      payload_shape:
        type: code_generation
        task_id: string
        generation: GenerationResult.json
      must_have:
        - Write on both success and sandbox error
        - task_id must match external issue id

    verification_stage:
      component: QAAgentVerification._persist_verification
      segment: generation_artifacts
      packet_type: verification_report
      payload_shape:
        type: verification_report
        task_id: string
        report: VerificationReport.json
      must_have:
        - Include full test_results and breaking_changes

    approval_stage:
      component_requirement: ApprovalWorkflow._persist_requirement
      segment_requirement: generation_artifacts
      packet_type_requirement: approval_requirement
      payload_requirement:
        type: approval_requirement
        task_id: string
        requirement: ApprovalRequirement.dict
      component_result: ApprovalWorkflow._persist_result
      segment_result: generation_artifacts
      packet_type_result: approval_decision
      payload_result:
        type: approval_decision
        task_id: string
        approval_result: ApprovalResult.dict
      must_have:
        - Never skip writing requirement or decision
        - approval_decision must be written before any mutation_applied

    mutation_stage:
      component: GitMutationWorker._persist_mutation
      segment: code_mutations
      packet_type_success: mutation_applied
      packet_type_failure: mutation_failed
      payload_shape:
        type: mutation_applied|mutation_failed
        task_id: string
        mutation: MutationResult.json
      must_have:
        - Always write a record regardless of success
        - On success, ensure branch_name, commit_sha, pr_url are present

  read_patterns:
    by_task:
      description: Reconstruct full lifecycle for a given task_id.
      steps:
        - query generation_artifacts where payload.task_id == task_id
        - sort by created_at
        - query code_mutations where payload.task_id == task_id
      outputs:
        - generation_chain: [GenerationResult*]
        - verification_chain: [VerificationReport*]
        - approval_chain: [ApprovalRequirement*, ApprovalResult*]
        - mutation_chain: [MutationResult*]

    by_pr:
      description: Determine approval_level and history for a PR.
      prerequisites:
        - task_id must be encoded in commit message or PR body
      steps:
        - extract task_id from PR metadata
        - apply by_task pattern
      outputs:
        - approval_level: from latest ApprovalRequirement.approval_level
        - risk_score: from latest ApprovalRequirement.risk_score
        - decision: latest ApprovalResult

  governance:
    invariants_global:
      - Each stage must write to its designated segment; no side segments.
      - Segments are immutable; updates are append-only.
      - High-risk changes should have approval_level == manual_human until manual_final ApprovalResult is written.
      - No mutation_applied is permitted without an approval_decision with approved == true.
    checks_and_gap_analysis:
      must_have_checks:
        - Ensure segments enforce packet_types_allowed at substrate level.
        - Ensure ApprovalRequirement/ApprovalResult enums are validated.
        - Ensure mutation_applied writes only occur when ApprovalResult.approved == true.
        - Ensure all errors (sandbox, guardrails, git) produce mutation_failed entries.
      gaps:
        - No explicit index mapping pr_number <-> task_id (should add link records).
        - No schema-level storage of diff statistics or affected paths (could add to GenerationResult or MutationResult).
        - No built-in authz around who can read/write segments (relies on substrate-level policies).
        - No dedicated telemetry segment for metrics (success/failure counts, TTM).

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | TOO-OPER-013 |
| **Component Name** | Code Mutation System Spec.V1.0 |
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
| **Purpose** | Documentation for code mutation system spec.v1.0 |

---
