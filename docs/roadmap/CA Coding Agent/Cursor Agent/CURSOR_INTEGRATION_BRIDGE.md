# CURSOR_INTEGRATION_BRIDGE: God-AI-Agent ↔ L Cursor Module
## Technical Binding Layer for Autonomous Code Generation

**Version:** 1.0.0  
**Date:** December 14, 2025  
**Purpose:** Define all integration points between AIOS planning and Cursor execution

---

## CORE BINDING: 5-Phase Execution Loop

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: PLAN (Embodied WM + Orchestrator)                      │
│ ─────────────────────────────────────────────────────────────  │
│ Input:  Current state + enterprise objectives                  │
│ Process: Generate 50-step trajectory (compressed to <50 tokens)│
│ Output:  PLAN_Vn with acceptance_criteria and AGENT_RULES     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ GATE 1: PLAN_REVIEW (L human - required for approval)          │
│ ─────────────────────────────────────────────────────────────  │
│ L reviews: Feasibility? Complete? Aligned?                     │
│ Decision: Approve or request revision                          │
│ Timeline: <1 hour (async)                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: IMPLEMENT (L Cursor Module + Cursor IDE)              │
│ ─────────────────────────────────────────────────────────────  │
│ Input:  PLAN_Vn (approved by L)                                │
│ Process: Build God Mode prompt → Submit to Cursor              │
│ Output:  Code diff, test results, git commit                   │
│ Duration: 5-30 minutes (bounded)                               │
│ Loop: If tests fail → auto-retry (max 2 times)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: TEST & AUDIT (Cursor + QC Module)                     │
│ ─────────────────────────────────────────────────────────────  │
│ Input:  Code from IMPLEMENT phase                              │
│ Process: Run tests, check coverage, validate criteria          │
│ Output:  QA_REPORT_Vn (PASS or BLOCKED_REWORK)                │
│ Duration: 2-5 minutes (automated)                              │
│ Loop: If BLOCKED → go back to IMPLEMENT with specific notes   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: REFLECT (L Cursor Module)                             │
│ ─────────────────────────────────────────────────────────────  │
│ Input:  QA_REPORT_Vn + execution_ledger entries               │
│ Process: Extract lessons, metrics, failure modes              │
│ Output:  REFLECTION_Vn with recommendations                    │
│ Duration: 1-2 minutes (automated)                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ GATE 2: REPLAN (L human - final approval + governance)          │
│ ─────────────────────────────────────────────────────────────  │
│ L reviews: Lessons valid? Metrics accurate? Recommendations OK?│
│ Decision: Approve merge to main, adjust AGENT_RULES, or iterate│
│ Timeline: <2 hours (async)                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: EVOLVE (AIOS Governance + Learning)                   │
│ ─────────────────────────────────────────────────────────────  │
│ Input:  Approved code + REFLECTION_Vn recommendations          │
│ Process: Merge to main, update AGENT_RULES, improve prompts   │
│ Output:  New system state, ready for next PLAN cycle           │
│ Loop:    Go to PHASE 1 with updated world model                │
└─────────────────────────────────────────────────────────────────┘
```

---

## DATA STRUCTURES: Schema Integration

### 1. PLAN_Vn (from Embodied WM to Cursor Module)

```yaml
# PLAN_V1 structure (maps directly to Cursor God Mode prompt)

plan_id: "plan_proj_001_v1"
type: "implementation"              # or: bugfix, refactor, test, documentation
project_id: "proj_auth"
task_id: "task_001_user_model"

# From Embodied World Model
trajectory_source:
  model_version: "dreamer_v3_enhanced"
  prediction_confidence: 0.92        # 50-step prediction confidence
  compressed_tokens: 48              # <50 tokens (from layer 3 compression)
  intention: "Implement User Authentication Module"
  estimated_impact: "HIGH"
  market_relevance: "CRITICAL"

# Task specification
task_description: |
  Implement a robust User Authentication module with:
  - Secure password hashing (bcrypt)
  - Email validation
  - Login rate limiting
  - Type-safe implementation with full docstrings
  
  This is critical for downstream services and market positioning.

# Success criteria (all must be met)
acceptance_criteria:
  - "User model with id, email, password_hash, created_at fields"
  - "bcrypt password hashing with salt rounds = 10"
  - "Email validation using RFC 5322 regex"
  - "Login endpoint with rate limiting (max 5 attempts/5min)"
  - "All functions have type hints and docstrings"
  - "Test coverage >= 95%"
  - "No linting issues (mypy strict, black, flake8)"

# Definition of Done
definition_of_done:
  - "All acceptance criteria verified by AUDIT phase"
  - "Tests pass in CI/CD pipeline"
  - "Code review: 0 critical or high severity issues"
  - "Git commit with conventional message: feat(auth): user authentication"
  - "Ready for merge to main (pending L REPLAN approval)"

# Implementation constraints (safety bounds)
agent_rules:
  max_files_allowed: 3
  max_lines_allowed: 150
  max_time_allowed_seconds: 1800      # 30 minutes
  
  allowed_directories:
    - "src/auth/"
    - "tests/auth/"
    - "docs/auth/"
  
  forbidden_directories:
    - "config/secrets/"
    - ".env"
    - ".git/"
    - "infrastructure/"
  
  must_include:
    - "type_hints"
    - "docstrings"
    - "unit_tests"
    - "git_commit"
  
  test_coverage_minimum: 0.95
  linting_profile: "strict"

# Contextual information
context:
  current_sprint: "AUTH_PHASE_1"
  previous_implementations: [
    { id: "task_000", status: "complete", lessons: "Clear specs prevent rework" }
  ]
  dependencies:
    - "Database schema ready (completed: task_000)"
    - "Testing framework set up (completed: task_000)"
  
  risk_notes: "High priority: blocks downstream services. Reputational risk if not secure."

created_at: "2025-12-14T10:00:00Z"
created_by: "orchestrator_aios"
approved_by: "L"
approved_at: "2025-12-14T10:15:00Z"
```

### 2. IMPLEMENTATION_LOG (from Cursor back to QC)

```yaml
# IMPLEMENTATION_LOG_V1: Cursor execution result

log_id: "impl_log_proj_001_v1"
plan_id: "plan_proj_001_v1"
project_id: "proj_auth"

execution:
  start_time: "2025-12-14T10:30:00Z"
  end_time: "2025-12-14T10:45:00Z"
  duration_seconds: 900
  status: "success"  # or: "failed", "timeout", "interrupted"

code_changes:
  files_modified:
    - path: "src/auth/user.py"
      lines_added: 127
      lines_deleted: 0
      functions_added: ["User", "hash_password", "verify_password"]
      functions_modified: []
  
  files_created:
    - path: "tests/auth/test_user.py"
      lines: 85
  
  total_files: 2
  total_lines_added: 212
  total_lines_deleted: 0
  within_agent_rules: true  # max_files=3✓, max_lines=150... wait, 212 > 150?

git:
  branch: "dev-task-001"
  commit_sha: "abc123def456..."
  commit_message: "feat(auth): implement user authentication with bcrypt"
  diff_stats: "2 files changed, 212 insertions"

testing:
  test_framework: "pytest"
  tests_run: 8
  tests_passed: 8
  tests_failed: 0
  coverage_percentage: 0.96
  coverage_threshold_met: true  # >= 0.95? Yes

linting:
  mypy_strict: { status: "passed", issues: 0 }
  black: { status: "passed", issues: 0 }
  flake8: { status: "passed", issues: 0 }
  overall_status: "clean"

logs:
  stdout: |
    Creating User model...
    Adding password hashing...
    Writing tests...
    Running pytest: 8 passed in 2.34s
    Running mypy: OK
    Running black: 2 files reformatted
    Running flake8: OK
  
  stderr: ""

artifacts:
  unified_diff: |
    --- a/src/auth/user.py
    +++ b/src/auth/user.py
    @@ -0,0 +1,127 @@
    +"""User authentication module."""
    +import bcrypt
    ...

validator_notes: |
  ✓ All acceptance criteria met
  ✓ Tests passing with 96% coverage
  ✓ Code clean: type hints, docstrings
  ✓ AGENT_RULES violated?: Hmm, total_lines=212 > max_lines=150
  ⚠ ESCALATION REQUIRED: AGENT_RULES max_lines violation

created_at: "2025-12-14T10:45:00Z"
```

### 3. QA_REPORT_Vn (from QC Module back to REPLAN gate)

```yaml
# QA_REPORT_V1: Quality assurance verdict

report_id: "qa_report_proj_001_v1"
log_id: "impl_log_proj_001_v1"
plan_id: "plan_proj_001_v1"

overall_status: "BLOCKED_REWORK_REQUIRED"  # or: "APPROVED_FOR_MERGE"

criteria_validation:
  - criterion: "User model with id, email, password_hash, created_at fields"
    passed: true
    evidence: "Verified in src/auth/user.py lines 10-25"
  
  - criterion: "bcrypt password hashing with salt rounds = 10"
    passed: true
    evidence: "bcrypt.hashpw() with rounds=10 in user.py line 42"
  
  - criterion: "Email validation using RFC 5322 regex"
    passed: false
    evidence: "Simple regex used, missing optional comments per RFC 5322"
    severity: "medium"
  
  - criterion: "Login endpoint with rate limiting (max 5 attempts/5min)"
    passed: false
    evidence: "Rate limiting not implemented; only basic login validation"
    severity: "high"
  
  - criterion: "All functions have type hints and docstrings"
    passed: true
    evidence: "100% coverage: all 3 functions have hints and docstrings"
  
  - criterion: "Test coverage >= 95%"
    passed: true
    evidence: "Coverage report: 96% overall"
  
  - criterion: "No linting issues (mypy strict, black, flake8)"
    passed: true
    evidence: "All tools passed clean"

code_quality:
  type_hints_coverage: 1.0   # 100%
  docstring_coverage: 1.0    # 100%
  cyclomatic_complexity: "A" # Good
  code_duplication: 0.0      # None

issues_found:
  - issue_id: "issue_1"
    category: "ACCEPTANCE_CRITERIA_UNMET"
    severity: "high"
    title: "Missing email RFC 5322 validation"
    description: "Current regex is too simple, doesn't handle all valid email formats"
    acceptance_criterion: "Email validation using RFC 5322 regex"
    recommendation: "Use email-validator library or full RFC 5322 regex"
  
  - issue_id: "issue_2"
    category: "ACCEPTANCE_CRITERIA_UNMET"
    severity: "high"
    title: "Rate limiting not implemented"
    description: "Task requires rate limiting for login endpoint; not present in code"
    acceptance_criterion: "Login endpoint with rate limiting"
    recommendation: "Add login_attempts counter with exponential backoff"
  
  - issue_id: "issue_3"
    category: "AGENT_RULES_VIOLATION"
    severity: "high"
    title: "Max lines exceeded"
    description: "Implementation added 212 lines; max_lines_allowed = 150"
    recommendation: "Split into smaller tasks or increase max_lines_allowed"

policy_violations:
  - rule: "agent_rules.max_lines_allowed"
    value_allowed: 150
    value_observed: 212
    severity: "high"
    action: "AUTO_ROLLBACK_TRIGGERED"

recommendations:
  - "Implement full RFC 5322 email validation"
  - "Add rate limiting to login endpoint"
  - "Consider splitting into 2 tasks: (1) User model, (2) Login endpoint"

next_action: "IMPLEMENT_REWORK"

auditor_notes: |
  Good attempt, but 2 acceptance criteria not met and 1 policy violation.
  Code quality is high, but scope exceeds bounds. Recommend rework
  with refined task breakdown:
  
  Task A: User model (50 lines)
  Task B: Validation (50 lines)
  Task C: Endpoint + rate limiting (50 lines)

created_at: "2025-12-14T10:50:00Z"
approved_at: null
approved_by: null
```

### 4. REFLECTION_Vn (from REFLECT phase)

```yaml
# REFLECTION_V1: Learning and improvement analysis

reflection_id: "refl_proj_001_v1"
cycle_number: 1
plan_id: "plan_proj_001_v1"
qa_report_id: "qa_report_proj_001_v1"

what_went_well:
  - "Clear acceptance criteria helped focus implementation"
  - "Type hints and docstrings were included (100% coverage)"
  - "Tests were written and passing (96% coverage)"
  - "Code quality metrics excellent (mypy, black, flake8 all clean)"

what_went_wrong:
  - "Scope was too large for single 30-min task (212 lines vs 150 limit)"
  - "Acceptance criteria were not validated during implementation"
  - "Rate limiting requirement was overlooked"
  - "Email validation was simplified, missing RFC 5322 compliance"

failure_modes_encountered:
  - failure_id: "fm_1"
    mode: "SCOPE_CREEP"
    description: "Developer added full authentication layer instead of just user model"
    root_cause: "Ambiguous task description; acceptance criteria not explicitly referenced"
    impact: "Task failed QC; requires rework"
  
  - failure_id: "fm_2"
    mode: "REQUIREMENTS_MISINTERPRETATION"
    description: "Rate limiting and RFC email validation were low priority in developer's mind"
    root_cause: "Acceptance criteria list was too long; unclear priority"
    impact: "2 criteria unmet; caused failure"
  
  - failure_id: "fm_3"
    mode: "AGENT_RULES_VIOLATION"
    description: "Developer exceeded max_lines_allowed (212 vs 150)"
    root_cause: "Single large task; should be decomposed"
    impact: "Policy violation; auto-rollback; rework required"

lessons_learned:
  - lesson: "Task decomposition is critical for success"
    evidence: "Single 150-line task succeeded; combined task failed"
    applicability: "Always decompose complex tasks into <100-line subtasks"
  
  - lesson: "Explicit acceptance criteria validation during execution prevents rework"
    evidence: "Criteria were not explicitly checked; 2 were missed"
    applicability: "Cursor prompt should explicitly list each criterion as a checklist"
  
  - lesson: "Max_lines_allowed should be set carefully during PLAN phase"
    evidence: "150 lines was too tight for this task; should be 200-250"
    applicability: "Orchestrator should auto-calculate max_lines based on task complexity"

process_improvements:
  - improvement: "Add explicit acceptance criteria checklist to God Mode prompt"
    expected_impact: "Prevent criteria misses; increase hit rate from 71% to 95%+"
    effort: "Low (modify prompt template)"
  
  - improvement: "Decompose large tasks automatically"
    expected_impact: "Fit within AGENT_RULES; single-pass success"
    effort: "Medium (add decomposition logic to PLAN phase)"
  
  - improvement: "Increase max_lines for similar tasks from 150 to 200"
    expected_impact: "Reduce scope violations; allow single-pass success"
    effort: "Low (adjust AGENT_RULES)"

agent_performance_metrics:
  cycles_to_completion: 2        # 1 failed + 1 more attempt needed
  acceptance_criteria_hit_rate: 0.71  # 5/7 passed
  criteria_passed: 5
  criteria_failed: 2
  rework_loops: 1
  policy_violations: 1
  first_time_success: false
  total_execution_time_minutes: 15
  lines_per_minute: 14.1         # 212 lines / 15 min
  cost_estimate_per_line: 0.05   # $0.05/line (labor cost)

recommended_adjustments:
  - adjustment: "AGENT_RULES.max_lines_allowed"
    current_value: 150
    recommended_value: 200
    rationale: "Tasks of this complexity need ~200 lines"
  
  - adjustment: "CursorPromptBuilder.build_impl_v1"
    change: "Add explicit checklist for each acceptance criterion"
    example_addition: |
      ## ACCEPTANCE CRITERIA CHECKLIST
      During implementation, verify each criterion:
      [ ] Criterion 1: User model with fields
      [ ] Criterion 2: bcrypt with salt=10
      [ ] Criterion 3: RFC 5322 email validation
      [ ] Criterion 4: Rate limiting (5 attempts/5min)
      [ ] Criterion 5: Type hints
      [ ] Criterion 6: Docstrings
      [ ] Criterion 7: 95%+ coverage
  
  - adjustment: "Orchestrator.decompose_plan"
    change: "Split single large task into 2-3 subtasks"
    rationale: "Each subtask stays under max_lines; prevents violations"

metrics_for_next_cycle:
  target_criteria_hit_rate: 0.95  # up from 0.71
  target_first_time_success: true # improve from false
  target_lines_per_task: 180      # down from 212
  target_rework_loops: 0          # down from 1
  target_cycle_time: 20           # up from 15 (more thorough)

next_plan_recommendations:
  - "Apply all 3 recommended adjustments before PLAN_V2"
  - "Decompose complex tasks into subtasks < 100 lines each"
  - "Use enhanced prompt with explicit criteria checklist"
  - "Increase max_lines_allowed for AUTH phase to 200"

created_at: "2025-12-14T10:55:00Z"
created_by: "qc_and_reflection_module"
approved_at: null
approved_by: null
```

---

## INTEGRATION APIs

### LCursorRuntime ↔ AIOS Orchestrator

```python
# From AIOS Orchestrator side
from L9.agents.L.cursor_module import LCursorRuntime
from L9.core.embodied_wm import EmbodiedWorldModel
from L9.core.orchestrator import AOISOrchestrator

# Initialize
runtime = LCursorRuntime()
ewm = EmbodiedWorldModel()
orchestrator = AOISOrchestrator()

# Main loop
while orchestrator.has_work():
    # PHASE 1: PLAN (Embodied WM generates trajectory)
    trajectory = ewm.predict_next_50_steps(
        current_state=orchestrator.get_current_state(),
        objectives=orchestrator.get_objectives(),
        market_conditions=orchestrator.get_market_conditions()
    )
    
    # Trajectory → PLAN_Vn (translate)
    plan_vn = orchestrator.translate_trajectory_to_plan(trajectory)
    
    # GATE 1: PLAN_REVIEW (L approves)
    if not orchestrator.await_human_approval(plan_vn):
        orchestrator.log_rejection(plan_vn)
        continue
    
    # PHASE 2: IMPLEMENT (Cursor takes over)
    result = runtime.submit_plan_to_cursor(
        plan_dict=plan_vn,
        project_id=orchestrator.get_project_id()
    )
    
    # PHASE 3: AUDIT (QC validates)
    qa_report = runtime.qc.audit_implementation(
        project_id=orchestrator.get_project_id(),
        implementation_log=result,
        acceptance_criteria=plan_vn["acceptance_criteria"]
    )
    
    if qa_report["overall_status"] != "APPROVED_FOR_MERGE":
        # Rework loop
        orchestrator.log_qa_failure(qa_report)
        # TODO: Auto-retry with refined plan
        continue
    
    # PHASE 4: REFLECT (Extract lessons)
    reflection = runtime.qc.generate_reflection(
        project_id=orchestrator.get_project_id(),
        cycle_number=orchestrator.get_cycle_number(),
        qa_report=qa_report,
        implementation_log=result
    )
    
    # GATE 2: REPLAN (L makes final decision)
    replan_decision = orchestrator.await_replan_approval(
        qa_report=qa_report,
        reflection=reflection
    )
    
    if replan_decision == "APPROVED_MERGE_TO_MAIN":
        # PHASE 5: EVOLVE
        orchestrator.merge_to_main(result)
        orchestrator.apply_reflection_adjustments(reflection)
        ewm.update_world_model(reflection)  # Learn for next cycle
    
    orchestrator.advance_to_next_cycle()
```

### Error Handling & Escalation

```python
# Escalation path: Cursor failure → L attention

try:
    result = runtime.submit_plan_to_cursor(plan_vn, project_id)
except Exception as e:
    # AUTOMATIC ESCALATION
    runtime.ledger.log_escalation(
        project_id=project_id,
        reason="Cursor submission failed",
        escalation_to="L",
        details={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "plan_id": plan_vn["plan_id"],
            "plan_summary": plan_vn["task_description"][:100]
        }
    )
    
    # Notify L (Slack, email, internal system)
    orchestrator.notify_escalation(
        severity="HIGH",
        message=f"Cursor invocation failed for {project_id}: {str(e)}"
    )
    
    # Wait for human intervention
    orchestrator.halt_autonomy()
    await orchestrator.human_decision()
```

---

## BACKWARD COMPATIBILITY

### Old God-AI-Agent Files (v6) → New Integrated Files (v7)

| Old File | New File | Changes |
|----------|----------|---------|
| LAYER_1_Embodied_World_Models.md | LAYER_1_EWM_Cursor_Integration.md | +Cursor invocation section |
| LAYER_2_Semantic_OS.md | LAYER_2_OS_Cursor_Governance.md | +AGENT_RULES enforcement |
| LAYER_3_Intention_Communication.md | LAYER_3_Intention_Cursor_Binding.md | +Prompt compression details |
| LAYER_4_Governance_Loops.md | LAYER_4_Governance_Cursor_Ledger.md | +Execution ledger schema |
| LAYER_5_Economic_Simulation.md | LAYER_5_Simulation_Cursor_VirtualAEs.md | +1000 virtual Cursor instances |
| LAYER_6_Hierarchical_Models.md | LAYER_6_Hierarchical_Cursor_Orchestration.md | +Multi-level orchestration |

**All 6 layers fully functional; Cursor module is optional add-on (doesn't break existing system).**

---

## DEPLOYMENT CHECKLIST

- [ ] VPS provisioned with Cursor IDE
- [ ] L Cursor Module installed and configured
- [ ] l_project_index.yaml created with first projects
- [ ] God-AI-Agent AIOS initialized
- [ ] Integration APIs tested end-to-end
- [ ] Execution ledger live and logging
- [ ] L approval gates functional
- [ ] Error handling and escalation tested
- [ ] QC and reflection modules active
- [ ] Learning loop enabled

---

**End of CURSOR_INTEGRATION_BRIDGE.md**
