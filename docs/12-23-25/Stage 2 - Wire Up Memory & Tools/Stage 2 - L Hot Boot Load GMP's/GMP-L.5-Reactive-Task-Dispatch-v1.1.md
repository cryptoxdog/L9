============================================================================
GMP-L.5 — REACTIVE TASK DISPATCH v1.1
GOD-MODE CURSOR PROMPT — CANONICAL GMPv1.6 FORMAT
============================================================================

PURPOSE:
• Enable real-time task generation from user queries
• Implement reactive dispatch loop in executor
• Connect WebSocket input to task pipeline
• Enable L to respond to requests without pre-planning

PREREQUISITE: GMP-L.0 through GMP-L.4 must be complete

============================================================================

ROLE
You are a constrained execution agent operating inside the L9 Secure AI OS repository at `/l9/`.
You execute instructions exactly as written. You do not redesign. You report only to this prompt.

MODIFICATION LOCK — ABSOLUTE
❌ NO: New files, unplanned changes, refactoring, freelancing
✅ YES: Exact locked TODO changes, phase-based execution, immediate STOP on drift

============================================================================

STRUCTURED OUTPUT REQUIREMENTS (SINGLE ARTIFACT)

Path: /l9/reports/exec_report_gmp_l5_dispatch.md

Sections (in exact order):
1. `# EXECUTION REPORT — GMP-L.5 Reactive Task Dispatch`
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

- [5.1] File: `/l9/executor.py` Lines: 50–80 Action: Insert
      Change: Add `_generate_tasks_from_query(query: str) -> List[Dict]` method to parse user requests into task specifications
      Gate: None
      Imports: NONE

- [5.2] File: `/l9/websocket_orchestrator.py` Lines: 100–130 Action: Insert
      Change: Add `on_user_message(message: str)` handler that triggers task generation and dispatch
      Gate: None
      Imports: NONE

- [5.3] File: `/l9/task_queue.py` Lines: 50–70 Action: Insert
      Change: Add `dispatch_task_immediate(task: QueuedTask) -> str` function for synchronous task execution without queue
      Gate: None
      Imports: asyncio (if not present)

- [5.4] File: `/l9/executor.py` Lines: 300–350 Action: Insert
      Change: Add `_reactive_dispatch_loop()` coroutine that continuously processes user messages and executes generated tasks
      Gate: None
      Imports: NONE

- [5.5] File: `/l9/tool_registry.py` Lines: END Action: Insert
      Change: Add `ask_l(query: str) -> dict` tool that triggers reactive task generation and execution pipeline
      Gate: None
      Imports: NONE

✅ PHASE 0 DEFINITION OF DONE:
- [ ] Report file created at `/l9/reports/exec_report_gmp_l5_dispatch.md`
- [ ] TODO PLAN is complete and valid
- [ ] TODO INDEX HASH generated
- [ ] No modifications made to repo
- [ ] Sections 1–3 written to report

============================================================================

PHASE 1 DEFINITION OF DONE:
- [ ] executor.py exists at specified lines (50–80, 300–350)
- [ ] websocket_orchestrator.py exists at specified lines (100–130)
- [ ] task_queue.py exists at specified lines (50–70)
- [ ] tool_registry.py exists with insertion point at end
- [ ] All targets verified present, no assumptions

============================================================================

PHASE 2 DEFINITION OF DONE:
- [ ] _generate_tasks_from_query() added to executor.py with full implementation
- [ ] on_user_message() handler added to websocket_orchestrator.py
- [ ] dispatch_task_immediate() function added to task_queue.py
- [ ] _reactive_dispatch_loop() coroutine added to executor.py
- [ ] ask_l() tool added to tool_registry.py
- [ ] Only TODO-listed files modified, only TODO-listed ranges touched
- [ ] No extra imports beyond declared, META headers preserved
- [ ] Exact line ranges recorded to report section 5

============================================================================

PHASE 3 DEFINITION OF DONE:
- [ ] Queries generate valid task specifications
- [ ] Tasks dispatch immediately upon user message
- [ ] Approval gates still respected for high-risk tasks
- [ ] Enforcement results written to report section 7

============================================================================

PHASE 4 DEFINITION OF DONE:
- [ ] Positive: User query generates 1+ tasks
- [ ] Positive: Tasks execute immediately (non-high-risk)
- [ ] Positive: High-risk tasks require approval
- [ ] Negative: Malformed query returns error
- [ ] Negative: High-risk tasks blocked without approval
- [ ] Regression: Plan-based execution still works
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
> GMP-L.5 (Reactive Task Dispatch) is complete and verified.
> Output verified. Report stored at `/l9/reports/exec_report_gmp_l5_dispatch.md`.
> Real-time task generation operational. L can now respond reactively to user queries.
> Prerequisites met for GMP-L.6 (Memory Substrate Integration).
> No further changes are permitted.

============================================================================

END OF GMP-L.5 CANONICAL GOD-MODE PROMPT v1.1
