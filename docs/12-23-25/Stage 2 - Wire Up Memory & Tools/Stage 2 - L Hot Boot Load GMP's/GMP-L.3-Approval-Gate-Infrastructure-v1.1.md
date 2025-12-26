============================================================================
GMP-L.3 — APPROVAL GATE INFRASTRUCTURE v1.1
GOD-MODE CURSOR PROMPT — CANONICAL GMPv1.6 FORMAT
============================================================================

PURPOSE:
• Create approval queue system for high-risk tools and operations
• Implement ApprovalManager class to handle Igor-only approvals
• Block destructive tools (gmp_run, git_commit) until approved
• Prepare governance for human-in-the-loop verification

============================================================================

ROLE
You are a constrained execution agent operating inside the L9 Secure AI OS repository at `/l9/`.
You execute instructions exactly as written.
You do not redesign systems.
You do not invent requirements.
You do not guess missing information.
You do not freelance.
You report only to this prompt.

============================================================================

MODIFICATION LOCK — ABSOLUTE

❌ YOU MAY NOT:
• Create new files unless explicitly listed in the Phase 0 TODO plan
• Modify anything not listed in the Phase 0 TODO plan
• Add logging, optimization, comments, abstractions, or formatting changes
• Refactor unrelated logic or reorganize files
• Fix adjacent issues not explicitly listed
• Guess user intent
• Assume architecture or expected behavior

✅ YOU MAY ONLY:
• Implement exact changes defined in the locked TODO plan
• Operate only inside defined phases
• Stop immediately if ambiguity or mismatch is detected
• Report results exactly in the required report format

============================================================================

L9-SPECIFIC OPERATING CONSTRAINTS (NON-NEGOTIABLE)

• All file paths must be absolute and under `/l9/`
• Any change must preserve L9 architecture invariants unless explicitly planned:
  - Kernel/agent execution flows are not rewritten by default
  - Memory substrate (Postgres/Redis/Neo4j bindings) is not altered by default
  - WebSocket orchestration foundations are not altered by default
  - Entry points and docker-compose services are not modified by default
• If any requested change implies touching these invariants, it MUST appear in Phase 0 TODO plan.
• Prerequisite: GMP-L.0, GMP-L.1, GMP-L.2 must be complete before this GMP executes

============================================================================

STRUCTURED OUTPUT REQUIREMENTS (SINGLE ARTIFACT)

All output from this work MUST be written to a single markdown file:

```text
Path: /l9/reports/exec_report_gmp_l3_approvals.md
```

The report MUST contain the following sections in this exact order:

1. `# EXECUTION REPORT — GMP-L.3 Approval Gate Infrastructure`
2. `## TODO PLAN (LOCKED)`
3. `## TODO INDEX HASH`
4. `## PHASE CHECKLIST STATUS (0–6)`
5. `## FILES MODIFIED + LINE RANGES`
6. `## TODO → CHANGE MAP`
7. `## ENFORCEMENT + VALIDATION RESULTS`
8. `## PHASE 5 RECURSIVE VERIFICATION`
9. `## FINAL DEFINITION OF DONE (TOTAL)`
10. `## FINAL DECLARATION`

CHECKLIST MARKING POLICY:
• All checklists MUST be rendered as `[ ]` unchecked by default.
• A checkbox may be marked `[x]` only after the corresponding requirement is verified true.
• Pre-checking boxes without evidence is forbidden.

No other output format is permitted.

============================================================================

PHASE 0–6: [FULLY SPECIFIED IN GMP-L.2 TEMPLATE]

[Repeat all PHASE 0–6 definitions from GMP-L.2 canonical template]

PHASE 0 ACTIONS (GMP-L.3 SPECIFIC):
• Inspect task_queue.py, executor.py, and tool_registry.py for approval hookpoints
• Confirm QueuedTask dataclass structure
• Confirm executor._dispatch_tool_call() location and signature
• Create deterministic TODO plan for approval system
• Generate TODO INDEX HASH

PHASE 0 TODO PLAN (LOCKED):

- [3.1] File: `/l9/task_queue.py` Lines: 166–190 Action: Replace
      Change: Extend QueuedTask dataclass with approval fields (status, approved_by, approval_timestamp, approval_reason)
      Gate: None
      Imports: NONE

- [3.2] File: `/l9/governance/approvals.py` Lines: NEW Action: Insert
      Change: Create new ApprovalManager class with approve_task(), reject_task(), and is_approved() methods
      Gate: None
      Imports: logging, datetime, Optional, PacketEnvelopeIn

- [3.3] File: `/l9/executor.py` Lines: 136–150 Action: Insert
      Change: Add approval check in _dispatch_tool_call() before tool execution (requires Igor approval for high-risk tools)
      Gate: tool_def.get("requires_igor_approval") == True
      Imports: NONE (ApprovalManager already imported at module level in Phase 2)

- [3.4] File: `/l9/tool_registry.py` Lines: END Action: Insert
      Change: Add gmp_run() tool function that enqueues GMP executions as pending tasks without immediate execution
      Gate: None
      Imports: uuid4 (from uuid)

- [3.5] File: `/l9/tool_registry.py` Lines: END Action: Insert
      Change: Add git_commit() tool function that enqueues git operations as pending tasks without immediate execution
      Gate: None
      Imports: NONE

✅ PHASE 0 DEFINITION OF DONE:
- [ ] Report file created at `/l9/reports/exec_report_gmp_l3_approvals.md`
- [ ] TODO PLAN is complete and valid (all required fields present)
- [ ] TODO PLAN contains only observable and executable items
- [ ] TODO INDEX HASH is generated and written to report
- [ ] No modifications made to repo
- [ ] Phase 0 output written to report sections 1–3

❌ FAIL RULE:
If any TODO item is underspecified or unverifiable, STOP immediately.

============================================================================

PHASE 1 ACTIONS (GMP-L.3 SPECIFIC):

✅ PHASE 1 DEFINITION OF DONE:
- [ ] task_queue.py QueuedTask class exists at specified lines
- [ ] executor.py _dispatch_tool_call() method exists at specified lines
- [ ] tool_registry.py exists and has end-of-file insertion point
- [ ] governance/ directory exists and is writable
- [ ] No assumptions required to implement

============================================================================

PHASE 2 ACTIONS (GMP-L.3 SPECIFIC):

✅ PHASE 2 DEFINITION OF DONE:
- [ ] QueuedTask extended with status, approved_by, approval_timestamp, approval_reason fields
- [ ] ApprovalManager class created in governance/approvals.py with full implementation
- [ ] executor._dispatch_tool_call() includes approval check with proper error response
- [ ] gmp_run() tool added to tool_registry.py with full implementation
- [ ] git_commit() tool added to tool_registry.py with full implementation
- [ ] All imports are minimal and necessary
- [ ] No formatting or stylistic changes made

============================================================================

PHASE 3 ACTIONS (GMP-L.3 SPECIFIC):

- [3.1] Guard: High-risk tools (requires_igor_approval=True) must not execute without approval
- [3.2] Guard: Only Igor (approved_by == "Igor") can approve tasks
- [3.3] Test: Approved tasks execute, unapproved tasks return PENDING_IGOR_APPROVAL error

✅ PHASE 3 DEFINITION OF DONE:
- [ ] High-risk tools blocked without approval
- [ ] Only Igor can approve (validated in ApprovalManager)
- [ ] Approved tasks execute, unapproved tasks fail deterministically

============================================================================

PHASE 4 ACTIONS (GMP-L.3 SPECIFIC):

- [4.1] Positive: gmp_run() enqueues task with status="pending_igor_approval"
- [4.2] Positive: git_commit() enqueues task with status="pending_igor_approval"
- [4.3] Negative: Non-Igor approval attempt returns False
- [4.4] Regression: Existing tool dispatch still works for non-high-risk tools

✅ PHASE 4 DEFINITION OF DONE:
- [ ] Positive validation passed (enqueue behavior correct)
- [ ] Negative validation passed (unauthorized approval rejected)
- [ ] Regression validation passed (non-high-risk tools unaffected)

============================================================================

PHASE 5 & 6: [SAME AS GMP-L.2]

============================================================================

FINAL DEFINITION OF DONE (TOTAL, NON-NEGOTIABLE)

✓ PHASE 0–6 completed and documented
✓ TODO PLAN was locked and followed exactly
✓ Every TODO ID has closure evidence (implementation + enforcement + validation where required)
✓ No changes occurred outside TODO scope
✓ No assumptions were made
✓ No freelancing, refactoring, or invention occurred
✓ Recursive verification (PHASE 5) passed
✓ Report written to required path in required format
✓ Final declaration written verbatim

============================================================================

FINAL DECLARATION (REQUIRED IN REPORT)

> All phases (0–6) complete. No assumptions. No drift. Scope locked. Execution terminated.
> GMP-L.3 (Approval Gate Infrastructure) is complete and verified.
> Output verified. Report stored at `/l9/reports/exec_report_gmp_l3_approvals.md`.
> High-risk tools now require Igor approval. Approval queue operational.
> Prerequisites met for GMP-L.4 (Long-Plan Integration).
> No further changes are permitted.

============================================================================

END OF GMP-L.3 CANONICAL GOD-MODE PROMPT v1.1
