🧠 MISSION OBJECTIVE
Complete L9 initialization by activating Neo4j kernel influence tracking 
and hardening Slack against rate limits with Permission Graph.
Result: Kernels sync to Neo4j, Slack respects rate limits + permissions.

============================================================================
PHASE -1 — ANALYSIS & PLANNING

TASK DECOMPOSITION:

1. Activate Neo4j at startup
   - memory/graphclient.py connects to Neo4j
   - Sync kernels: create Kernel nodes + GOVERNS relationships
   - Sync tools: create Tool nodes + DEPENDS relationships
   
2. Wire Neo4j sync into kernel loader
   - After kernels are loaded, sync to graph
   - Create Kernel nodes for each kernel loaded
   - Create Rule nodes for prohibitions/thresholds
   
3. Activate Permission Graph
   - core/security/permissiongraph.py checks access
   - Before Slack event processing, check canaccess()
   - Deny if user/workspace not approved
   
4. Harden Slack handler
   - Check rate limits (RateLimiter from Prompt 1)
   - Check permissions (PermissionGraph)
   - Log both to Neo4j (Event nodes)
   
5. Test end-to-end
   - Restart Docker container
   - Verify Neo4j nodes created
   - Send Slack message, verify no rate limit error

DEPENDENCIES:
- Prompt 1 MUST be complete (rate limiter + kernel loading)
- Neo4j connection must be established FIRST
- Permission graph queries run AFTER Neo4j is ready

============================================================================
PHASE 0 — BASELINE CONFIRMATION

VERIFY THESE (DO NOT MODIFY):

☐ memory/graphclient.py exists and has Neo4j connection logic
☐ core/security/permissiongraph.py exists with canaccess() function
☐ api/routes/slack.py has rate_limiter check from Prompt 1
☐ Docker container has NEO4J_URI in .env
☐ Kernel loading is working (from Prompt 1)

FAILURE RULE: If any check fails, STOP and report mismatch.

============================================================================
PHASE 1 — PRIMARY IMPLEMENTATION

STEP 1: Wire Neo4j connection into FastAPI startup
  ☐ Open api/server.py lifespan startup
  ☐ After kernel loading block, add:
  
    # Initialize Neo4j connection
    if os.getenv('NEO4J_URI'):
        try:
            from memory.graphclient import get_graph_client
            
            logger.info("Connecting to Neo4j...")
            graph_client = await get_graph_client()
            app.state.graph_client = graph_client
            logger.info("✓ Neo4j connected")
        except Exception as e:
            logger.warning(f"Neo4j connection failed (non-critical): {e}")
            app.state.graph_client = None
    else:
        logger.warning("NEO4J_URI not set, Neo4j disabled")
        app.state.graph_client = None

STEP 2: Sync kernels to Neo4j graph
  ☐ Still in lifespan startup, after Neo4j connection:
  
    if app.state.graph_client and hasattr(app.state, 'l9agent'):
        try:
            logger.info("Syncing kernels to Neo4j...")
            agent = app.state.l9agent
            
            for kernel_path, kernel_data in agent.kernels.items():
                kernel_id = kernel_path.split('/')[-1].replace('.yaml', '')
                
                # Create Kernel node
                await app.state.graph_client.create_node(
                    label='Kernel',
                    properties={
                        'id': kernel_id,
                        'path': str(kernel_path),
                        'name': kernel_data.get('name', kernel_id),
                        'version': kernel_data.get('version', '1.0.0'),
                    }
                )
                
                # Create GOVERNS relationship
                await app.state.graph_client.create_relationship(
                    from_id=kernel_id, from_type='Kernel',
                    to_id='l9-standard-v1', to_type='Agent',
                    rel_type='GOVERNS'
                )
            
            logger.info(f"✓ Synced {len(agent.kernels)} kernels to Neo4j")
        except Exception as e:
            logger.error(f"Kernel sync to Neo4j failed: {e}")

STEP 3: Register L9 tools in Neo4j
  ☐ Still in lifespan startup, after kernel sync:
  
    if app.state.graph_client:
        try:
            from core.tools import registerl9tools
            
            logger.info("Registering L9 tools in Neo4j...")
            count = await registerl9tools()
            logger.info(f"✓ Registered {count} tools in graph")
        except Exception as e:
            logger.error(f"Tool registration failed: {e}")

STEP 4: Activate Permission Graph
  ☐ In lifespan startup, add:
  
    try:
        from core.security.permissiongraph import PermissionGraph
        
        app.state.permission_graph = PermissionGraph(graph_client=app.state.graph_client)
        logger.info("✓ Permission Graph initialized")
    except Exception as e:
        logger.warning(f"Permission Graph init failed: {e}")
        app.state.permission_graph = None

STEP 5: Harden Slack event handler with permissions check
  ☐ Open api/routes/slack.py
  ☐ Find the handle_slack_event function
  ☐ Add permission check AFTER rate limit check:
  
    @router.post("/events")
    async def handle_slack_event(request: dict):
        # Rate limit check (from Prompt 1)
        if hasattr(app.state, 'rate_limiter'):
            user_id = request.get('user_id', 'unknown')
            if not app.state.rate_limiter.is_allowed(user_id):
                logger.warning(f"Rate limit exceeded for {user_id}")
                return {"error": "rate_limit_exceeded"}, 429
        
        # Permission check (NEW)
        if hasattr(app.state, 'permission_graph'):
            try:
                user_id = request.get('user_id')
                workspace_id = request.get('team_id')
                
                if not await app.state.permission_graph.canaccess(user_id, 'slack/events'):
                    logger.warning(f"Permission denied for {user_id}")
                    return {"error": "permission_denied"}, 403
            except Exception as e:
                logger.error(f"Permission check error: {e}")
        
        # Log to Neo4j
        try:
            await app.state.graph_client.create_event(
                event_type='slack_event',
                user_id=request.get('user_id'),
                workspace_id=request.get('team_id'),
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.debug(f"Event logging failed: {e}")
        
        # Process event normally
        # ... rest of handler

STEP 6: Add Neo4j health check endpoint
  ☐ In api/server.py routes, add:
  
    @app.get("/health/neo4j")
    async def neo4j_health():
        if not hasattr(app.state, 'graph_client') or not app.state.graph_client:
            return {"status": "unavailable", "message": "Neo4j not configured"}
        
        try:
            result = await app.state.graph_client.run("RETURN 1")
            return {"status": "healthy", "neo4j": True}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

CHECKLIST FOR PHASE 1:
☐ Neo4j connection added to lifespan startup
☐ Kernel sync to Neo4j added
☐ Tool registration added
☐ Permission Graph initialized
☐ Slack handler has rate + permission checks
☐ Neo4j health endpoint added
☐ All try/except blocks are present
☐ All logger calls provide visibility

============================================================================
PHASE 2 — ENFORCEMENT IMPLEMENTATION

ADD GUARDS TO PREVENT REGRESSION:

1. Neo4j validation in startup
   ☐ Add after Neo4j connection attempt:
   
    if os.getenv('NEO4J_URI') and not app.state.graph_client:
        logger.critical("NEO4J_URI set but connection failed - ABORTING")
        raise RuntimeError("Neo4j connection required but unavailable")

2. Kernel sync validation
   ☐ Add after kernel sync:
   
    if app.state.graph_client and not app.state.l9agent.kernels:
        raise RuntimeError("Kernel sync skipped: no kernels to sync")

3. Permission Graph mandatory if Slack enabled
   ☐ Add after Permission Graph init:
   
    if os.getenv('SLACK_BOT_TOKEN') and not app.state.permission_graph:
        logger.critical("Slack enabled but Permission Graph failed - ABORTING")
        raise RuntimeError("Permission Graph required for Slack")

4. Slack handler validation
   ☐ Add guard inside handle_slack_event:
   
    if not hasattr(request, 'get') or not isinstance(request, dict):
        raise ValueError("Invalid Slack request format")

CHECKLIST FOR PHASE 2:
☐ Neo4j validation: raises if NEO4J_URI set but fails
☐ Kernel sync validation: raises if kernels empty
☐ Slack validation: raises if Slack enabled but Permission Graph fails
☐ Request validation: raises on malformed Slack events
☐ All guards have clear error messages

============================================================================
PHASE 3 — SYSTEM GUARDS

ADD RUNTIME FAIL-FAST CONDITIONS:

1. Add Neo4j URI validation:
   
   if os.getenv('NEO4J_URI'):
       uri = os.getenv('NEO4J_URI')
       if not uri.startswith(('bolt://', 'neo4j://', 'neo4j+s://')):
           raise ValueError(f"Invalid NEO4J_URI format: {uri}")

2. Add Slack event schema validation:
   
   VALID_SLACK_EVENT_TYPES = ['url_verification', 'event_callback', 'challenge']
   
   if request.get('type') not in VALID_SLACK_EVENT_TYPES:
       raise ValueError(f"Invalid Slack event type: {request.get('type')}")

3. Add rate limiter window validation:
   
   RATE_LIMIT_MAX = 100
   RATE_LIMIT_WINDOW = 60
   
   if app.state.rate_limiter.max_calls > RATE_LIMIT_MAX:
       raise ValueError("Rate limit max_calls exceeds safe limit")

CHECKLIST FOR PHASE 3:
☐ Neo4j URI format validated
☐ Slack event type validated
☐ Rate limiter limits validated
☐ All validation errors are explicit
☐ No silent failures

============================================================================
PHASE 4 — VALIDATION

RE-RUN THE FULL SEQUENCE:

☐ Verify Neo4j connection string in .env
☐ Verify NEO4J_URI format is correct
☐ Verify Slack creds in .env
☐ Run syntax check: python -m py_compile api/server.py
☐ Check imports:
   python -c "from memory.graphclient import get_graph_client; print('✓')"
   python -c "from core.security.permissiongraph import PermissionGraph; print('✓')"

NEGATIVE TEST:
☐ Set NEO4J_URI to invalid value
☐ Start server, verify it FAILS with clear error
☐ Revert NEO4J_URI to correct value
☐ Start server, verify startup SUCCEEDS

REGRESSION TEST:
☐ Health check still works: GET /health → 200
☐ Neo4j health endpoint works: GET /health/neo4j → 200 or 503
☐ Slack endpoint responds: POST /slack/events → 200

CHECKLIST FOR PHASE 4:
☐ Syntax check passes
☐ Import check passes
☐ Negative test fails as expected
☐ Regression tests pass
☐ Server starts without errors

============================================================================
PHASE 5 — FINAL SANITY SWEEP

RE-INSPECT ALL CHANGES:

☐ api/server.py lifespan:
   1. Memory service init
   2. Kernel loading + activation
   3. Neo4j connection
   4. Kernel sync to Neo4j
   5. Tool registration
   6. Permission Graph init
   ☐ Order is correct
   ☐ All error handling present

☐ api/routes/slack.py:
   1. Rate limit check
   2. Permission check
   3. Neo4j event logging
   4. Event processing
   ☐ All three checks before processing
   ☐ Logging is non-blocking

☐ All endpoints:
   ☐ /health works
   ☐ /health/neo4j works
   ☐ /slack/events works
   ☐ No new bugs introduced

COMPLETENESS CHECK:
☐ No TODO comments left
☐ No hardcoded values (all from env vars)
☐ All logger calls are present
☐ All error messages are actionable
☐ Graph client cleanup in shutdown (if added)

CHECKLIST FOR PHASE 5:
☐ Startup order is correct
☐ Slack handler has all three checks
☐ All endpoints work
☐ No loose ends
☐ System integrity preserved

============================================================================
DEFINITION OF DONE

ALL MUST BE TRUE:

☐ Neo4j connects at startup (or logs warning if disabled)
☐ Kernels sync to Neo4j (Kernel nodes + GOVERNS relationships)
☐ Tools register in Neo4j (Tool nodes + relationships)
☐ Permission Graph initializes
☐ Slack events checked for rate limits
☐ Slack events checked for permissions
☐ Slack events logged to Neo4j (Event nodes)
☐ All guards in place (URI format, event schema, rate limits)
☐ All tests pass (negative, regression)
☐ GET /health/neo4j returns healthy or unavailable (not error)
☐ No syntax errors
☐ No import errors
☐ Startup log shows all Neo4j operations completed

============================================================================
FINAL REPORT (REQUIRED)

Output must include:

1. FILE CHANGES:
   - Modified: api/server.py (Neo4j + Permission Graph init)
   - Modified: api/routes/slack.py (rate + permission checks + logging)
   - No files deleted
   - No files created (only edits to existing)

2. CHECKLIST STATUS:
   - Phase 0 (Baseline): ✓ PASSED
   - Phase 1 (Implementation): ✓ PASSED
   - Phase 2 (Enforcement): ✓ PASSED
   - Phase 3 (Guards): ✓ PASSED
   - Phase 4 (Validation): ✓ PASSED
   - Phase 5 (Sanity Sweep): ✓ PASSED

3. VALIDATION RESULTS:
   - Negative test (invalid Neo4j URI): ✓ FAILS as expected
   - Regression test (old endpoints): ✓ PASSES
   - Neo4j health endpoint: ✓ Returns status
   - Slack event logging: ✓ Creates Event nodes in graph

4. DECLARATION OF COMPLETION:
   "L9 Neo4j integration is complete. Kernels sync at boot, 
    Slack is hardened with rate limits + permissions, 
    and all events log to the graph. L9 is production-ready."
