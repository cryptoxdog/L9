============================================================================
GMP-L.6 — MEMORY SUBSTRATE INTEGRATION v1.1
GOD-MODE CURSOR PROMPT — CANONICAL GMPv1.6 FORMAT
============================================================================

PURPOSE:
• Bind memory systems (Postgres/Redis/Neo4j) to task execution
• Enable persistent state across task sequences
• Implement memory-backed task tracking
• Enable L to maintain context across operations

PREREQUISITE: GMP-L.0 through GMP-L.5 must be complete

============================================================================

ROLE
You are a constrained execution agent operating inside the L9 Secure AI OS repository at `/l9/`.
You execute instructions exactly as written. You do not redesign. You report only to this prompt.

MODIFICATION LOCK — ABSOLUTE
❌ NO: New files, unplanned changes, refactoring, freelancing
✅ YES: Exact locked TODO changes, phase-based execution, immediate STOP on drift

============================================================================

STRUCTURED OUTPUT REQUIREMENTS (SINGLE ARTIFACT)

Path: /l9/reports/exec_report_gmp_l6_memory.md

Sections (in exact order):
1. `# EXECUTION REPORT — GMP-L.6 Memory Substrate Integration`
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

- [6.1] File: `/l9/executor.py` Lines: 400–450 Action: Insert
      Change: Add `_bind_memory_context(task_id: str, agent_id: str)` method to load and inject memory state into executor
      Gate: None
      Imports: NONE (memory_helpers already imported)

- [6.2] File: `/l9/executor.py` Lines: 450–500 Action: Insert
      Change: Add `_persist_task_result(task_id: str, result: dict)` method to write execution results to Postgres
      Gate: None
      Imports: NONE

- [6.3] File: `/l9/redis_client.py` Lines: 200–250 Action: Insert
      Change: Add `get_task_context(task_id: str) -> dict` function to retrieve cached task state from Redis
      Gate: None
      Imports: NONE

- [6.4] File: `/l9/executor.py` Lines: 300–330 Action: Insert
      Change: Hook _bind_memory_context() and _persist_task_result() into _dispatch_tool_call() before and after execution
      Gate: None
      Imports: NONE

- [6.5] File: `/l9/tool_registry.py` Lines: END Action: Insert
      Change: Add `get_l_memory_state() -> dict` tool that exposes L's current memory context
      Gate: None
      Imports: NONE

- [6.6] File: `/l9/tool_registry.py` Lines: END Action: Insert
      Change: Add `recall_task_history(num_tasks: int = 10) -> List[dict]` tool to retrieve recent task execution history
      Gate: None
      Imports: NONE

✅ PHASE 0 DEFINITION OF DONE:
- [ ] Report file created at `/l9/reports/exec_report_gmp_l6_memory.md`
- [ ] TODO PLAN is complete and valid
- [ ] TODO INDEX HASH generated
- [ ] No modifications made to repo
- [ ] Sections 1–3 written to report

============================================================================

PHASE 1 DEFINITION OF DONE:
- [ ] executor.py exists at specified lines (400–450, 450–500, 300–330)
- [ ] redis_client.py exists at specified lines (200–250)
- [ ] tool_registry.py exists with insertion point at end
- [ ] Memory substrate (Postgres, Redis, Neo4j) accessible from executor
- [ ] All targets verified present, no assumptions

============================================================================

PHASE 2 DEFINITION OF DONE:
- [ ] _bind_memory_context() added to executor.py with full implementation
- [ ] _persist_task_result() added to executor.py with full implementation
- [ ] get_task_context() function added to redis_client.py
- [ ] Memory binding and persistence hooked into _dispatch_tool_call()
- [ ] get_l_memory_state() tool added to tool_registry.py
- [ ] recall_task_history() tool added to tool_registry.py
- [ ] Only TODO-listed files modified, only TODO-listed ranges touched
- [ ] No extra imports beyond declared, META headers preserved
- [ ] Exact line ranges recorded to report section 5

============================================================================

PHASE 3 DEFINITION OF DONE:
- [ ] Task context loaded before execution
- [ ] Task results persisted to Postgres after execution
- [ ] Memory state cached in Redis
- [ ] Task history queryable and retrievable
- [ ] Enforcement results written to report section 7

============================================================================

PHASE 4 DEFINITION OF DONE:
- [ ] Positive: Task context loaded correctly for known tasks
- [ ] Positive: Task results persisted and queryable
- [ ] Positive: Memory state retrieval works
- [ ] Positive: Task history returns recent operations
- [ ] Negative: Unknown task_id returns null context
- [ ] Negative: Persistence failure handled gracefully
- [ ] Regression: Non-memory-backed tasks still work
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
> GMP-L.6 (Memory Substrate Integration) is complete and verified.
> Output verified. Report stored at `/l9/reports/exec_report_gmp_l6_memory.md`.
> Memory systems operational. L can now maintain persistent state and recall execution history.
> Prerequisites met for GMP-L.7 (Bootstrap Simulation).
> No further changes are permitted.

============================================================================

END OF GMP-L.6 CANONICAL GOD-MODE PROMPT v1.1
