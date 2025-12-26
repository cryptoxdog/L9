============================================================================
GOD-MODE CURSOR PROMPT — L9 GMP v1.7 CORRECTIVE (DETERMINISTIC, LOCKED, COMPREHENSIVE)
============================================================================

PURPOSE:
• Fix 3 critical code issues found in Stage 2 deep code analysis
• Add proper stub implementations with explicit Stage 2 deferral markers
• Create documentation files (DEFERRED_FEATURES.md, TODO_MAPPING.md)
• Update 6 execution reports with clarification notes
• Clear repo for VPS deployment with no silent failures

============================================================================

ROLE
You are a constrained execution agent operating inside the L9 Secure AI OS repository at `/Users/ib-mac/Projects/L9/`.  
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
• Add logging, optimization, comments, abstractions, or formatting changes beyond what's specified
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

• All file paths must be absolute and under `/Users/ib-mac/Projects/L9/`  
• Any change must preserve L9 architecture invariants unless explicitly planned:
  - Kernel/agent execution flows are not rewritten by default
  - Memory substrate (Postgres/Redis/Neo4j bindings) is not altered by default
  - WebSocket orchestration foundations are not altered by default
  - Entry points and docker-compose services are not modified by default
• If any requested change implies touching these invariants, it MUST appear in Phase 0 TODO plan.

============================================================================

STRUCTURED OUTPUT REQUIREMENTS (SINGLE ARTIFACT)

All output from this work MUST be written to a single markdown file:

```text
Path: /Users/ib-mac/Projects/L9/reports/exec_report_gmp_v1.7_corrective.md
```

The report MUST contain the following sections in this exact order:

1. `# EXECUTION REPORT — GMP v1.7 CORRECTIVE`  
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

PHASE 0 — RESEARCH & ANALYSIS + TODO PLAN LOCK

PURPOSE:
• Establish ground truth inside `/Users/ib-mac/Projects/L9/`  
• Produce a deterministic, auditable TODO plan  
• Lock scope before edits begin  

ACTIONS:
• Inspect all relevant files and code paths within `/Users/ib-mac/Projects/L9/`  
• Locate exact functions/blocks targeted  
• Create the TODO plan in locked format below  
• Create a TODO INDEX HASH (deterministic checksum string based on TODO text)  
• Create the report file at `/Users/ib-mac/Projects/L9/reports/exec_report_gmp_v1.7_corrective.md` and write sections 1–3  

REQUIRED TODO FORMAT:

```markdown
## TODO PLAN (LOCKED)
Each TODO item MUST include:
- Unique TODO ID (e.g., [v1.7-001])
- Absolute file path under /Users/ib-mac/Projects/L9/
- Line number OR explicit line range
- Action verb (Replace | Insert | Delete | Wrap | Move | Create)
- Target structure (function/class/block)
- Expected new behavior (one sentence max)
- Optional gating mechanism (flag/condition) if applicable
- Imports: NONE or list of exact new imports (must be minimal)

Example TODO item format:
- [v1.7-001] File: `/Users/ib-mac/Projects/L9/runtime/mcp_client.py` Lines: 177–225 Action: Replace Target: `call_tool()` method
      Change: Replace error return dict to include "stage": "deferred_to_stage_2" and proper error structure
      Gate: None
      Imports: NONE
```

TODO VALIDITY RULES (MANDATORY):
• No TODO may contain "maybe", "likely", "should", "consider", or speculation  
• No TODO may omit file path, lines, action verb, or target structure  
• No TODO may bundle unrelated operations  
• Each TODO must be independently checkable and directly observable  

PLAN LOCK:
• Once the TODO plan is written, it is immutable  
• If any plan item needs revision: STOP and restart Phase 0  

✅ PHASE 0 DEFINITION OF DONE:
- [ ] Report file created at `/Users/ib-mac/Projects/L9/reports/exec_report_gmp_v1.7_corrective.md`
- [ ] TODO PLAN is complete and valid (all required fields present)
- [ ] TODO PLAN contains only observable and executable items
- [ ] TODO INDEX HASH is generated and written to report
- [ ] No modifications made to repo
- [ ] Phase 0 output written to report sections 1–3

❌ FAIL RULE:
If any TODO item is underspecified or unverifiable, STOP immediately.

============================================================================

PHASE 1 — BASELINE CONFIRMATION

PURPOSE:
• Verify the TODO plan matches the repo state  
• Prevent assumptions and mismatched edits  
• Confirm all targets exist exactly as planned  

ACTIONS:
• Open each file referenced by TODOs  
• Confirm line anchors exist and match described structures  
• Confirm required symbols/imports/config references are present  
• Record baseline confirmation per TODO ID in report section 4  

✅ PHASE 1 DEFINITION OF DONE:
- [ ] Every TODO item verified to exist at described file+line
- [ ] Baseline results recorded per TODO ID
- [ ] No assumptions required to interpret target code
- [ ] Phase 1 checklist written to report section 4

❌ FAIL RULE:
If any TODO target does not match reality, STOP and return to Phase 0.

============================================================================

PHASE 2 — IMPLEMENTATION

PURPOSE:
• Apply only the locked TODO changes  
• Ensure zero drift outside scope  
• Preserve L9 patterns and structure unless explicitly planned  

ACTIONS:
• Execute TODO items in numeric order  
• Modify only the described files and line ranges  
• Make minimal edits required for the requested change  
• Do not touch unrelated code  
• Enforce import locking:
  - No new imports unless explicitly listed per TODO item
• Enforce META header compliance (only in modified files):
  - Python modules must preserve canonical docstring header format
  - YAML files must preserve canonical META block format including path+filename
  - Use Date Created / Last Modified fields where applicable
• Record exact line ranges changed per TODO ID into report section 5  

✅ PHASE 2 DEFINITION OF DONE:
- [ ] Every TODO ID implemented
- [ ] Only TODO-listed files were modified
- [ ] Only TODO-listed line ranges were modified
- [ ] No extra imports added beyond TODO-declared imports
- [ ] META headers remain compliant for each modified file (if present)
- [ ] Exact line ranges changed recorded in report section 5
- [ ] TODO → CHANGE map drafted in report section 6

❌ FAIL RULE:
If any change cannot be traced to a TODO ID, STOP immediately.

============================================================================

PHASE 3 — ENFORCEMENT (GUARDS / TESTS)

PURPOSE:
• Ensure required behavior cannot silently regress  
• Add enforcement only if required by TODOs  
• Produce deterministic pass/fail evidence  

ACTIONS:
• Add guards, validation, or tests ONLY if explicitly listed in TODO plan  
• If enforcement was not requested, do not invent it  
• Ensure enforcement is deterministic (no flaky behavior)  
• Record enforcement mechanism per TODO ID into report section 7  

✅ PHASE 3 DEFINITION OF DONE:
- [ ] Enforcement exists ONLY where TODO plan requires it
- [ ] Enforcement is deterministic
- [ ] Removing enforcement causes failure (where applicable)
- [ ] Enforcement results written to report section 7

❌ FAIL RULE:
If enforcement requires new scope or new TODOs, STOP and restart Phase 0.

============================================================================

PHASE 4 — VALIDATION (POSITIVE / NEGATIVE / REGRESSION)

PURPOSE:
• Confirm implementation works as requested  
• Confirm failure modes are correct  
• Confirm no regressions introduced  

ACTIONS:
• Run required validations (tests/build/lint/smoke checks) ONLY if listed in TODOs  
• Perform negative test only if listed in TODOs  
• Perform regression test only if listed in TODOs  
• Record validation results per TODO ID into report section 7  

✅ PHASE 4 DEFINITION OF DONE:
- [ ] Positive validation passed where required by TODOs
- [ ] Negative validation passed where required by TODOs
- [ ] Regression validation passed where required by TODOs
- [ ] Results recorded per TODO ID in report section 7

❌ FAIL RULE:
If any validation fails, STOP. Do not "fix forward" unless a TODO explicitly permits it.

============================================================================

PHASE 5 — RECURSIVE SELF-VALIDATION (SCOPE + COMPLETENESS PROOF)

PURPOSE:
• Prove that all work matches the locked TODO plan  
• Detect drift, unauthorized edits, missing enforcement, or incomplete closure  
• Verify report completeness before final output is considered valid  

ACTIONS:
• Compare every modified file to TODO scope  
• Confirm every TODO ID appears in:
  - Implementation evidence
  - Enforcement evidence (if applicable)
  - Validation evidence (if applicable)
  - Report mappings
• Confirm no files were modified outside scope  
• Confirm no changes exist that lack a TODO ID  
• Confirm report includes all required sections in correct order  
• Confirm checklists were not pre-checked without evidence  

✅ PHASE 5 DEFINITION OF DONE:
- [ ] Every TODO ID maps to a verified code change
- [ ] Every TODO ID has closure evidence (implemented/enforced/validated where required)
- [ ] No unauthorized diffs exist
- [ ] No assumptions used
- [ ] Report structure verified complete
- [ ] Checklist marking policy respected
- [ ] Phase 5 results written to report section 8

❌ FAIL RULE:
If any TODO lacks closure evidence, STOP. Report is invalid until corrected.

============================================================================

PHASE 6 — FINAL AUDIT + REPORT FINALIZATION

PURPOSE:
• Freeze final state  
• Produce the final required report artifact  
• Emit final completion declaration  
• Ensure the report is the single authoritative output  

ACTIONS:
• Write final sections into the report:
  - Final Definition of Done (Total)
  - Final Declaration
• Reconfirm the report path is correct  
• Confirm no placeholders exist  
• Confirm all required checklists are completed with evidence  

✅ PHASE 6 DEFINITION OF DONE:
- [ ] Report exists at required path `/Users/ib-mac/Projects/L9/reports/exec_report_gmp_v1.7_corrective.md`
- [ ] All required sections exist in correct order
- [ ] All sections contain real data (no placeholders)
- [ ] Final Definition of Done included and satisfied
- [ ] Final Declaration present verbatim

❌ FAIL RULE:
If the report is incomplete or contains placeholders, STOP.

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
> Output verified. Report stored at `/Users/ib-mac/Projects/L9/reports/exec_report_gmp_v1.7_corrective.md`.  
> No further changes are permitted.

============================================================================

SPECIFIC REQUIREMENTS FROM GMP_v1.7_CORRECTIVE.md

The following fixes MUST be implemented exactly as specified:

### TODO-v1.7-001: Fix MCP Protocol Implementation
**File**: `runtime/mcp_client.py` → `call_tool()` method (lines 177–225)
**Action**: Replace the error return dict to include:
- "success": False
- "error": "MCP JSON-RPC protocol not yet implemented — deferred to Stage 2"
- "server": server_id
- "tool": tool_name
- "stage": "deferred_to_stage_2"

Also update the two early return error dicts (lines 194–198 and 200–204) to include "stage": "deferred_to_stage_2".

Update the docstring to include "DEFERRED TO STAGE 2: Full MCP JSON-RPC protocol implementation."

Update the logger.warning call to match the format specified.

### TODO-v1.7-002: Fix GMP Execution Runner
**File**: `runtime/gmp_worker.py` → `_run_gmp()` method (lines 146–181)
**Action**: Replace the error return dict to include:
- "success": False
- "status": "deferred_to_stage_2"
- "error": "GMP Cursor integration not yet available — deferred to Stage 2"
- "queued": True
- "task_details": { "caller": caller, "repo_root": repo_root, "gmp_preview": ... }

Update the docstring to include "DEFERRED TO STAGE 2: Integration with Cursor runner..."

Update the logger.info call to match the format specified.

### TODO-v1.7-003: Update Long Plan DAG Functions
**File**: `orchestration/long_plan_graph.py`
**Action**: Update `execute_long_plan()` (lines 447–534) and `simulate_long_plan()` (lines 537–571) to return proper error dicts with "status": "deferred_to_stage_2" when LangGraph is not available or when execution fails.

Note: The functions already exist, but need to be updated to return the proper error format as specified in the corrective document.

Also ensure `build_long_plan_graph()` (lines 406–440) returns None with proper warning logs when LangGraph is not available.

### TODO-v1.7-004: Create DEFERRED_FEATURES.md
**File**: New → `/Users/ib-mac/Projects/L9/DEFERRED_FEATURES.md`
**Action**: Create file with content from GMP_v1.7_CORRECTIVE.md Phase 2 → TODO-v1.7-004

### TODO-v1.7-005: Create TODO_MAPPING.md
**File**: New → `/Users/ib-mac/Projects/L9/TODO_MAPPING.md`
**Action**: Create file with content from GMP_v1.7_CORRECTIVE.md Phase 2 → TODO-v1.7-005

### TODO-v1.7-006: Update Reports with Clarification Notes
**Files**: 
- `/Users/ib-mac/Projects/L9/reports/exec_report_gmp_l2_metadata.md`
- `/Users/ib-mac/Projects/L9/reports/exec_report_gmp_l3_approvals.md`
- `/Users/ib-mac/Projects/L9/reports/exec_report_gmp_l4_longplan.md`
- `/Users/ib-mac/Projects/L9/reports/exec_report_gmp_l5_dispatch.md`
- `/Users/ib-mac/Projects/L9/reports/exec_report_gmp_l6_memory.md`
- `/Users/ib-mac/Projects/L9/reports/exec_report_gmp_l7_bootstrap.md`

**Action**: Add clarification section at the top of "AREAS FOR IMPROVEMENT" section (or create it if it doesn't exist) with content from GMP_v1.7_CORRECTIVE.md Phase 3 → TODO-v1.7-006

============================================================================

