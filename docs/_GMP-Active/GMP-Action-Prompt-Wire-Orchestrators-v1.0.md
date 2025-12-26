============================================================================
GOD-MODE CURSOR PROMPT — WIRE ORCHESTRATORS TO ENDPOINTS V1.0
============================================================================

PURPOSE:
• Wire MemoryOrchestrator to /memory/batch, /memory/gc, /memory/compact endpoints
• Wire ActionToolOrchestrator to /tools/execute endpoint
• Add explicit WorldModelService initialization at startup
• Complete the orchestrator integration layer

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
• Preserve existing API patterns (FastAPI, Depends, Header auth)
• Use structlog for all logging
• Use async/await for all I/O operations
• Orchestrators accessed via app.state.*
• Memory substrate integration via existing imports only

============================================================================

STRUCTURED OUTPUT REQUIREMENTS

Report MUST be written to:
```text
Path: /Users/ib-mac/Projects/L9/reports/GMP_Report_Wire_Orchestrators_v1.0.md
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

### [v1.0-001] ADD /memory/batch endpoint
- **File:** `/Users/ib-mac/Projects/L9/api/memory/router.py`
- **Lines:** After line 150 (end of file)
- **Action:** Insert
- **Target:** New `POST /batch` endpoint
- **Change:** Add endpoint that accepts list of packets, calls MemoryOrchestrator.execute(BATCH_WRITE)
- **Gate:** NONE
- **Imports:** `from orchestrators.memory.interface import MemoryRequest, MemoryOperation`

### [v1.0-002] ADD /memory/gc endpoint
- **File:** `/Users/ib-mac/Projects/L9/api/memory/router.py`
- **Lines:** After /batch endpoint
- **Action:** Insert
- **Target:** New `POST /gc` endpoint
- **Change:** Add endpoint that triggers garbage collection via MemoryOrchestrator.execute(GC)
- **Gate:** NONE
- **Imports:** NONE (already imported in v1.0-001)

### [v1.0-003] ADD /memory/compact endpoint
- **File:** `/Users/ib-mac/Projects/L9/api/memory/router.py`
- **Lines:** After /gc endpoint
- **Action:** Insert
- **Target:** New `POST /compact` endpoint
- **Change:** Add endpoint that triggers compaction via MemoryOrchestrator.execute(COMPACT)
- **Gate:** NONE
- **Imports:** NONE

### [v1.0-004] ADD get_memory_orchestrator dependency
- **File:** `/Users/ib-mac/Projects/L9/api/memory/router.py`
- **Lines:** After imports (around line 18)
- **Action:** Insert
- **Target:** New dependency function
- **Change:** Add function to get MemoryOrchestrator from app.state
- **Gate:** NONE
- **Imports:** `from fastapi import Request`

### [v1.0-005] CREATE /api/tools/router.py
- **File:** `/Users/ib-mac/Projects/L9/api/tools/router.py`
- **Lines:** New file
- **Action:** Create
- **Target:** New router module for tool endpoints
- **Change:** Create FastAPI router with POST /execute endpoint that calls ActionToolOrchestrator
- **Gate:** NONE
- **Imports:** Full imports for new file

### [v1.0-006] CREATE /api/tools/__init__.py
- **File:** `/Users/ib-mac/Projects/L9/api/tools/__init__.py`
- **Lines:** New file
- **Action:** Create
- **Target:** Package init
- **Change:** Export router
- **Gate:** NONE
- **Imports:** NONE

### [v1.0-007] REGISTER tools router in server.py
- **File:** `/Users/ib-mac/Projects/L9/api/server.py`
- **Lines:** Find router registration section (~line 80-100)
- **Action:** Insert
- **Target:** Router registration
- **Change:** Add `from api.tools.router import router as tools_router` and `app.include_router(tools_router, prefix="/tools")`
- **Gate:** NONE
- **Imports:** See above

### [v1.0-008] ADD WorldModelService initialization at startup
- **File:** `/Users/ib-mac/Projects/L9/api/server.py`
- **Lines:** After memory service initialization (~line 235)
- **Action:** Insert
- **Target:** Startup lifespan
- **Change:** Add explicit WorldModelService initialization: `from world_model.service import get_world_model_service; world_model_service = get_world_model_service(); app.state.world_model_service = world_model_service`
- **Gate:** NONE
- **Imports:** See above

============================================================================

## TODO INDEX HASH

```
[LOCKED]
TODO_0: memory_router_batch_endpoint_insert_150
TODO_1: memory_router_gc_endpoint_insert
TODO_2: memory_router_compact_endpoint_insert
TODO_3: memory_router_orchestrator_dependency_insert
TODO_4: tools_router_create_new_file
TODO_5: tools_init_create_new_file
TODO_6: server_register_tools_router
TODO_7: server_worldmodel_service_init
HASH: gmp_wire_orchestrators_v1_20251226
```

============================================================================

## PHASE 0 — RESEARCH & ANALYSIS + TODO PLAN LOCK

- [ ] Read existing memory router to confirm structure
- [ ] Verify MemoryOrchestrator interface (MemoryRequest, MemoryOperation)
- [ ] Verify ActionToolOrchestrator interface (ActionToolRequest)
- [ ] Confirm server.py router registration pattern
- [ ] TODO plan locked (all 8 TODOs defined)
- [ ] TODO INDEX HASH generated
- [ ] Report file created

✅ **Status:** READY FOR EXECUTION

============================================================================

## PHASE 1 — BASELINE CONFIRMATION

- [ ] Verify `/Users/ib-mac/Projects/L9/api/memory/router.py` exists (150 lines)
- [ ] Verify `/Users/ib-mac/Projects/L9/api/server.py` exists
- [ ] Verify `/Users/ib-mac/Projects/L9/api/tools/` does NOT exist (will create)
- [ ] Confirm MemoryOrchestrator in app.state at startup
- [ ] Confirm ActionToolOrchestrator in app.state at startup

============================================================================

## PHASE 2 — IMPLEMENTATION

- [ ] TODO [v1.0-001]: Insert /batch endpoint
- [ ] TODO [v1.0-002]: Insert /gc endpoint
- [ ] TODO [v1.0-003]: Insert /compact endpoint
- [ ] TODO [v1.0-004]: Insert orchestrator dependency function
- [ ] TODO [v1.0-005]: Create tools/router.py
- [ ] TODO [v1.0-006]: Create tools/__init__.py
- [ ] TODO [v1.0-007]: Register tools router in server.py
- [ ] TODO [v1.0-008]: Add WorldModelService initialization
- [ ] Record exact line ranges changed
- [ ] Zero drift outside scope

============================================================================

## PHASE 3 — ENFORCEMENT (GUARDS / TESTS)

- [ ] All endpoints have proper error handling (try/except)
- [ ] All endpoints require API key auth (Depends(verify_api_key))
- [ ] All endpoints return proper response models
- [ ] Logging present in all handlers

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

- [ ] Report exists at `/Users/ib-mac/Projects/L9/reports/GMP_Report_Wire_Orchestrators_v1.0.md`
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
- [ ] Report written to `/Users/ib-mac/Projects/L9/reports/GMP_Report_Wire_Orchestrators_v1.0.md`
- [ ] Final declaration written verbatim

============================================================================

## FINAL DECLARATION

> GMP action prompt generated. All requirements extracted. Format compliant. Ready for execution.  
> Prompt stored at `/Users/ib-mac/Projects/L9/docs/_GMP-Active/GMP-Action-Prompt-Wire-Orchestrators-v1.0.md`.  
> No further modifications needed.

============================================================================

## SPECIFIC REQUIREMENTS — IMPLEMENTATION DETAILS

### Memory Router Endpoints

**POST /memory/batch**
- Request: `{ "packets": [...], "batch_size": 100 }`
- Calls: `MemoryOrchestrator.execute(MemoryRequest(operation=BATCH_WRITE, packets=...))`
- Response: `{ "success": true, "processed_count": N, "errors": [] }`

**POST /memory/gc**
- Request: `{ "threshold_days": 30 }`
- Calls: `MemoryOrchestrator.execute(MemoryRequest(operation=GC, gc_threshold_days=...))`
- Response: `{ "success": true, "deleted_count": N }`

**POST /memory/compact**
- Request: `{}`
- Calls: `MemoryOrchestrator.execute(MemoryRequest(operation=COMPACT))`
- Response: `{ "success": true, "compacted_count": N }`

### Tools Router Endpoints

**POST /tools/execute**
- Request: `{ "tool_id": "...", "arguments": {...}, "max_retries": 3, "require_approval": false }`
- Calls: `ActionToolOrchestrator.execute(ActionToolRequest(...))`
- Response: `{ "success": true, "result": {...}, "safety_level": "safe", "retries_used": 0 }`

### WorldModelService Initialization

At startup after memory service init:
```python
# Initialize WorldModelService explicitly (not lazy)
from world_model.service import get_world_model_service
world_model_service = get_world_model_service()
app.state.world_model_service = world_model_service
logger.info("WorldModelService initialized")
```

============================================================================

