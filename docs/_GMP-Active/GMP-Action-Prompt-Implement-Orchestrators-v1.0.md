============================================================================
GOD-MODE CURSOR PROMPT — IMPLEMENT MEMORY & ACTION TOOL ORCHESTRATORS V1.0
============================================================================

PURPOSE:
• Implement actual orchestration logic for MemoryOrchestrator and ActionToolOrchestrator
• Replace stub implementations with production-ready code
• Wire orchestrators into L9 system for active use
• Follow interface contracts defined in respective interface.py files

============================================================================

ROLE
You are a constrained execution agent operating inside the L9 Secure AI OS repository at `/Users/ib-mac/Projects/L9/`.  
You execute deterministically.  
You do not redesign architecture.  
You do not invent requirements.  
You modify only the files, line ranges, and behaviors specified in the TODO plan.  
You do not freelance.

============================================================================

MODIFICATION LOCK — ABSOLUTE

❌ YOU MAY NOT:
• Add features not in the TODO plan
• Modify files or lines outside the TODO plan
• Alter imports beyond what each TODO explicitly allows
• Change function signatures that break interface contracts
• Skip enforcement or validation steps
• Leave any TODO incomplete

✅ YOU MAY ONLY:
• Execute the TODO plan exactly as written
• Use only the action verbs: Replace | Insert | Delete | Wrap | Move | Create
• Add imports listed in the TODO (must be minimal, no new deps)
• Write to the report file
• Stop if any step fails

============================================================================

L9-SPECIFIC OPERATING CONSTRAINTS (NON-NEGOTIABLE)

• All paths are absolute under `/Users/ib-mac/Projects/L9/`
• Preserve existing interface contracts (MemoryRequest/Response, ActionToolRequest/Response)
• Use structlog for all logging
• Use async/await for all I/O operations
• Preserve YAML META comments if present
• Memory substrate integration via existing imports only

============================================================================

STRUCTURED OUTPUT REQUIREMENTS

Report MUST be written to:
```text
Path: /Users/ib-mac/Projects/L9/reports/GMP_Report_Implement_Orchestrators_v1.0.md
```

Report MUST contain:
1. TODO PLAN (copy of locked plan)
2. TODO INDEX HASH
3. Phase checklist status (Phases 0–6)
4. Files modified + line ranges
5. TODO → change map (each TODO ID linked to actual file change)
6. Enforcement + validation results
7. Final declaration (verbatim, no paraphrase)

============================================================================

## TODO PLAN (LOCKED)

### [v1.0-001] IMPLEMENT MemoryOrchestrator.execute() — BATCH_WRITE operation
- **File:** `/Users/ib-mac/Projects/L9/orchestrators/memory/orchestrator.py`
- **Lines:** 30-42 (replace entire execute method)
- **Action:** Replace
- **Target:** `execute()` method
- **Change:** Implement dispatch to `_batch_write()`, `_replay()`, `_gc()`, `_compact()` based on operation type
- **Gate:** NONE
- **Imports:** `from typing import List, Dict, Any`

### [v1.0-002] ADD MemoryOrchestrator._batch_write() method
- **File:** `/Users/ib-mac/Projects/L9/orchestrators/memory/orchestrator.py`
- **Lines:** 43+ (insert after execute method)
- **Action:** Insert
- **Target:** New `_batch_write()` method
- **Change:** Implement batch packet writing with memory substrate integration
- **Gate:** NONE
- **Imports:** NONE

### [v1.0-003] ADD MemoryOrchestrator._replay() method
- **File:** `/Users/ib-mac/Projects/L9/orchestrators/memory/orchestrator.py`
- **Lines:** After _batch_write
- **Action:** Insert
- **Target:** New `_replay()` method
- **Change:** Implement replay of packets from specified time range
- **Gate:** NONE
- **Imports:** `from datetime import datetime, timedelta`

### [v1.0-004] ADD MemoryOrchestrator._gc() method
- **File:** `/Users/ib-mac/Projects/L9/orchestrators/memory/orchestrator.py`
- **Lines:** After _replay
- **Action:** Insert
- **Target:** New `_gc()` method
- **Change:** Implement garbage collection of packets older than threshold
- **Gate:** NONE
- **Imports:** NONE

### [v1.0-005] ADD MemoryOrchestrator._compact() method
- **File:** `/Users/ib-mac/Projects/L9/orchestrators/memory/orchestrator.py`
- **Lines:** After _gc
- **Action:** Insert
- **Target:** New `_compact()` method
- **Change:** Implement packet compaction (merge duplicate/related packets)
- **Gate:** NONE
- **Imports:** NONE

### [v1.0-006] IMPLEMENT ActionToolOrchestrator.execute() — full dispatch
- **File:** `/Users/ib-mac/Projects/L9/orchestrators/action_tool/orchestrator.py`
- **Lines:** 30-42 (replace entire execute method)
- **Action:** Replace
- **Target:** `execute()` method
- **Change:** Implement tool validation, safety check, execution with retries, and packet logging
- **Gate:** NONE
- **Imports:** `from typing import Dict, Any, Optional`

### [v1.0-007] ADD ActionToolOrchestrator._validate_tool() method
- **File:** `/Users/ib-mac/Projects/L9/orchestrators/action_tool/orchestrator.py`
- **Lines:** 43+ (insert after execute method)
- **Action:** Insert
- **Target:** New `_validate_tool()` method
- **Change:** Validate tool_id exists and arguments match expected schema
- **Gate:** NONE
- **Imports:** NONE

### [v1.0-008] ADD ActionToolOrchestrator._assess_safety() method
- **File:** `/Users/ib-mac/Projects/L9/orchestrators/action_tool/orchestrator.py`
- **Lines:** After _validate_tool
- **Action:** Insert
- **Target:** New `_assess_safety()` method
- **Change:** Assess tool safety level based on tool_id and arguments
- **Gate:** NONE
- **Imports:** NONE

### [v1.0-009] ADD ActionToolOrchestrator._execute_with_retry() method
- **File:** `/Users/ib-mac/Projects/L9/orchestrators/action_tool/orchestrator.py`
- **Lines:** After _assess_safety
- **Action:** Insert
- **Target:** New `_execute_with_retry()` method
- **Change:** Execute tool with retry logic up to max_retries
- **Gate:** NONE
- **Imports:** `import asyncio`

### [v1.0-010] ADD ActionToolOrchestrator._log_tool_packet() method
- **File:** `/Users/ib-mac/Projects/L9/orchestrators/action_tool/orchestrator.py`
- **Lines:** After _execute_with_retry
- **Action:** Insert
- **Target:** New `_log_tool_packet()` method
- **Change:** Log tool execution as packet to memory substrate
- **Gate:** NONE
- **Imports:** NONE

============================================================================

## TODO INDEX HASH

```
[LOCKED]
TODO_0: memory_orchestrator_execute_replace_30_42
TODO_1: memory_orchestrator_batch_write_insert
TODO_2: memory_orchestrator_replay_insert
TODO_3: memory_orchestrator_gc_insert
TODO_4: memory_orchestrator_compact_insert
TODO_5: action_tool_orchestrator_execute_replace_30_42
TODO_6: action_tool_validate_tool_insert
TODO_7: action_tool_assess_safety_insert
TODO_8: action_tool_execute_retry_insert
TODO_9: action_tool_log_packet_insert
HASH: gmp_implement_orchestrators_v1_20251226
```

============================================================================

## PHASE 0 — RESEARCH & ANALYSIS + TODO PLAN LOCK

- [ ] Read interface files to confirm method signatures
- [ ] Verify existing stub implementations
- [ ] Confirm no conflicts with existing code
- [ ] TODO plan locked (all 10 TODOs defined)
- [ ] TODO INDEX HASH generated
- [ ] Report file created

✅ **Status:** READY FOR EXECUTION

============================================================================

## PHASE 1 — BASELINE CONFIRMATION

- [ ] Verify `/Users/ib-mac/Projects/L9/orchestrators/memory/orchestrator.py` exists
- [ ] Verify `/Users/ib-mac/Projects/L9/orchestrators/action_tool/orchestrator.py` exists
- [ ] Confirm stub implementations at expected lines
- [ ] Confirm interface contracts match

============================================================================

## PHASE 2 — IMPLEMENTATION

- [ ] TODO [v1.0-001]: Replace MemoryOrchestrator.execute()
- [ ] TODO [v1.0-002]: Insert _batch_write()
- [ ] TODO [v1.0-003]: Insert _replay()
- [ ] TODO [v1.0-004]: Insert _gc()
- [ ] TODO [v1.0-005]: Insert _compact()
- [ ] TODO [v1.0-006]: Replace ActionToolOrchestrator.execute()
- [ ] TODO [v1.0-007]: Insert _validate_tool()
- [ ] TODO [v1.0-008]: Insert _assess_safety()
- [ ] TODO [v1.0-009]: Insert _execute_with_retry()
- [ ] TODO [v1.0-010]: Insert _log_tool_packet()
- [ ] Record exact line ranges changed
- [ ] Zero drift outside scope

============================================================================

## PHASE 3 — ENFORCEMENT (GUARDS / TESTS)

- [ ] All methods have proper error handling
- [ ] All methods return correct response types
- [ ] Logging present in all methods
- [ ] Retry logic has backoff

============================================================================

## PHASE 4 — VALIDATION

- [ ] Run syntax check: `python3 ci/check_syntax.py`
- [ ] Run lint check: `python3 ci/lint_forbidden_imports.py`
- [ ] Verify no import errors
- [ ] Record validation output

============================================================================

## PHASE 5 — RECURSIVE VERIFICATION

- [ ] Compare modified files to TODO scope
- [ ] Confirm every TODO ID has closure evidence
- [ ] Confirm no unauthorized diffs exist
- [ ] Confirm no changes outside plan

============================================================================

## PHASE 6 — FINAL AUDIT + REPORT FINALIZATION

- [ ] Report exists at `/Users/ib-mac/Projects/L9/reports/GMP_Report_Implement_Orchestrators_v1.0.md`
- [ ] All sections complete with real data
- [ ] No placeholders remain
- [ ] Final Declaration present verbatim

============================================================================

## FINAL DEFINITION OF DONE (TOTAL)

✅ **Required for completion:**

- [ ] PHASE 0–6 completed and documented
- [ ] TODO PLAN locked with exact file paths/lines
- [ ] Every TODO ID has closure evidence (implementation + enforcement + validation)
- [ ] No changes outside TODO scope
- [ ] No assumptions made (all ground truth verified)
- [ ] Recursive verification (PHASE 5) passed
- [ ] Report written to `/Users/ib-mac/Projects/L9/reports/GMP_Report_Implement_Orchestrators_v1.0.md`
- [ ] Final declaration written verbatim

============================================================================

## FINAL DECLARATION

> GMP action prompt generated. All requirements extracted. Format compliant. Ready for execution.  
> Prompt stored at `/Users/ib-mac/Projects/L9/docs/_GMP-Active/GMP-Action-Prompt-Implement-Orchestrators-v1.0.md`.  
> No further modifications needed.

============================================================================

## SPECIFIC REQUIREMENTS — IMPLEMENTATION DETAILS

### MemoryOrchestrator Implementation

**Operations to implement:**
1. `BATCH_WRITE` — Write multiple packets to memory substrate in batch
2. `REPLAY` — Replay packets from a time range (for debugging/recovery)
3. `GC` — Garbage collect packets older than threshold_days
4. `COMPACT` — Merge duplicate/related packets to reduce storage

**Integration points:**
- Use `memory.substrate_service.get_service()` for substrate access
- Use `PacketEnvelopeIn` for packet creation
- Respect existing memory substrate API

### ActionToolOrchestrator Implementation

**Flow:**
1. Validate tool_id exists in tool registry
2. Assess safety level (SAFE, REQUIRES_APPROVAL, DANGEROUS)
3. If REQUIRES_APPROVAL and not approved, return early
4. Execute tool with retry logic (exponential backoff)
5. Log execution as packet to memory substrate

**Safety classification:**
- SAFE: read-only tools, queries
- REQUIRES_APPROVAL: file writes, API calls
- DANGEROUS: system commands, destructive operations

**Retry logic:**
- Max retries from request (default 3)
- Exponential backoff: 1s, 2s, 4s
- Log each retry attempt

============================================================================

