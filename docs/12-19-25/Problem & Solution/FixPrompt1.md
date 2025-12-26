🧠 MISSION OBJECTIVE
Fix L9 kernel loading by consolidating duplicate loaders, 
merging them into runtime/, and wiring them into FastAPI startup.
Result: L-CTO agent loads all kernels at boot time.

============================================================================
PHASE -1 — ANALYSIS & PLANNING

TASK DECOMPOSITION:

1. Identify duplicate kernel loaders
   - runtime/kernelloader.py (CURRENT, HAS NEO4J SYNC)
   - core/kernels/privateloader.py (LEGACY, CONFLICTS)
   
2. Consolidate into single loader
   - Merge privateloader.py logic into runtime/kernelloader.py
   - Keep Neo4j sync from runtime version
   - Delete privateloader.py
   
3. Fix import paths
   - core/agents/kernelregistry.py imports from runtime.kernelloader ✓
   - Verify all imports updated
   
4. Wire kernel loader into FastAPI startup
   - Find api/server.py lifespan context manager
   - Add loadkernels() call in STARTUP section
   - Add requirekernelactivation() validation
   
5. Fix Slack integration
   - Add RateLimiter import to api/routes/slack.py
   - Initialize RateLimiter at startup
   - Check rate limits before processing Slack events
   
6. Validate & test
   - Docker restart container
   - Verify kernels loaded in logs
   - Confirm Slack responds without rate limit errors

DEPENDENCIES:
- runtime/kernelloader.py must be finalized BEFORE wiring
- api/server.py must be modified AFTER loader is ready

============================================================================
PHASE 0 — BASELINE CONFIRMATION

VERIFY THESE (DO NOT MODIFY):

☐ runtime/kernelloader.py exists and has loadkernels() function
☐ core/kernels/privateloader.py exists (will be deleted)
☐ api/server.py has asynccontextmanager def lifespan(app)
☐ core/agents/kernelregistry.py imports from runtime.kernelloader
☐ /opt/l9 directory structure matches repo structure

FAILURE RULE: If any check fails, STOP and report mismatch.

============================================================================
PHASE 1 — PRIMARY IMPLEMENTATION

STEP 1: Merge privateloader.py into runtime/kernelloader.py
  ☐ Open core/kernels/privateloader.py
  ☐ Extract any unique logic NOT in runtime/kernelloader.py
  ☐ Add extracted logic to runtime/kernelloader.py (preserve Neo4j sync)
  ☐ Add comment: "# Consolidated from core/kernels/privateloader.py"

STEP 2: Update runtime/__init__.py
  ☐ Verify exports include loadkernels, requirekernelactivation
  ☐ Add any missing exports from the consolidated loader

STEP 3: Delete the old loader
  ☐ Delete file: core/kernels/privateloader.py
  ☐ Confirm no other files import from privateloader.py
  ☐ Check: grep -r "privateloader" . (should be empty)

STEP 4: Wire kernel loading into FastAPI startup
  ☐ Open api/server.py
  ☐ Find asynccontextmanager def lifespan(app)
  ☐ After memory service initialization, add:
  
    if hasattr(app.state, 'substrateservice') and app.state.substrateservice:
        try:
            from runtime.kernelloader import loadkernels, requirekernelactivation
            from agents.lcto import LCTOAgent
            
            logger.info("Kernel loading: initializing L-CTO agent...")
            l9agent = LCTOAgent(agent_id="l9-standard-v1")
            loadkernels(l9agent)
            requirekernelactivation(l9agent)
            
            app.state.l9agent = l9agent
            logger.info(f"✓ Kernels loaded: {len(l9agent.kernels)} kernels active")
        except Exception as e:
            logger.error(f"✗ Kernel loading failed: {e}", exc_info=True)
            raise RuntimeError("L9 kernel initialization failed") from e
    
  ☐ Test: Save file, verify no syntax errors

STEP 5: Initialize RateLimiter in startup
  ☐ In the same lifespan startup section, add after kernel loading:
  
    if hasattr(app.state, 'substrateservice'):
        try:
            from runtime.ratelimiter import RateLimiter
            
            app.state.rate_limiter = RateLimiter(max_calls=100, window_seconds=60)
            logger.info("✓ Rate limiter initialized")
        except Exception as e:
            logger.error(f"Rate limiter init failed: {e}")

STEP 6: Wire rate limiter into Slack handler
  ☐ Open api/routes/slack.py (or api/slackrouter.py)
  ☐ Find the Slack events endpoint
  ☐ Add rate limit check at the start:
  
    @router.post("/events")
    async def handle_slack_event(request: dict):
        if not app.state.rate_limiter.is_allowed(request.get('user_id')):
            logger.warning(f"Rate limit exceeded for {request.get('user_id')}")
            return {"error": "rate_limit_exceeded"}, 429
        
        # ... rest of handler
  
  ☐ Test: Verify endpoint still parses

CHECKLIST FOR PHASE 1:
☐ privateloader.py deleted
☐ No grep matches for "privateloader"
☐ runtime/__init__.py updated
☐ api/server.py lifespan has kernel loading code
☐ api/server.py lifespan has rate limiter init
☐ Slack endpoint has rate limit check
☐ No syntax errors in any file
☐ Logger messages added for visibility

============================================================================
PHASE 2 — ENFORCEMENT IMPLEMENTATION

ADD GUARDS TO PREVENT REGRESSION:

1. Kernel presence guard in runtime/kernelloader.py
   ☐ Add at end of loadkernels():
   
    if not agent.kernels or agent.kernel_state != "ACTIVE":
        raise RuntimeError("Kernel loading incomplete: no kernels loaded or state not ACTIVE")
    
    logger.info(f"Kernel validation passed: {len(agent.kernels)} loaded, state={agent.kernel_state}")

2. Startup validation in api/server.py
   ☐ Before yielding in lifespan, add:
   
    if not hasattr(app.state, 'l9agent'):
        raise RuntimeError("L9 agent not initialized at startup")
    
    if app.state.l9agent.kernel_state != "ACTIVE":
        raise RuntimeError("L9 kernels not activated")
    
    logger.critical("✓✓✓ L9 FULLY INITIALIZED WITH ACTIVE KERNELS ✓✓✓")

3. Rate limiter validation
   ☐ Add to startup:
   
    if not hasattr(app.state, 'rate_limiter'):
        raise RuntimeError("Rate limiter not initialized")

CHECKLIST FOR PHASE 2:
☐ loadkernels() validates completion
☐ Startup raises if l9agent missing
☐ Startup raises if kernels not ACTIVE
☐ Startup raises if rate_limiter missing
☐ All guards have clear error messages

============================================================================
PHASE 3 — SYSTEM GUARDS

ADD RUNTIME FAIL-FAST CONDITIONS:

1. Add to api/server.py startup, BEFORE all other initialization:
   
   required_env_vars = ['MEMORY_DSN', 'OPENAI_API_KEY', 'SLACK_BOT_TOKEN']
   missing = [v for v in required_env_vars if not os.getenv(v)]
   if missing:
       raise RuntimeError(f"Missing required env vars: {missing}")

2. Add kernel path validation to runtime/kernelloader.py:
   
   KERNEL_ORDER = [...]  # existing list
   
   for path in KERNEL_ORDER:
       if not (base_path / path).exists():
           raise RuntimeError(f"Required kernel not found: {path}")
   
   logger.info(f"✓ All {len(KERNEL_ORDER)} kernel paths verified")

CHECKLIST FOR PHASE 3:
☐ Env var check added
☐ Kernel path check added
☐ All errors are explicit (no silent failures)
☐ Error messages are actionable

============================================================================
PHASE 4 — VALIDATION

RE-RUN THE FULL SEQUENCE:

☐ Delete all __pycache__ and .pyc files
☐ Run: python -m py_compile api/server.py (syntax check)
☐ Run: python -m py_compile runtime/kernelloader.py
☐ Check for import errors:
   grep -r "from core.kernels.privateloader" . (should be EMPTY)
   grep -r "import privateloader" . (should be EMPTY)
☐ Verify runtime/__init__.py exports:
   python -c "from runtime import loadkernels, requirekernelactivation; print('✓ exports ok')"

NEGATIVE TEST:
☐ Comment out the kernel loading code in lifespan
☐ Start server and verify it FAILS with RuntimeError
☐ Uncomment code, verify it SUCCEEDS

REGRESSION TEST:
☐ Verify old routes still work: GET /health should return 200
☐ Verify Slack endpoint still responds: POST /slack/events

CHECKLIST FOR PHASE 4:
☐ No syntax errors
☐ No import errors
☐ No grep matches for privateloader
☐ Negative test fails as expected
☐ Regression test passes

============================================================================
PHASE 5 — FINAL SANITY SWEEP

RE-INSPECT ALL CHANGES:

☐ api/server.py lifespan startup: kernel loading → rate limiter → yield
☐ Kernel order in runtime/kernelloader.py: 10 kernels in correct sequence
☐ api/routes/slack.py: rate limiter check BEFORE processing
☐ runtime/__init__.py: exports are correct
☐ All error messages are clear
☐ All logger.info calls provide visibility

COMPLETENESS CHECK:
☐ No TODO comments left in code
☐ All deleted files are confirmed gone
☐ All new code has inline comments
☐ All error paths raise with meaningful messages

CHECKLIST FOR PHASE 5:
☐ No loose ends remain
☐ All changes map to Phase -1 plan
☐ No improvisation detected
☐ System integrity preserved

============================================================================
DEFINITION OF DONE

ALL MUST BE TRUE:

☐ core/kernels/privateloader.py deleted
☐ runtime/kernelloader.py is the single loader
☐ api/server.py lifespan calls loadkernels() at startup
☐ app.state.l9agent exists after startup
☐ app.state.l9agent.kernel_state == "ACTIVE"
☐ app.state.rate_limiter exists after startup
☐ Slack endpoint has rate limit check
☐ All guards in place (env vars, kernel paths, agent validation)
☐ All tests pass (negative, regression)
☐ No syntax errors in any file
☐ No import errors
☐ Logger shows: "✓✓✓ L9 FULLY INITIALIZED WITH ACTIVE KERNELS ✓✓✓"

============================================================================
FINAL REPORT (REQUIRED)

Output must include:

1. FILE CHANGES:
   - Deleted: core/kernels/privateloader.py
   - Modified: runtime/kernelloader.py (consolidated loader)
   - Modified: runtime/__init__.py (exports)
   - Modified: api/server.py (lifespan startup)
   - Modified: api/routes/slack.py (rate limit check)

2. CHECKLIST STATUS:
   - Phase 0 (Baseline): ✓ PASSED
   - Phase 1 (Implementation): ✓ PASSED
   - Phase 2 (Enforcement): ✓ PASSED
   - Phase 3 (Guards): ✓ PASSED
   - Phase 4 (Validation): ✓ PASSED
   - Phase 5 (Sanity Sweep): ✓ PASSED

3. VALIDATION RESULTS:
   - Negative test: ✓ FAILS as expected (kernel loading disabled)
   - Regression test: ✓ PASSES (old routes work)
   - Startup log shows kernel activation: ✓ YES

4. DECLARATION OF COMPLETION:
   "L9 kernel loading is now deterministic, enforced, 
    and integrated into FastAPI startup. L-CTO agent loads all 
    kernels at boot. System is ready for VPS deployment."
