============================================================================
GMP-L.4 — LONG-PLAN INTEGRATION v1.1
GOD-MODE CURSOR PROMPT — CANONICAL GMPv1.6 FORMAT
============================================================================

PURPOSE:
• Integrate long-plan generation into L's task pipeline
• Enable L to extract task sequences from multi-step plans
• Connect plan graph to task queue
• Enable GMP execution via long-plan mechanism

PREREQUISITE: GMP-L.0, GMP-L.1, GMP-L.2, GMP-L.3 must be complete

============================================================================

ROLE
You are a constrained execution agent operating inside the L9 Secure AI OS repository at `/l9/`.
You execute instructions exactly as written. You do not redesign. You report only to this prompt.

MODIFICATION LOCK — ABSOLUTE
❌ NO: New files, unplanned changes, refactoring, freelancing
✅ YES: Exact locked TODO changes, phase-based execution, immediate STOP on drift

============================================================================

STRUCTURED OUTPUT REQUIREMENTS (SINGLE ARTIFACT)

Path: /l9/reports/exec_report_gmp_l4_longplan.md

Sections (in exact order):
1. `# EXECUTION REPORT — GMP-L.4 Long-Plan Integration`
2. `## TODO PLAN (LOCKED)`
3. `## TODO INDEX HASH`
4. `## PHASE CHECKLIST STATUS (0–6)`
5. `## FILES MODIFIED + LINE RANGES`
6. `## TODO → CHANGE MAP`
7. `## ENFORCEMENT + VALIDATION RESULTS`
8. `## PHASE 5 RECURSIVE VERIFICATION`
9. `## FINAL DEFINITION OF DONE (TOTAL)`
10. `## FINAL DECLARATION`

============================================================================

PHASE 0 TODO PLAN (LOCKED):

- [4.1] File: `/l9/long_plan_graph.py` Lines: 380–410 Action: Insert
      Change: Add method `extract_tasks_from_plan(plan_id: str) -> List[Dict]` to extract executable task specs from completed plan
      Gate: None
      Imports: NONE

- [4.2] File: `/l9/task_queue.py` Lines: END Action: Insert
      Change: Add function `enqueue_long_plan_tasks(plan_id: str, task_specs: List[Dict]) -> List[str]` to bulk-enqueue extracted tasks
      Gate: None
      Imports: uuid4 (from uuid)

- [4.3] File: `/l9/executor.py` Lines: 200–220 Action: Insert
      Change: Add `_execute_plan_sequence()` handler that dequeues and executes tasks from a plan in order, with approval checks
      Gate: None
      Imports: NONE

- [4.4] File: `/l9/tool_registry.py` Lines: END Action: Insert
      Change: Add `execute_long_plan(plan_id: str, repo_root: str) -> dict` tool that triggers plan-based task execution
      Gate: None
      Imports: NONE

✅ PHASE 0 DEFINITION OF DONE:
- [ ] Report file created at `/l9/reports/exec_report_gmp_l4_longplan.md`
- [ ] TODO PLAN is complete and valid
- [ ] TODO INDEX HASH generated
- [ ] No modifications made to repo
- [ ] Sections 1–3 written to report

============================================================================

PHASE 1 DEFINITION OF DONE:
- [ ] long_plan_graph.py exists at specified file and line range
- [ ] task_queue.py exists with insertion point at end
- [ ] executor.py exists at specified lines
- [ ] tool_registry.py exists with insertion point at end
- [ ] All targets verified present, no assumptions

============================================================================

PHASE 2 DEFINITION OF DONE:
- [ ] extract_tasks_from_plan() added to long_plan_graph.py with full implementation
- [ ] enqueue_long_plan_tasks() added to task_queue.py with full implementation
- [ ] _execute_plan_sequence() added to executor.py with approval checks
- [ ] execute_long_plan() tool added to tool_registry.py with full implementation
- [ ] Only TODO-listed files modified, only TODO-listed ranges touched
- [ ] No extra imports, META headers preserved
- [ ] Exact line ranges recorded to report section 5

============================================================================

PHASE 3 DEFINITION OF DONE:
- [ ] Tasks extracted from valid plans
- [ ] Tasks enqueued with correct status
- [ ] Plan sequence execution respects approval gates
- [ ] Enforcement results written to report section 7

============================================================================

PHASE 4 DEFINITION OF DONE:
- [ ] Positive: Plans extract tasks correctly (at least 3 tasks)
- [ ] Positive: Tasks enqueue and execute in order
- [ ] Negative: Invalid plan ID returns error
- [ ] Negative: Non-approved destructive tasks blocked
- [ ] Regression: Non-plan tasks still work normally
- [ ] Results recorded to report section 7

============================================================================

PHASE 5 & 6: [STANDARD VERIFICATION + FINALIZATION]

✓ All phases (0–6) complete
✓ Scope locked, no drift
✓ Recursive verification passed
✓ Report complete and verified

============================================================================

FINAL DECLARATION (REQUIRED IN REPORT)

> All phases (0–6) complete. No assumptions. No drift. Scope locked. Execution terminated.
> GMP-L.4 (Long-Plan Integration) is complete and verified.
> Output verified. Report stored at `/l9/reports/exec_report_gmp_l4_longplan.md`.
> Long-plan task extraction operational. Plan-based execution ready.
> Prerequisites met for GMP-L.5 (Reactive Task Dispatch).
> No further changes are permitted.

============================================================================

END OF GMP-L.4 CANONICAL GOD-MODE PROMPT v1.1
