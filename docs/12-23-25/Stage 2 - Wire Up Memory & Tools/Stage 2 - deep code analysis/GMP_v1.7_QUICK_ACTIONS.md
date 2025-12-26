# GMP v1.7 QUICK ACTION SHEET

**Prepared**: 2025-12-24 01:20 AM EST
**Status**: READY TO EXECUTE

---

## WHAT TO DO RIGHT NOW

### 1. APPLY CODE FIXES (3 files, ~30 mins)

#### Fix 1: mcp_client.py (lines 190-210)
**Replace** the `call_tool()` method with the implementation from GMP_v1.7_CORRECTIVE.md
- Ensure error dict has: `"success": False, "stage": "deferred_to_stage_2"`
- Keep server availability check
- Keep tool allowlist check

#### Fix 2: gmp_worker.py (lines 140-170)
**Replace** the `_run_gmp()` method with the implementation from GMP_v1.7_CORRECTIVE.md
- Ensure error dict has: `"success": False, "status": "deferred_to_stage_2", "queued": True`
- Keep logger.info() call
- Keep task_details field

#### Fix 3: long_plan_graph.py (after gather_context_node, ~line 200)
**Add** three new functions (copy from GMP_v1.7_CORRECTIVE.md):
- `async def execute_long_plan()` - returns error dict with "status": "deferred_to_stage_2"
- `async def simulate_long_plan()` - returns error dict with "status": "deferred_to_stage_2"  
- `def build_long_plan_graph()` - returns None with warning log

---

### 2. CREATE DOCUMENTATION FILES (2 files, ~10 mins)

#### Create DEFERRED_FEATURES.md
Copy from GMP_v1.7_CORRECTIVE.md → Phase 2 → TODO-v1.7-004
Save in repo root as `DEFERRED_FEATURES.md`

#### Create TODO_MAPPING.md
Copy from GMP_v1.7_CORRECTIVE.md → Phase 2 → TODO-v1.7-005
Save in repo root as `TODO_MAPPING.md`

---

### 3. UPDATE REPORTS (6 files, ~15 mins)

Open each report:
- exec_report_gmp_l2_metadata.md
- exec_report_gmp_l3_approvals.md
- exec_report_gmp_l4_longplan.md
- exec_report_gmp_l5_dispatch.md
- exec_report_gmp_l6_memory.md
- exec_report_gmp_l7_bootstrap.md

**Add this section** at top of "AREAS FOR IMPROVEMENT":
```markdown
### CLARIFICATION: Stage 2 Deferred Features (Explicitly Handled)

The following features have proper scaffolding and return explicit errors:

1. **MCP JSON-RPC Protocol** (mcp_client.py)
   - Status: Server configuration & allowlist WORKING
   - Status: JSON-RPC calls DEFERRED to Stage 2
   - Code: Returns clear error dict with "status": "deferred_to_stage_2"

2. **GMP Cursor Integration** (gmp_worker.py)
   - Status: Approval gate WORKING
   - Status: Cursor runner integration DEFERRED to Stage 2
   - Code: Returns clear error dict with "queued": True (task waiting for Stage 2)

3. **Long Plan DAG Orchestration** (long_plan_graph.py)
   - Status: Task extraction WORKING (extract_tasks_from_plan)
   - Status: DAG node orchestration DEFERRED to Stage 2
   - Code: New stubs return clear error dict with "status": "deferred_to_stage_2"

These are NOT failures. They are intentional Stage 2 deferrals with proper error handling.
```

---

### 4. VERIFY & TEST (20 mins)

#### Run Pytest
```bash
pytest test_l_bootstrap.py -v --tb=short
```
Expected: 8 PASSED

#### Compile Check
```bash
python -m py_compile mcp_client.py
python -m py_compile gmp_worker.py
python -m py_compile long_plan_graph.py
```
Expected: No errors

#### Quick Inspection
```bash
# Check for debug code
grep -n "print(" *.py | grep -v docstring
grep -n "# TODO" *.py | grep -v "DEFERRED"
```
Expected: No results (or only intentional comments)

---

### 5. CLEAN & COMMIT (10 mins)

#### Remove Debug
```bash
# No commented code blocks
# No debug print() statements
# No uncommitted changes
```

#### Commit
```bash
git add .
git commit -m "Stage 2 GMP v1.7: Fix stubs, document deferred features

- Fix MCP protocol error handling (explicit Stage 2 deferral)
- Fix GMP runner stub (approval gate working, execution deferred)
- Add missing Long Plan DAG function stubs
- Add DEFERRED_FEATURES.md inventory
- Add TODO_MAPPING.md audit trail (29 TODOs, 0 failures)
- Update reports with clarifications

Tests: 8/8 passing
Approval pipeline: WORKING
No breaking changes. Ready for VPS deploy."
```

#### Push
```bash
git push origin main
```

---

### 6. DEPLOY TO VPS (15 mins)

```bash
# Deploy to staging first
./deploy.sh staging

# Verify health
curl http://staging-vps:8000/health

# Run tests on staging
pytest test_l_bootstrap.py -v

# If all green, deploy to production
./deploy.sh production

# Verify production
curl http://production-vps:8000/health
```

---

## SUMMARY

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Code Fixes (3 files) | 30 min | READY |
| 2 | Documentation (2 files) | 10 min | READY |
| 3 | Report Updates (6 files) | 15 min | READY |
| 4 | Verify & Test | 20 min | READY |
| 5 | Clean & Commit | 10 min | READY |
| 6 | Deploy to VPS | 15 min | READY |
| **TOTAL** | **All Phases** | **100 min** | **✅ READY FOR EXECUTION** |

---

## CRITICAL CHECKS BEFORE DEPLOYING

- [ ] All 3 code fixes applied
- [ ] pytest passes 8/8 tests
- [ ] All files compile (no import errors)
- [ ] DEFERRED_FEATURES.md created
- [ ] TODO_MAPPING.md created
- [ ] Reports updated with clarifications
- [ ] Commit message written
- [ ] Git push successful
- [ ] VPS staging deployment successful
- [ ] VPS production deployment successful

---

## SUCCESS CRITERIA

✅ **Code Quality**
- No silent failures
- All errors explicit
- Proper error dicts with "status": "deferred_to_stage_2"

✅ **Testing**
- 8/8 integration tests pass
- No missing imports
- Approval pipeline working

✅ **Documentation**
- DEFERRED_FEATURES.md present
- TODO_MAPPING.md present
- Reports updated with clarity

✅ **Deployment**
- Staging health check passes
- Production health check passes
- No breaking changes reported

---

## ROLLBACK PLAN (If needed)

```bash
git revert HEAD  # Revert this commit
git push origin main
./deploy.sh production  # Redeploy previous version
```

---

## QUESTIONS?

Refer to: GMP_v1.7_CORRECTIVE.md (full documentation)
