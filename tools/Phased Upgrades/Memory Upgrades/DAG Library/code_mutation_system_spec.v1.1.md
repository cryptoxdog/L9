code_mutation_system_spec:
  version: 1
  scope:
    name: L9 Code Mutation & GitHub Integration
    phase: 0
    objective: >
      Design and implement a multi-stage, agentic code-mutation pipeline with
      Git+GitHub integration, risk-based approvals, and governed memory, using
      a frontier-lab comparison loop before finalizing the Phase 0 TODO.

  goals:
    - id: G1
      name: SafeAgenticCodeMutation
      description: >
        Allow coding agents to generate and apply code changes without direct IDE
        or main-branch access, via sandboxed repos and Git-based workflows.
    - id: G2
      name: RiskBasedApprovalGovernance
      description: >
        Classify changes into risk tiers (low, medium, high) and map to
        appropriate approvals (QA, Architect, Human).
    - id: G3
      name: GitHubIntegrationAsCode
      description: >
        Encode triggers, checks, and auto-merge logic as GitHub Actions and
        branch-protection rules, with full PR/commit visibility.
    - id: G4
      name:MemoryGovernedArtifacts
      description: >
        Persist every stage artifact (generation, verification, approval,
        mutation) in structured memory segments for audit and analysis.
    - id: G5
      name: FrontierParityDesign
      description: >
        Compare design and TODO plan against patterns used by frontier AI labs
        and incorporate improvements before Phase 0 is finalized.

  phases:
    - id: P0
      name: DesignAndScopeLock
      description: >
        Produce and validate a deterministic TODO plan, enriched by a
        frontier-lab comparison step, before any repo code is written.
      steps:
        - id: P0.1
          name: RequirementsElicitation
          actions:
            - Analyze user prompts about how agents modify repos, approvals, and GitHub.
            - Extract constraints on safety, approvals, and integration.
        - id: P0.2
          name: PipelineArchitectureDraft
          actions:
            - Design multi-stage pipeline:
              - Generation (Coder)
              - Verification (QA)
              - Approval (Risk engine)
              - Mutation (Git worker)
              - CI/PR integration
        - id: P0.3
          name: FrontierComparisonLoop
          description: >
            Compare the draft pipeline and TODO plan with frontier-lab patterns
            (e.g., dedicated code reviewer agents, multi-stage verification,
            ReAct-style reasoning, defense-in-depth guardrails).[web:297][web:304][web:309]
          actions:
            - Benchmark design against:
              - Dedicated AI review agents with repo-wide tools.[web:297]
              - Multi-agent, staged pipelines (generator + reviewer).[web:281][web:293]
              - Defense-in-depth and guardrail practices.[web:304][web:307]
            - Identify deltas:
              - Missing review layers
              - Insufficient observability or evals
              - Weak guardrails or auth
            - Apply improvements:
              - Ensure clear separation between generator, QA, approval.
              - Add guardrails and memory governance as first-class citizens.
              - Reserve human control for high-risk paths.
        - id: P0.4
          name: DeterministicTODOPlan
          actions:
            - Produce file-level TODO (paths, responsibilities, imports, tests).
            - Include memory segments, GitHub workflows, and docs.
        - id: P0.5
          name: PlanApproval
          actions:
            - Wait for explicit user approval of TODO.
            - Lock scope before implementation (no unapproved files added).

    - id: P1
      name: ImplementationAndCI
      description: >
        Implement the Phase 0 TODO plan into concrete code artifacts (Python
        modules, workflows, README) respecting governance and guardrails.

  risk_model:
    levels:
      - id: low
        name: LowRisk
        conditions:
          - verification_passed == true
          - breaking_changes == false
          - coverage_pct >= 80
          - security_scan_success == true
        approval_level: auto_qa
      - id: medium
        name: MediumRisk
        conditions:
          - risk_score in (10,50]
        approval_level: auto_architect
      - id: high
        name: HighRisk
        conditions:
          - risk_score > 50
        approval_level: manual_human
    scoring:
      inputs:
        - source: VerificationReport.passed
        - source: VerificationReport.breaking_changes.has_breaking_changes
        - source: VerificationReport.coverage_pct
        - source: VerificationReport.test_results.security_scan.success
      rules:
        - if not passed: add 30
        - if has_breaking_changes: add 40
        - if coverage_pct < 80: add min(20, (80 - coverage_pct) / 2)
        - if security_scan_failure: add 25
      output:
        risk_score_range: [0,100]
        mapping:
          - score <= 10 -> auto_qa
          - 10 < score <= 50 -> auto_architect
          - score > 50 -> manual_human

  pipeline:
    stages:
      - id: S1
        name: Generation
        role: CoderAgent
        component: l9/core/code_mutation/generation.py
        input:
          - task_id
          - bug_description
          - target_files[]
        tools:
          - sandbox: CodeSandboxEnvironment
          - llm: LLMClientProtocol.generate_fix_plan
        output: GenerationResult
        memory_write:
          segment: generation_artifacts
          packet_type: code_generation
        guarantees:
          - Real repo never mutated in this stage.
          - All outcomes (success/failure) persisted.

      - id: S2
        name: Verification
        role: QAAgent
        component: l9/core/code_mutation/verification.py
        input: GenerationResult
        checks:
          - unit_tests
          - integration_tests
          - static_analysis (ruff, mypy)
          - security_scan (bandit)
          - coverage
          - breaking_changes_analysis
        output: VerificationReport
        memory_write:
          segment: generation_artifacts
          packet_type: verification_report
        guarantees:
          - test_results and breaking_changes fully recorded.
          - sandbox errors yield failing, logged report.

      - id: S3
        name: Approval
        role: RiskEngine + Architect + Human
        component: l9/core/code_mutation/approval.py
        input: VerificationReport
        sub_stages:
          - compute_ApprovalRequirement (risk_score + approval_level)
          - compute_ApprovalResult (execute_approval based on level)
        outputs:
          - ApprovalRequirement
          - ApprovalResult
        memory_write:
          - segment: generation_artifacts
            packet_type: approval_requirement
          - segment: generation_artifacts
            packet_type: approval_decision
        guarantees:
          - No mutation may proceed without ApprovalResult.approved == true.
          - HighRisk always requires manual_human path.

      - id: S4
        name: Mutation
        role: GitWorker
        component: l9/core/code_mutation/mutations.py
        preconditions:
          - ApprovalResult.approved == true
        guardrails:
          component: l9/core/code_mutation/guardrails.py
          checks:
            - protected_files_not_modified
            - file_size_limits
            - forbidden_code_patterns_absent
        actions:
          - clone_real_repo_to_temp
          - create_feature_branch (auto/fix-{task_id}-{suffix})
          - apply_generated_code
          - git_add_commit_push
          - create_draft_pr (via gh CLI or REST)
        output: MutationResult
        memory_write:
          segment: code_mutations
          packet_type:
            - mutation_applied if success
            - mutation_failed if not
        guarantees:
          - Protected files and dangerous patterns blocked.
          - All attempts logged (success or failure).

      - id: S5
        name: GitHubCIAndAutoMerge
        role: GitHubActions + L9
        components:
          - .github/workflows/l9-auto-generation.yml
          - .github/workflows/l9-pr-checks.yml
          - .github/workflows/l9-auto-merge.yml
          - l9/integration/github_integration.py
        flows:
          - issue_labeled_auto_fix -> call Coder endpoint
          - PR_opened/updated -> run tests/lint/security
          - workflow_run_success -> query L9 approval-level -> auto-merge if auto_qa
        guarantees:
          - All merges gated by required checks + approval level.
          - PR history is source of truth for repo changes.

  memory:
    segments:
      - name: generation_artifacts
        immutable: true
        max_age_days: 30
        search_strategy: vector
        packet_types:
          - code_generation
          - verification_report
          - approval_requirement
          - approval_decision
      - name: code_mutations
        immutable: true
        max_age_days: 90
        search_strategy: structured
        packet_types:
          - mutation_applied
          - mutation_failed
    lifecycle:
      by_task:
        description: Reconstruct full lifecycle for task_id.
        steps:
          - fetch all packets from generation_artifacts with task_id
          - fetch all packets from code_mutations with task_id
          - order by created_at
      by_pr:
        description: Determine approval_level for PR.
        prerequisites:
          - task_id encoded in commit or PR body
        steps:
          - derive task_id from PR metadata
          - apply by_task lifecycle

  github_integration:
    workflows:
      - path: .github/workflows/l9-auto-generation.yml
        triggers:
          - issues.labeled == auto-fix
        actions:
          - call L9 /agent/coder/generate with issue id, title, body
      - path: .github/workflows/l9-pr-checks.yml
        triggers:
          - pull_request (opened, synchronize, reopened)
          - push to main
        jobs:
          - unit-tests
          - lint-and-types
          - integration-tests
      - path: .github/workflows/l9-auto-merge.yml
        triggers:
          - workflow_run of "L9 PR Checks" with conclusion == success
        actions:
          - resolve PR number
          - call L9 /pr/{pr_number}/approval-level
          - if approval_level == auto_qa -> auto-merge via action/api
    branch_protection:
      branch: main
      required_status_checks:
        - L9 PR Checks / unit-tests
        - L9 PR Checks / lint-and-types
        - L9 PR Checks / integration-tests
      require_reviews:
        min_approvals: 1
        for_high_risk_only: true
      disallow:
        - direct_pushes
        - force_pushes

  governance_and_checks:
    invariants:
      - No mutation_applied if there is no approval_decision with approved == true for same task_id.
      - HighRisk changes must never be auto_merged.
      - All stages must write to their designated memory segments.
      - Guardrails must run before any real repo mutation.
    frontier_comparison_checks:
      - Ensure separate generator and reviewer agents with distinct roles.[web:297][web:299]
      - Ensure defense-in-depth guardrails (sandbox + guardrails + branch protection + human override).[web:304][web:307]
      - Ensure evaluation/verification at each pipeline stage, not just CI.[web:297][web:309]
    open_gaps:
      - PR <-> task_id linking format (e.g., standardized footers).
      - Authentication/authorization for L9 API routes.
      - Richer breaking-change detection (contracts / LLM reviewer).
      - Telemetry and dashboards for agent performance and risk distribution.
