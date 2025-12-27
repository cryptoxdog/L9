# AGENT_RULES_FRAMEWORK: Safety Bounds and Governance Constraints
## God-AI-Agent + Cursor Module Safety Architecture

**Version:** 1.0.0  
**Date:** December 14, 2025  
**Purpose:** Define immutable safety rules, escalation policies, and learning loops

---

## CORE PRINCIPLE: Bounded Autonomy

**Statement:**  
> "The Cursor Module operates within strict, enforceable bounds set by AGENT_RULES.  
> Violations trigger automatic rollback and escalation to human oversight.  
> The system can NEVER override these rules autonomously."

---

## AGENT_RULES TAXONOMY

### Tier 1: Hard Stops (Immutable - Cannot Be Broken)

#### 1.1 File Scope Rules
```yaml
rule: "max_files_allowed"
type: "hard_stop"
enforcement: "pre-execution (diff analysis)"
examples:
  task_simple: 1-2 files
  task_medium: 3-5 files
  task_complex: 5-8 files
effect_if_violated: "automatic rollback, escalation to L"
cannot_be_overridden: true

rule: "forbidden_directories"
type: "hard_stop"
enforcement: "diff analysis + pre-merge check"
examples:
  forbidden:
    - "config/secrets/"
    - ".env"
    - ".git/"
    - "infrastructure/"
  reason: "Prevent accidental exposure of credentials or system files"
effect_if_violated: "automatic rollback, escalation to L"
cannot_be_overridden: true

rule: "file_type_whitelist"
type: "hard_stop"
enforcement: "pre-execution (file extension validation)"
allowed_extensions:
  - ".py", ".js", ".ts", ".go", ".java", ".cpp"
  - ".md", ".yaml", ".json", ".toml"
forbidden_extensions:
  - ".exe", ".dll", ".so"
  - ".key", ".pem", ".crt"
effect_if_violated: "automatic rollback, escalation to L"
cannot_be_overridden: true
```

#### 1.2 Code Quality Rules
```yaml
rule: "test_coverage_minimum"
type: "hard_stop"
enforcement: "post-execution (coverage report)"
value: "80-95% (configurable per project)"
effect_if_violated: "AUDIT fails, loop back to IMPLEMENT"
cannot_be_overridden: true

rule: "linting_must_pass"
type: "hard_stop"
enforcement: "post-execution (mypy, black, flake8)"
tools:
  - "mypy --strict"
  - "black --check"
  - "flake8 --max-line-length=100"
effect_if_violated: "AUDIT fails, loop back to IMPLEMENT"
cannot_be_overridden: true

rule: "acceptance_criteria_all_met"
type: "hard_stop"
enforcement: "AUDIT phase (manual + automated checks)"
effect_if_violated: "AUDIT fails, loop back to IMPLEMENT"
cannot_be_overridden: true

rule: "no_security_vulnerabilities"
type: "hard_stop"
enforcement: "pre-execution (static analysis) + AUDIT (manual review)"
tools:
  - "bandit (Python security linter)"
  - "SAST (static analysis security testing)"
effect_if_violated: "automatic rollback, escalation to L (security team)"
cannot_be_overridden: true
```

#### 1.3 Governance Rules
```yaml
rule: "execution_ledger_immutable"
type: "hard_stop"
enforcement: "write-once to execution_ledger.jsonl"
explanation: "Audit trail cannot be modified or deleted"
effect_if_violated: "system panic, escalation to L (potential breach)"
cannot_be_overridden: true

rule: "human_gates_required"
type: "hard_stop"
gates:
  - "PLAN_REVIEW: L must approve before IMPLEMENT"
  - "REPLAN: L must approve before merge to main"
effect_if_violated: "cannot proceed autonomously"
cannot_be_overridden: true

rule: "no_auto_commit_to_main"
type: "hard_stop"
enforcement: "branch validation"
allowed_branches:
  - "dev-task-*"
  - "feature/*"
forbidden_branches:
  - "main"
  - "production"
effect_if_violated: "merge blocked by CI/CD, escalation"
cannot_be_overridden: true

rule: "task_time_limit"
type: "hard_stop"
enforcement: "real-time timer"
value: "30 minutes per task"
effect_if_violated: "automatic timeout, rollback, escalation"
cannot_be_overridden: true
```

### Tier 2: Soft Bounds (Configurable - Can Be Adjusted Per Project)

```yaml
# These can be set per-project in AGENT_RULES but not overridden mid-task

configuration_points:
  - "max_lines_allowed: 50-200 lines (project-specific)"
  - "test_coverage_minimum: 80-95% (project-specific)"
  - "allowed_directories: customizable per project"
  - "max_files_allowed: 1-10 (project-specific)"
  - "max_concurrent_tasks: 1-3 (per agent)"

adjustment_process:
  1. "REFLECT phase generates metrics and recommendations"
  2. "L reviews recommendations"
  3. "REPLAN gate: L approves or rejects adjustment"
  4. "Adjustment applies to next PLAN_V(n+1)"

example_adjustment:
  metric: "cycles_to_completion: 3 (too many rework loops)"
  root_cause: "max_lines_allowed too tight (150 lines was too restrictive)"
  recommendation: "Increase max_lines_allowed to 200"
  process: "REFLECT → L review → REPLAN approval → apply to next task"
```

### Tier 3: Learning Parameters (Adaptive - Improve Automatically)

```yaml
# System learns and optimizes these through REFLECT phase

learning_targets:
  - "CursorPromptBuilder templates: improve clarity"
  - "Acceptance criteria phrasing: reduce ambiguity"
  - "Task decomposition: split complex tasks"
  - "AGENT_RULES calibration: adjust bounds for faster success"

learning_mechanism:
  1. "Execute task (IMPLEMENT)"
  2. "Record outcome metrics (AUDIT)"
  3. "Analyze failure modes (REFLECT)"
  4. "Propose adjustments (REFLECTION_Vn)"
  5. "L approves/rejects (REPLAN gate)"
  6. "Apply improvements (EVOLVE)"
  7. "Measure impact (next cycle metrics)"

feedback_loop_timeline:
  cycle_1: "baseline metrics"
  cycle_2: "first improvement applied"
  cycle_3: "measure impact"
  cycle_4: "next adjustment"

target_improvements:
  metric: "acceptance_criteria_hit_rate"
  current: "71% (example from LAYER 1 integration)"
  target: "95%+"
  timeline: "3-5 cycles"
```

---

## ESCALATION POLICY

### Automatic Escalation Triggers

```yaml
escalation_rules:
  
  - trigger_id: "ESC_001"
    trigger: "AGENT_RULES_VIOLATION"
    examples:
      - "max_files_allowed exceeded"
      - "max_lines_allowed exceeded"
      - "forbidden_directory touched"
      - "file_type_whitelist violated"
    action: "automatic rollback + escalation"
    severity: "CRITICAL"
    escalation_to: "L"
    timeline: "immediate"
  
  - trigger_id: "ESC_002"
    trigger: "SECURITY_VULNERABILITY_DETECTED"
    examples:
      - "hardcoded credentials found"
      - "SQL injection vulnerability"
      - "unsafe deserialization"
      - "XSS vulnerability"
    action: "automatic rollback + escalation"
    severity: "CRITICAL"
    escalation_to: "L + security_team"
    timeline: "immediate"
  
  - trigger_id: "ESC_003"
    trigger: "TEST_FAILURE"
    examples:
      - "any test failed"
      - "coverage drops below minimum"
      - "type checking fails (mypy strict)"
    action: "loop back to IMPLEMENT (auto-retry max 2x)"
    severity: "HIGH"
    escalation_to: "L (if manual retry exhausted)"
    timeline: "after 2 auto-retries"
  
  - trigger_id: "ESC_004"
    trigger: "ACCEPTANCE_CRITERIA_UNMET"
    examples:
      - "1+ acceptance criteria failed AUDIT"
      - "QA_REPORT status: BLOCKED_REWORK_REQUIRED"
    action: "loop back to IMPLEMENT (manual intervention by L)"
    severity: "HIGH"
    escalation_to: "L"
    timeline: "<1 hour"
    l_action: "refine plan or approve with known gaps"
  
  - trigger_id: "ESC_005"
    trigger: "AMBIGUOUS_REQUIREMENT"
    examples:
      - "acceptance criterion unclear"
      - "conflicting requirements"
      - "acceptance_criteria_hit_rate < 70%"
    action: "AUDIT flags as UNCLEAR; loop back to PLAN"
    severity: "MEDIUM"
    escalation_to: "L"
    timeline: "within 1 cycle"
    l_action: "clarify requirements or split task"
  
  - trigger_id: "ESC_006"
    trigger: "TIMEOUT"
    examples:
      - "task execution > 30 minutes"
      - "test run > 10 minutes"
    action: "interrupt execution, rollback to checkpoint"
    severity: "HIGH"
    escalation_to: "L"
    timeline: "immediate"
  
  - trigger_id: "ESC_007"
    trigger: "RESOURCE_EXHAUSTION"
    examples:
      - "out of memory"
      - "disk space critical"
      - "CPU throttling"
    action: "halt execution, escalation"
    severity: "CRITICAL"
    escalation_to: "L + infrastructure_team"
    timeline: "immediate"
  
  - trigger_id: "ESC_008"
    trigger: "DEPENDENCY_UNAVAILABLE"
    examples:
      - "database offline"
      - "required service unavailable"
      - "API rate limited"
    action: "halt execution, escalation"
    severity: "HIGH"
    escalation_to: "L"
    timeline: "immediate"
    l_action: "wait for dependency or split task"
  
  - trigger_id: "ESC_009"
    trigger: "EXECUTION_LEDGER_CORRUPTION"
    examples:
      - "ledger write failed"
      - "ledger data mismatch"
    action: "system panic, halt all execution"
    severity: "CRITICAL"
    escalation_to: "L + ops_team"
    timeline: "immediate"
    l_action: "investigate audit trail integrity"
  
  - trigger_id: "ESC_010"
    trigger: "CONTEXT_LOSS_OR_MISMATCH"
    examples:
      - "project state inconsistency"
      - "project_index corruption"
      - "workflow_state.md missing"
    action: "halt execution, escalation"
    severity: "CRITICAL"
    escalation_to: "L"
    timeline: "immediate"
    l_action: "reconcile state or reset project"
```

### Escalation Action Template

```python
# Code path: Escalation detected → Log + Notify + Halt

def escalate_to_human(
    trigger_id: str,
    severity: str,
    context: Dict[str, Any],
    escalation_to: List[str],
) -> None:
    """
    Escalate issue to human for intervention.
    
    Args:
        trigger_id: ESC_001, ESC_002, etc.
        severity: CRITICAL, HIGH, MEDIUM
        context: Full context (project_id, plan_id, error details)
        escalation_to: ["L", "security_team"] etc.
    """
    
    # 1. Log to ledger (immutable audit trail)
    runtime.ledger.log_escalation(
        escalation_trigger=trigger_id,
        severity=severity,
        context=context,
    )
    
    # 2. Halt autonomous execution
    runtime.halt_autonomy()
    
    # 3. Notify humans
    for recipient in escalation_to:
        notify_escalation(
            recipient=recipient,
            trigger=trigger_id,
            severity=severity,
            message=escalation_message(trigger_id, context),
            url=human_review_link(context),
        )
    
    # 4. Wait for human decision
    decision = await runtime.await_human_decision(
        timeout_seconds=3600,  # 1 hour
    )
    
    # 5. Log decision and proceed
    runtime.ledger.log_human_decision(
        escalation_id=escalation_id,
        decision=decision,
        decided_by=decision.decided_by,
    )
    
    if decision.action == "APPROVE_AND_CONTINUE":
        runtime.resume_autonomy()
    elif decision.action == "REWORK_REQUIRED":
        runtime.loop_back_to_phase(decision.phase)
    elif decision.action == "HALT":
        runtime.halt_all_work()
```

---

## FAILURE MODES & MITIGATIONS

### Mitigation Matrix

| Failure Mode | Severity | Detection | Cause | Mitigation |
|---|---|---|---|---|
| **Scope Creep** | HIGH | Diff > max_lines | Task too large | Auto-decompose; adjust max_lines |
| **Criteria Miss** | HIGH | AUDIT fails | Unclear requirements | Refine prompt template; explicit checklist |
| **Test Failure** | HIGH | TEST fails | Implementation bug | Auto-retry (max 2x); manual if persists |
| **Security Issue** | CRITICAL | SAST scan | Insecure pattern | Auto-rollback; escalate to security team |
| **Timeout** | HIGH | Timer | Task takes >30 min | Interrupt; reduce scope; escalate |
| **Coverage Drop** | HIGH | Coverage report | Inadequate testing | Loop back to IMPLEMENT |
| **Policy Violation** | CRITICAL | Rule check | AGENT_RULES broken | Auto-rollback; escalate to L |
| **Context Loss** | CRITICAL | Consistency check | State corruption | Panic; escalate to ops |
| **Dependency Failure** | HIGH | Status check | External service down | Retry or escalate; wait for fix |
| **Ambiguous Spec** | MEDIUM | AUDIT analysis | Requirement unclear | Escalate; request clarification |

---

## LEARNING & CONTINUOUS IMPROVEMENT

### Metrics Tracked for Each Task

```yaml
execution_metrics:
  
  - metric: "cycles_to_completion"
    definition: "Number of loops (IMPLEMENT, AUDIT) before APPROVED_FOR_MERGE"
    target: "1 (first-time success)"
    current_baseline: "2-3"
    improvement_path: "Better task decomposition, clearer criteria"
  
  - metric: "acceptance_criteria_hit_rate"
    definition: "% of acceptance criteria met on first attempt"
    target: "95%+"
    current_baseline: "71% (from LAYER 1 example)"
    improvement_path: "Explicit criteria checklist in prompt"
  
  - metric: "first_time_success_rate"
    definition: "% of tasks that pass AUDIT on first IMPLEMENT attempt"
    target: "90%+"
    current_baseline: "60%"
    improvement_path: "Refine AGENT_RULES, decompose better"
  
  - metric: "policy_violation_rate"
    definition: "% of tasks that violate AGENT_RULES"
    target: "0%"
    current_baseline: "5% (from LAYER 1 example)"
    improvement_path: "Calibrate max_lines, auto-decompose"
  
  - metric: "rework_cycles_per_task"
    definition: "Average loops for task completion"
    target: "<1"
    current_baseline: "1.5"
    improvement_path: "Better initial planning"
  
  - metric: "execution_time_per_line"
    definition: "Minutes per 100 lines of code (efficiency metric)"
    target: "3-5 minutes"
    current_baseline: "7 minutes (from LAYER 1 example)"
    improvement_path: "Streamline Cursor prompt"

improvement_triggers:
  if_criteria_hit_rate_drops: "Refine prompt, add examples"
  if_rework_loops_increase: "Adjust AGENT_RULES, decompose better"
  if_policy_violations_increase: "Tighten validation, auto-check earlier"
  if_timeouts_occur: "Reduce task scope, parallelize"

feedback_cycle:
  1. "Execute (IMPLEMENT)"
  2. "Measure (AUDIT)"
  3. "Analyze (REFLECT)"
  4. "Adjust (REPLAN → approve new AGENT_RULES)"
  5. "Apply (next task uses improved rules)"
  6. "Measure impact (compare metrics)"
```

### Recommended Adjustments Template

```yaml
# From REFLECTION_Vn → REPLAN gate

recommended_adjustments:
  
  - id: "adj_1"
    metric_source: "REFLECT phase identified ambiguity"
    current_state: "acceptance_criteria_hit_rate = 71%"
    target_state: "acceptance_criteria_hit_rate >= 95%"
    adjustment_type: "prompt_improvement"
    specific_change: |
      Add explicit checklist to God Mode prompt:
      
      ## ACCEPTANCE CRITERIA CHECKLIST
      Please verify each criterion during implementation:
      [ ] Criterion 1: ...
      [ ] Criterion 2: ...
      [ ] Criterion 3: ...
      
      At the end of implementation, re-run this checklist.
    expected_impact: "Reduce criteria misses from 29% to <5%"
    effort_to_implement: "LOW (template update)"
    approval_required: "L approval at REPLAN gate"
  
  - id: "adj_2"
    metric_source: "policy_violations = 20% (AGENT_RULES exceeded)"
    current_state: "max_lines_allowed = 150"
    target_state: "max_lines_allowed = 200"
    adjustment_type: "agent_rules_adjustment"
    specific_change: "Increase max_lines from 150 to 200 for AUTH tasks"
    expected_impact: "Reduce policy violations from 20% to <5%"
    effort_to_implement: "TRIVIAL (config change)"
    approval_required: "L approval at REPLAN gate"
  
  - id: "adj_3"
    metric_source: "rework_loops = 1.5x (too many retries)"
    current_state: "Task decomposition: 1 large task"
    target_state: "Task decomposition: 3 focused subtasks"
    adjustment_type: "workflow_improvement"
    specific_change: |
      Split PLAN_V2 into 3 subtasks:
      A) User model definition (50 lines)
      B) Email validation and hashing (50 lines)
      C) Login endpoint and rate limiting (50 lines)
    expected_impact: "Reduce rework from 1.5x to <1x"
    effort_to_implement: "MEDIUM (restructure task graph)"
    approval_required: "L approval at REPLAN gate"
```

---

## ENFORCEMENT MECHANISMS

### Pre-Execution Validation

```python
# Check AGENT_RULES before Cursor invocation

def validate_agent_rules(plan_vn: Dict[str, Any]) -> bool:
    """
    Pre-execution validation of AGENT_RULES.
    
    Returns:
        True if all rules will be enforceable
        False if violation likely → escalate
    """
    
    rules = plan_vn.get("agent_rules", {})
    
    # Check file scope
    if "max_files_allowed" not in rules:
        escalate("Missing max_files_allowed in AGENT_RULES")
        return False
    
    # Check time limit
    if "max_time_allowed_seconds" not in rules:
        rules["max_time_allowed_seconds"] = 1800  # 30 min default
    
    # Check test coverage minimum
    if "test_coverage_minimum" not in rules:
        rules["test_coverage_minimum"] = 0.80  # 80% default
    
    # Check forbidden directories
    if not rules.get("forbidden_directories"):
        escalate("No forbidden_directories defined; security risk")
        return False
    
    return True

def enforce_at_execution(result: Dict[str, Any], rules: Dict[str, Any]) -> bool:
    """
    Post-execution enforcement of AGENT_RULES.
    
    Returns:
        True if result complies
        False → auto-rollback + escalation
    """
    
    # Check files modified
    files_modified = len(result.get("files_modified", []))
    if files_modified > rules.get("max_files_allowed", 5):
        escalate(
            f"Files modified ({files_modified}) exceed max ({rules['max_files_allowed']})"
        )
        return False
    
    # Check lines changed
    lines_added = result.get("lines_added", 0)
    if lines_added > rules.get("max_lines_allowed", 200):
        escalate(
            f"Lines added ({lines_added}) exceed max ({rules['max_lines_allowed']})"
        )
        return False
    
    # Check coverage
    coverage = result.get("coverage_percentage", 0)
    if coverage < rules.get("test_coverage_minimum", 0.80):
        escalate(f"Coverage ({coverage*100}%) below minimum ({rules['test_coverage_minimum']*100}%)")
        return False
    
    # Check linting
    if not result.get("linting_clean", False):
        escalate("Linting failed; mypy, black, or flake8 issues found")
        return False
    
    return True
```

---

## SUMMARY: AGENT_RULES ARE SACRED

✅ **Hard Stops** (Tier 1): Never broken, automatic enforcement  
✅ **Soft Bounds** (Tier 2): Configured per project, adjusted via L approval  
✅ **Learning Parameters** (Tier 3): Continuously improved through feedback loop  

**Key Principle:**  
> Violations = Automatic rollback + Escalation to L + Full audit trail  
> The system cannot, will not, and should not override these rules.

---

**End of AGENT_RULES_FRAMEWORK.md**
