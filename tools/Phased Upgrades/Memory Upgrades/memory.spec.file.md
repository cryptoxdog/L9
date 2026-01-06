l9_memory_governance_pattern:
  version: 1
  spec_kind: memory_pattern

  description: >
    Canonical pattern for L9 memory governance: how to structure segments,
    entities, packet types, and invariants for any agentic subsystem.
    This is reusable across all L9 subsystems (code mutation, tools, auth, memory, etc.).

  pattern:
    goals:
      - name: FullAuditability
        description: Persist every artifact as structured, immutable records.
      - name: ClearDataContracts
        description: Use typed entities and packet types to separate concerns.
      - name: SegmentGovernance
        description: Enforce governance via immutable segments, retention, and search strategy.

    entity_interface:
      fields:
        uid: string               # e.g., entity.GenerationResult
        name: string
        purpose: string
        fields:                   # schema definition
          - name: string
            type: string
            required: bool
            default: any
            description: string
        derived:                  # computed fields
          - name: string
            type: string
            source: string        # e.g., test_results.coverage.coverage_pct
        invariants: [string]      # must-hold predicates

    segment_interface:
      fields:
        uid: string               # e.g., segment.generation_artifacts
        name: string
        purpose: string
        immutable: bool
        max_packet_age_days: int
        scope: string             # global | subsystem | user
        required_authority_level: int
        write_authority_level: int
        search_strategy: string   # vector | structured | hybrid
        packet_types_allowed: [string]
        invariants: [string]
        usage:
          writes:
            - stage: string       # which pipeline stage writes this
              packet_type: string
              condition: string   # optional predicate (e.g., success==true)
              payload_shape:      # expected structure
                - field: string
                  type: string
          reads:
            - pattern: string     # e.g., ByTask, ByUser
              key: string         # e.g., task_id
              goal: string        # what this read accomplishes

    write_path_interface:
      fields:
        uid: string               # e.g., writepath.generation_stage
        component: string         # which code component writes (e.g., CoderAgent._persist)
        segment: string           # target segment uid
        packet_type: string       # packet type to write
        payload_shape:            # schema of payload
          - field: string
            type: string
        must_have: [string]       # guarantees this write must uphold

    read_pattern_interface:
      fields:
        uid: string               # e.g., readpat.by_task
        name: string
        description: string
        query: string             # human-readable or DSL query
        output: string            # what results should look like

    invariant_interface:
      fields:
        uid: string
        description: string
        type: string              # cross_segment | in_entity | in_segment | global
        predicate: string         # formal or pseudo-code

instance:
  metadata:
    name: L9 Code Mutation Memory Model
    uid: memory.code_mutation
    subsystem: code_mutation
    version: 1

  goals:
    - id: M1
      uid: goal.full_auditability
      name: FullAuditability
      summary: Persist every agentic code-change artifact as structured records.
    - id: M2
      uid: goal.clear_data_contracts
      name: ClearDataContracts
      summary: Use typed schemas and segments to separate proposal, verification, approval, mutation.
    - id: M3
      uid: goal.segment_governance
      name: SegmentGovernance
      summary: Enforce governance via immutable memory segments with strict packet types and retention.

  entities:
    GenerationResult:
      uid: entity.GenerationResult
      purpose: Canonical record of Coder output from sandbox.
      fields:
        task_id: {type: str, required: true, description: "External task/issue id"}
        sandbox_id: {type: str, required: true, description: "Sandbox instance id"}
        generated_code:
          type: dict[str,str]
          required: true
          description: "Map of file_path -> full new file contents"
        explanation:
          type: str
          required: true
          description: "Why the change was made and what it does"
        breaking_changes:
          type: bool
          required: true
          default: false
          description: "Self-assessed breaking-change flag"
        tests_needed:
          type: list[str]
          required: true
          default: []
          description: "Tests that should be added/updated"
        git_diff:
          type: str
          required: true
          description: "Unified diff for proposed changes"
        test_result:
          type: dict[str,any]
          required: true
          default: {}
          description: "Smoke test result (success, stdout, stderr, exit_code)"
        created_at:
          type: datetime
          required: true
          default: now_utc
      invariants:
        - "generated_code may be empty only on sandbox error"
        - "task_id must be stable across all stages for the same change"

    VerificationReport:
      uid: entity.VerificationReport
      purpose: QA assessment of a GenerationResult.
      fields:
        task_id: {type: str, required: true}
        passed: {type: bool, required: true}
        passed_checks: {type: int, required: true, description: "Number of checks that passed"}
        total_checks: {type: int, required: true, description: "Total checks run"}
        issues:
          type: list[str]
          required: true
          default: []
          description: "Blocking problems discovered by QA"
        recommendations:
          type: list[str]
          required: true
          default: []
          description: "Non-blocking suggestions"
        test_results:
          type: dict[str,any]
          required: true
          default: {}
          description: "Per-check result payloads (unit/integration/static/security/coverage)"
        breaking_changes:
          type: dict[str,any]
          required: true
          default: {}
          description: "Breaking-change analysis (has_breaking_changes, details, source)"
        created_at:
          type: datetime
          required: true
          default: now_utc
      derived:
        coverage_pct:
          type: float|null
          source: test_results.coverage.coverage_pct
      invariants:
        - "total_checks > 0"
        - "passed implies len(issues) == 0"

    ApprovalRequirement:
      uid: entity.ApprovalRequirement
      purpose: Risk-scored requirement for approval level.
      fields:
        risk_score:
          type: int
          required: true
          range: [0,100]
          description: "Overall risk (higher == riskier)"
        approval_level:
          type: enum
          required: true
          allowed: [auto_qa, auto_architect, manual_human]
        reasons:
          type: list[str]
          required: true
          default: []
          description: "Human-readable rationale for risk/level"
      invariants:
        - "approval_level ∈ {auto_qa, auto_architect, manual_human}"

    ApprovalResult:
      uid: entity.ApprovalResult
      purpose: Concrete approval decision before mutation.
      fields:
        approved: {type: bool, required: true}
        approved_by:
          type: str|null
          required: false
          description: "Logical approver id (QA_Agent, Architect_Agent, human id)"
        approval_type:
          type: enum
          required: true
          allowed: [automatic, semi_automatic, manual_pending, manual_final]
        message:
          type: str|null
          required: false
          description: "Short message for logs/audit"
        timestamp:
          type: datetime
          required: true
          default: now_utc
        review_notes:
          type: str|null
          required: false
          description: "Extended review notes"
      invariants:
        - "approved == true implies approval_type in [automatic, semi_automatic, manual_final]"

    MutationResult:
      uid: entity.MutationResult
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
          description: "Error string if success == false"
        created_at:
          type: datetime
          required: true
          default: now_utc
      invariants:
        - "success == true implies commit_sha != null and branch_name != null"

  segments:
    generation_artifacts:
      uid: segment.generation_artifacts
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
            packet_type: code_generation
            payload:
              type: code_generation
              task_id: GenerationResult.task_id
              generation: GenerationResult.json
          - stage: verification
            packet_type: verification_report
            payload:
              type: verification_report
              task_id: VerificationReport.task_id
              report: VerificationReport.json
          - stage: approval
            packet_type: approval_requirement
            payload:
              type: approval_requirement
              task_id: VerificationReport.task_id
              requirement: ApprovalRequirement.dict
          - stage: approval
            packet_type: approval_decision
            payload:
              type: approval_decision
              task_id: ApprovalResult.task_id
              approval_result: ApprovalResult.dict
        reads:
          - pattern: ByTask
            key: task_id
            goal: Reconstruct generation→verification→approval timeline
      invariants:
        - "Every mutation_applied in code_mutations must have at least one prior code_generation, verification_report, approval_decision for same task_id."

    code_mutations:
      uid: segment.code_mutations
      purpose: Store effects of mutations against real repo.
      immutable: true
      max_packet_age_days: 90
      scope: global
      required_authority_level: 0
      write_authority_level: 1
      search_strategy: structured
      packet_types_allowed:
        - mutation_applied   # payload: MutationResult (success true)
        - mutation_failed    # payload: MutationResult (success false)
      usage:
        writes:
          - stage: mutation
            packet_type: mutation_applied
            condition: "MutationResult.success == true"
            payload:
              type: mutation_applied
              task_id: MutationResult.task_id
              mutation: MutationResult.json
          - stage: mutation
            packet_type: mutation_failed
            condition: "MutationResult.success == false"
            payload:
              type: mutation_failed
              task_id: MutationResult.task_id
              mutation: MutationResult.json
        reads:
          - pattern: ByTask
            key: task_id
            goal: See branch/commit/PR for a given task
          - pattern: Reporting
            key: null
            goal: Count failures, success rate, time-to-merge
      invariants:
        - "For any task_id, there may be multiple mutation_failed but at most one terminal mutation_applied for a given commit_sha."

  write_paths:
    generation_stage:
      uid: writepath.generation_stage
      component: CoderAgentCodeGeneration._persist_generation
      segment: segment.generation_artifacts
      packet_type: code_generation
      payload_shape:
        type: code_generation
        task_id: string
        generation: GenerationResult.json
      must_have:
        - "Write on both success and sandbox error"
        - "task_id must match external issue id"

    verification_stage:
      uid: writepath.verification_stage
      component: QAAgentVerification._persist_verification
      segment: segment.generation_artifacts
      packet_type: verification_report
      payload_shape:
        type: verification_report
        task_id: string
        report: VerificationReport.json
      must_have:
        - "Include full test_results and breaking_changes"

    approval_stage:
      uid: writepath.approval_stage
      components:
        - component: ApprovalWorkflow._persist_requirement
          segment: segment.generation_artifacts
          packet_type: approval_requirement
        - component: ApprovalWorkflow._persist_result
          segment: segment.generation_artifacts
          packet_type: approval_decision
      must_have:
        - "Never skip writing requirement or decision"
        - "approval_decision must be written before any mutation_applied"

    mutation_stage:
      uid: writepath.mutation_stage
      component: GitMutationWorker._persist_mutation
      segment: segment.code_mutations
      packet_types:
        - success: mutation_applied
        - failure: mutation_failed
      must_have:
        - "Always write a record regardless of success"
        - "On success, ensure branch_name, commit_sha, pr_url are present"

  read_patterns:
    by_task:
      uid: readpat.by_task
      description: Reconstruct full lifecycle for a given task_id.
      query: >
        SELECT * FROM generation_artifacts WHERE task_id == $task_id
        UNION
        SELECT * FROM code_mutations WHERE task_id == $task_id
        ORDER BY created_at
      outputs:
        - generation_chain: "list[GenerationResult]"
        - verification_chain: "list[VerificationReport]"
        - approval_chain: "list[ApprovalRequirement], list[ApprovalResult]"
        - mutation_chain: "list[MutationResult]"

    by_pr:
      uid: readpat.by_pr
      description: Determine approval_level and history for a PR.
      prerequisites:
        - "task_id must be encoded in commit message or PR body"
      query: >
        EXTRACT task_id FROM PR metadata
        APPLY by_task pattern
      outputs:
        - approval_level: "from latest ApprovalRequirement.approval_level"
        - risk_score: "from latest ApprovalRequirement.risk_score"
        - decision: "latest ApprovalResult"

  invariants:
    global:
      - uid: inv.stage_writes_to_designated_segment
        description: "Each stage must write to its designated segment; no side segments."
        type: global
      - uid: inv.segments_immutable_append_only
        description: "Segments are immutable; updates are append-only."
        type: global
      - uid: inv.high_risk_approval_required
        description: "High-risk changes must have approval_level == manual_human until manual_final ApprovalResult is written."
        type: global
      - uid: inv.no_mutation_without_approval
        description: "No mutation_applied is permitted without an approval_decision with approved == true."
        type: cross_segment

    cross_segment:
      - uid: inv.generation_before_verification
        description: "A VerificationReport requires at least one prior GenerationResult for same task_id."
        type: cross_segment
      - uid: inv.verification_before_approval
        description: "An ApprovalRequirement requires at least one prior VerificationReport for same task_id."
        type: cross_segment
      - uid: inv.approval_before_mutation
        description: "A mutation_applied requires at least one prior ApprovalResult with approved==true for same task_id."
        type: cross_segment

    in_entity:
      - uid: inv.generation_result_consistency
        description: "If breaking_changes==true, explanation must describe the breaking change."
        type: in_entity
      - uid: inv.verification_report_consistency
        description: "passed == false implies len(issues) > 0."
        type: in_entity
      - uid: inv.approval_result_consistency
        description: "approved == false implies approval_type in [manual_pending, manual_final]."
        type: in_entity

    in_segment:
      - uid: inv.generation_artifacts_only_has_proposal_types
        description: "generation_artifacts must only contain code_generation, verification_report, approval_requirement, approval_decision."
        type: in_segment
      - uid: inv.code_mutations_only_has_effect_types
        description: "code_mutations must only contain mutation_applied, mutation_failed."
        type: in_segment

  checks_and_gaps:
    must_have_checks:
      - "Ensure segments enforce packet_types_allowed at substrate level."
      - "Ensure ApprovalRequirement/ApprovalResult enums are validated."
      - "Ensure mutation_applied writes only occur when ApprovalResult.approved == true."
      - "Ensure all errors (sandbox, guardrails, git) produce mutation_failed entries."
      - "Ensure task_id is present and consistent across all packets for a task."

    gaps:
      - uid: gap.pr_task_linkage
        description: "No explicit index mapping pr_number <-> task_id (should add link records)."
        mitigation: "Add a new packet type 'task_pr_link' in generation_artifacts."
      - uid: gap.diff_metadata
        description: "No schema-level storage of diff statistics or affected paths."
        mitigation: "Extend GenerationResult and MutationResult with diff metadata."
      - uid: gap.authz
        description: "No built-in authz around who can read/write segments (relies on substrate-level policies)."
        mitigation: "Add segment-level ACL enforcement in MemorySubstrateService."
      - uid: gap.telemetry
        description: "No dedicated telemetry segment for metrics (success/failure counts, TTM)."
        mitigation: "Create a new 'metrics' segment with packet type 'pipeline_metric'."

  lifecycle:
    versioning:
      current_version: 1
      change_policies:
        - breaking_change_requires: new_version
        - minor_change_requires: review
    migration:
      from_versions: [0]
      steps:
        - "ensure_new_memory_segments_created"
        - "backfill_task_id_pr_links"
        - "update_retention_policies"
