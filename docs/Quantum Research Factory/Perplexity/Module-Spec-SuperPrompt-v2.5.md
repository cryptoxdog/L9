# L9 SUPERPROMPT: MODULE SPECIFICATION & WIRING (CANONICAL)

**Version**: 2.5.0 (Hardened)  
**Date**: 2025-12-17  
**Status**: PRODUCTION READY — Enterprise Deployment Grade  
**Audience**: Perplexity code generator (P-Prompt), CI gates, automated test generation  

---

## DOCTRINE: The Complete Closed Loop

For enterprise production workflow, the complete, closed loop is:

```
The SuperPrompt
    ↓ Controls flow, sequencing, responsibility
Tier Blocks
    ↓ Constrain & deepen scale expectations; no shallow Tier 2 specs
Module Spec v2.5
    ↓ Enforces removes discretion; locks runtime truth
Runtime Manifests
    ↓ Materialize specs into bootable topology (docker-compose, services, deps, startup order)
Tests
    ↓ Prove invariants (golden paths, negative cases, smoke reality check)
CI Gates
    ↓ Prevent drift (nothing merges unless all above remain true)
```

**Non-Negotiable**: Every statement in this SuperPrompt is **deterministic, verifiable, and measurable at deployment time**. No philosophy. No inference. No "implied behavior."

---

## GLOBAL CONSTRAINTS (BINDING)

These rules are **NON-NEGOTIABLE** and apply to every module spec:

1. **NO SUMMARIES** — Every fact must appear explicitly. No "see elsewhere," no references to implicit behavior.
2. **NO AMBIGUITY** — If something matters at runtime, it is **explicit in the spec**.
3. **NO PLACEHOLDERS** — Every field filled with real values. Zero `<placeholder>` tokens.
4. **NO EXTERNAL SUPPLEMENTS** — All guidance embedded within this document.
5. **NO SINGLETONS** — All dependencies injected. No module-level state.
6. **SSOT BINDING** — If these files contradict this SuperPrompt, these files win:
   - `DOCTRINE-Module-Spec.md` — Enterprise doctrine
   - `L9_RUNTIME_SSOT.md` — Deployment truth
   - `L9_DEPENDENCIES_SSOT.md` — Dependency authority
   - `L9_IDEMPOTENCY_SSOT.md` — Idempotency patterns
   - `MANUS_CONTEXT_PACK.md` — Code reference library

---

## CRITICAL READING STACK (MANDATORY, IN ORDER)

**Read these in order. Do NOT skip sections.**

### Priority 1: Enterprise Doctrine & Production Reality
- **DOCTRINE-Module-Spec.md** — Why we do this (5 min read)
- **L9_RUNTIME_SSOT.md** — Actual runtime: Docker, ports, services, initialization order (10 min)
- **L9_DEPENDENCIES_SSOT.md** — Exact dependencies, versions, binaries (5 min)
- **L9_IDEMPOTENCY_SSOT.md** — How duplicates are handled at runtime (5 min)

### Priority 2: Code Reality & Patterns
- **MANUS_CONTEXT_PACK.md** — Core schemas, protocols, existing patterns (10 min)
- **repo_supplement.md** — Exact imports, function signatures, error handling (read once, reference)
- **code_index.md** — All existing functions and classes (reference)

### Priority 3: Module Specification Schema
- **Module-Spec-v2.5.yaml** — Universal spec template (reference)
- **TIER_2_MODULE_GUIDANCE.yaml** — Tier 2 specific rules, file manifests, quality gates (10 min)

---

## TIER SYSTEM OVERVIEW

| Tier | Name | Complexity | File Count | External Surface | State | Testing | Example Modules |
|------|------|-----------|-----------|-----------------|-------|---------|-----------------|
| **1** | Simple Adapter | Low | 2–3 | Single webhook | Stateless | Basic validation | healthcheck, web.adapter |
| **2** | Integration Module | Medium | 4–7 | Webhook + API calls | Threaded (UUIDv5) | Idempotency + integration | slack.adapter, email.adapter, twilio.adapter |
| **3** | Complex Orchestration | High | 8+ | Multi-endpoint, stateful | State machine (4+ states) | Full DAG + governance + tracing | agent.executor, tool.registry, governance.engine |

**TIER DETERMINES OPERATIONAL DEPTH** — Tier 3 requires explicit runtime wiring; Tier 1 does not.

---

## TIER-SPECIFIC OPERATIONAL EXPANSION BLOCKS

These blocks are **MANDATORY** for spec completeness. Missing any section = **SPEC REJECTION**.

### TIER 1: SIMPLE ADAPTERS

#### Required Operational Depth

```yaml
runtime_wiring:
  placement: fastapi_route_handler
  startup_dependency: none
  blocks_boot: false
  external_surface:
    inbound: single_webhook_route
    outbound: none_or_internal_only
  packet_types: []  # stateless, no packets

dependency_contract:
  requires: []
  provides: []
  order: unconstrained

packet_contract:
  ingress: []
  egress: []
```

#### Must Be Explicit (No Inference Allowed)

- Route path and HTTP method (exact, no regex inference)
- Authentication method (none, hmac, bearer, etc.) — exact
- Response status codes (200, 400, 401, 5xx) — exact
- No database writes; no state persistence
- No threading; no UUIDv5 generation
- Failure handling: stateless, fail-silent

#### Must Not Be Omitted (Hard Failures)

- ✓ Endpoint documentation (path, method, headers)
- ✓ Authentication scheme (if any)
- ✓ Response format (JSON shape)
- ✓ Error codes and meanings
- ✗ Acceptance tests (if stateless, basic validation sufficient)

#### Common Failure Modes (Observed in Practice)

1. **Ambiguous auth** — Spec says "verify signature" but doesn't specify HMAC algorithm or header name → **REJECT**
2. **Missing error codes** — Spec doesn't define what 401 vs 403 means → **REJECT**
3. **Implicit statefulness** — Tier 1 pretending to be stateless when it caches → **RECLASSIFY to Tier 2**
4. **Vague endpoints** — "POST /webhook" without context → Clarify which platform

#### Tier 1 Completion Checklist

- [ ] Route path explicit (no inference)
- [ ] HTTP method explicit (POST, GET, etc.)
- [ ] Auth scheme explicit (none, hmac-sha256, bearer, apikey)
- [ ] All response status codes documented
- [ ] No database writes declared
- [ ] No state persistence declared
- [ ] No threading or UUIDv5 usage declared
- [ ] Error codes map to spec fields
- [ ] Ready for FastAPI route registration

---

### TIER 2: INTEGRATION MODULES (WEBHOOKS + THREADING + MEMORY)

#### Required Operational Depth

```yaml
runtime_wiring:
  placement: fastapi_route_handler_with_service_injection
  startup_dependency: [memory_substrate_service]
  blocks_boot: false
  external_surface:
    inbound: webhook_with_signature_verification
    outbound: [aios_chat_endpoint, external_api_optional]
  packet_types: [module.in, module.out, module.error]

dependency_contract:
  requires:
    - memory_substrate_service (PacketEnvelopeIn ingestion)
    - optional: external_api_client (httpx)
  provides:
    - packet_storage (conversation threads)
    - conversation_context (searchable packets)
  order: memory_substrate_must_be_ready

packet_contract:
  ingress:
    - packettype: module.in
      shape: {eventid, source, channel, payload}
      threadid: UUIDv5(deterministic)
  egress:
    - packettype: module.out
      shape: {response_text, metadata}
    - packettype: module.error
      shape: {error_type, error_message}
```

#### Must Be Explicit (No Inference Allowed)

- Thread UUID formula (components: sourceid, channelid, threadts) — exact
- Idempotency deduplication key — primary + fallback
- Packet metadata (which fields go where)
- Signature verification algorithm + header names
- Timestamp freshness window (seconds)
- AIOS endpoint and timeout
- External API retry logic (exponential backoff parameters)
- All HTTP headers required and sent
- Error packet structure (fields, when emitted)

#### Must Not Be Omitted (Hard Failures)

- ✓ Thread UUID formula with platform-specific mappings
- ✓ Idempotency deduplication strategy + durability level
- ✓ Signature verification (algorithm, header, secret management)
- ✓ Timestamp validation (window, rejection behavior)
- ✓ Packet storage metadata (which fields tagged, searchability)
- ✓ AIOS integration (endpoint, input shape, output handling)
- ✓ External API client (if outbound calls made)
- ✓ Error handling (5 categories: invalid_signature, stale_timestamp, aios_failure, sideeffect_failure, storage_failure)
- ✓ Acceptance tests (6 minimum: signature, valid request, threading, deduplication, AIOS forwarding, storage correctness)
- ✓ Logging (9 required events with structured fields)
- ✗ New database tables (FORBIDDEN)
- ✗ Module-level singletons (FORBIDDEN)

#### Common Failure Modes (Observed in Practice)

1. **Thread UUID not deterministic** — Using uuid4() instead of UUIDv5 → Same input ≠ same UUID → **REJECT**
2. **Idempotency undefined** — "Handle duplicates" without saying how → **REJECT**
3. **Packet metadata ambiguity** — "Store inbound event" without specifying fields → **REJECT**
4. **Error response inconsistency** — Return 401 on signature failure, then return 200 on storage failure → Breaks external redelivery logic → **REJECT**
5. **AIOS call timeout not specified** → Default 30s assumed but not declared → **RECLASSIFY as incomplete**
6. **External client not declared** — Module sends replies but spec has no `api_module_client.py` → **REJECT**

#### Tier 2 Completion Checklist

- [ ] Thread UUID formula with exact components and platform mappings
- [ ] Idempotency deduplication key (primary + fallback) and durability (none, in-memory, persistent)
- [ ] Signature verification algorithm, header name, secret source
- [ ] Timestamp freshness window (seconds) and rejection behavior
- [ ] Packet types explicit (module.in, module.out, module.error with field shapes)
- [ ] AIOS endpoint, timeout, input/output shapes, error handling
- [ ] External API client declared (if outbound calls) with retry logic
- [ ] Error policy complete (5 categories, status codes, actions)
- [ ] Logging config (9 events, structlog, field names)
- [ ] File manifest (allowednewfiles: adapter, router, client if needed, tests, docs)
- [ ] Acceptance tests (6 minimum, each maps to criterion)
- [ ] No new database tables declared
- [ ] No module-level singletons declared
- [ ] Ready for Perplexity code generation

---

### TIER 3: COMPLEX ORCHESTRATION (STATE MACHINES, GOVERNANCE, AGENTS)

#### Required Operational Depth

```yaml
runtime_wiring:
  placement: service_layer_with_protocol_injection
  startup_dependency: [memory_substrate_service, governance_engine, tool_registry, aios_runtime]
  blocks_boot: true  # Tier 3 modules must be healthy before system is usable
  external_surface:
    inbound: [api_endpoints, event_subscriptions, task_dispatch]
    outbound: [memory_packets, governance_evaluations, tool_dispatch, aios_reasoning]
  packet_types: [module.state.start, module.state.transition, module.state.end, module.error, module.audit]
  state_machine:
    states: [INITIALIZING, REASONING, TOOLUSE, COMPLETED, FAILED, TERMINATED]
    transitions: [explicit state map]
    invariants: [list of conditions maintained]

dependency_contract:
  requires:
    - agent_registry (AgentConfig lookup)
    - memory_substrate_service (PacketEnvelopeIn, search, context assembly)
    - tool_registry (ToolRegistry protocol with dispatch)
    - governance_engine (EvaluationRequest, EvaluationResult)
    - aios_runtime (AIOSRuntimeProtocol for reasoning)
  provides:
    - agent_execution_service
    - reasoning_traces (audit, debugging)
    - tool_bindings (capability scoping)
  order: must_satisfy_dependency_graph (no cycles)

packet_contract:
  ingress:
    - packettype: module.task.submitted
      shape: {task_id, agent_id, payload, metadata}
      routing: deterministic_by_agent_id
  egress:
    - packettype: module.execution.result
      shape: {task_id, status, result, iterations, duration}
    - packettype: module.reasoning.trace
      shape: {iteration, step, decision, tokens_used}
    - packettype: module.tool.call
      shape: {tool_id, arguments, context}
    - packettype: module.error
      shape: {error_type, task_id, traceback}
```

#### Must Be Explicit (No Inference Allowed)

- **State machine**: every state, every valid transition, invariants maintained
- **Startup dependencies**: exact order, health checks, blocking vs non-blocking
- **Idempotency**: how restarts recover (in-memory vs substrate-backed)
- **Packet emission**: when each packet type is emitted, which fields are required
- **Governance integration**: which actions require policy approval, deny-by-default applied where
- **Tool dispatch**: toolid as sole identity, capability checking, rate limiting if applicable
- **Context assembly**: how packet history is retrieved for reasoning
- **Error recovery**: explicit steps when module fails, what state is left behind
- **Test coverage**: 8+ acceptance tests covering all state transitions, error paths, governance integration

#### Must Not Be Omitted (Hard Failures)

- ✓ Complete state machine (definition, transitions, invariants, error states)
- ✓ Startup dependency graph with exact order and blocking/non-blocking nature
- ✓ Idempotency recovery strategy (in-memory vs substrate, restart behavior)
- ✓ All packet types (ingress + egress) with exact field shapes
- ✓ Governance integration points (which actions require approval, context passed to policy engine)
- ✓ Tool registry integration (tool dispatch, capability enforcement, rate limiting)
- ✓ AIOS reasoning integration (context assembly, reasoning loop, token tracking)
- ✓ Error handling (all error types, recovery, packet emission)
- ✓ Tracing/audit (all decisions logged, reasoning traces captured)
- ✓ Acceptance tests (8+ minimum: state transitions, error cases, governance, tool binding, context assembly)
- ✓ Wiring snippet for server.py (how service is initialized, injected into routes/handlers)
- ✗ New database tables (FORBIDDEN)
- ✗ Module-level singletons (FORBIDDEN)
- ✗ Implicit dependencies (all must be declared and injected)

#### Common Failure Modes (Observed in Practice)

1. **Missing state machine definition** — "Handles agent execution" without state diagram → **REJECT**
2. **Dependency cycle** — Tool Registry depends on Governance which depends on Tool Registry → **REJECT**
3. **Startup blocking undefined** — "Requires governance engine" but doesn't say if system can boot without it → **RECLASSIFY or REJECT**
4. **Implicit singletons** — `global governance_engine` at module level → **REJECT**, must be injected
5. **Idempotency not recovery-safe** — In-memory cache lost on restart, tasks re-execute → Document as limitation and plan mitigation
6. **Missing state invariants** — State machine drawn but no invariants declared (e.g., "if TOOLUSE, tool_binding must exist") → **REJECT**
7. **Packet types incomplete** — "Emit reasoning traces" without defining packet schema → **REJECT**

#### Tier 3 Completion Checklist

- [ ] State machine fully defined (states, transitions, invariants, error handling)
- [ ] Startup dependencies ordered, blocking/non-blocking declared, health checks specified
- [ ] Idempotency strategy (mechanism, key generation, recovery on restart)
- [ ] All packet types defined (ingress, egress, exact field shapes, routing rules)
- [ ] Governance integration explicit (approval points, context passed, deny-by-default applied)
- [ ] Tool registry integration explicit (tool lookup, capability checking, rate limiting)
- [ ] AIOS reasoning integration explicit (context assembly, loop, output handling)
- [ ] Error handling explicit (all error types, recovery steps, packet emission)
- [ ] Tracing/audit explicit (decision logging, reasoning trace capture, correlationids)
- [ ] Protocol injection declared (no singletons, all dependencies injected)
- [ ] Wiring snippet provided (initialization in server.py, service state storage)
- [ ] File manifest complete (module files, tests covering all paths)
- [ ] Acceptance tests (8+ minimum, covering all state transitions, error cases, integration points)
- [ ] Ready for Perplexity code generation + automated CI deployment

---

## THE 6-PASS WORKFLOW (CORE PROCESS — DO NOT MODIFY)

For each module, execute these 6 passes **in order**:

### Pass 1: Classify Module Tier

**Input**: Module description from MODULEROADMAP  
**Output**: Tier classification (1, 2, or 3)  
**Decision Logic**:

```yaml
if (receives_external_webhooks OR makes_outbound_api_calls) AND
   (integrates_with_memory_substrate) AND
   (calls_aios_chat_endpoint) AND
   (implements_conversation_threading):
  tier = 2

elif (creates_agent_instances_dynamically) OR
     (implements_tool_registry_dispatch) OR
     (requires_governance_policy_evaluation) OR
     (has_state_machine_4_states_or_more):
  tier = 3

else:
  tier = 1
```

**Validation**: Once classified, apply the **Tier-Specific Operational Expansion Block** for that tier.

---

### Pass 2: Map Existing Code (If Present)

**Input**: `module.hasexistingcode: true/false` from MODULEROADMAP  
**Output**: Gap analysis, rewrite/align/wire decision

**If NO existing code**:
```
existingfiles = []
action = create_from_scratch
```

**If YES existing code**:
```
1. Locate existingfile in repo (from MODULEROADMAP)
2. Read current implementation
3. Characterize behavior, gaps relative to spec requirements
4. Decide action:
   - REWRITE: Replace entirely (Slack, Twilio, WhatsApp adapters typically)
   - ALIGN: Modify to conform (add PacketEnvelopeIn, threading, idempotency)
   - WIRE: Minimal changes, integrate into new module service layer
5. List changes in allowedmodifiedfiles
```

**Example**:
```yaml
module: slack.adapter
hasexistingcode: true
existingfile: api/webhook_slack.py
current_gaps:
  - Thread UUID uses uuid4 (not deterministic)
  - Idempotency not durable (no substrate lookup)
  - Packet metadata structure unclear
action: REWRITE
justification: Current code predates PacketEnvelopeIn and ThreadUUID patterns
```

---

### Pass 3: Extract Interfaces (Inbound + Outbound)

**Input**: Module purpose, dependencies from MODULEROADMAP  
**Output**: `interfaces.inbound` and `interfaces.outbound`

#### Inbound Interfaces (How requests enter module)

For each inbound interface, specify:
- **name**: Interface identifier
- **method**: HTTP verb (POST, GET, etc.)
- **route**: URL path (exact, no inference)
- **headers**: Required headers (exact names)
- **payloadtype**: JSON, form, etc.
- **auth**: hmac-sha256, bearer, apikey, none
- **rate_limit**: Optional (requests per minute)

#### Outbound Interfaces (How module calls other services)

For each outbound interface, specify:
- **name**: Call identifier
- **endpoint**: URL or service reference (exact)
- **method**: HTTP verb or protocol (POST, gRPC, etc.)
- **timeoutseconds**: Exact timeout
- **retry**: true/false + backoff if true
- **auth**: How caller is authenticated
- **error_handling**: What happens on failure

**Example for Tier 2 Slack Adapter**:
```yaml
interfaces:
  inbound:
    - name: slack_events
      method: POST
      route: /slack/events
      headers:
        - X-Slack-Request-Timestamp
        - X-Slack-Signature
      payloadtype: JSON
      auth: hmac-sha256
  
  outbound:
    - name: aios_chat
      endpoint: /chat
      method: POST
      timeoutseconds: 30
      retry: false
    - name: slack_reply
      endpoint: https://slack.com/api/chat.postMessage
      method: POST
      timeoutseconds: 10
      retry: true
      auth: bearer_token
```

---

### Pass 4: Define Orchestration Flow (Step-by-Step Execution)

**Input**: Module responsibility, interfaces from Passes 1–3  
**Output**: `orchestration` section with explicit steps

The orchestration section describes **exactly** what happens, in order, when the module processes an event.

```yaml
orchestration:
  validation:
    - Step 1: Verify signature HMAC-SHA256 against X-Slack-Signature header
    - Step 2: Check X-Slack-Request-Timestamp is within 5 minutes (reject if stale)
    - Step 3: Parse JSON payload and validate required fields (eventid, source, channel)
  
  threadid_generation:
    - Compute deterministic UUID: uuid5(MODULE_NAMESPACE, f"{team_id}:{channel}:{thread_ts or ts}")
    - If same inputs repeat, UUID is identical (proof of determinism in test)
  
  deduplication:
    - Check processed_events cache for this event_id
    - If found: return { ok: true, dedupe: true, packet_id: cached_id } (200 status, silent)
    - If not found: continue to next step
  
  contextreads:
    - Method: substrateservice.searchpackets(threadid, limit=50)
    - Filter: Returns recent packets in this thread (conversation history)
    - Purpose: Assemble context for AIOS chat call
  
  aioscalls:
    - Endpoint: POST /chat
    - Input: { message: payload.text, context: [list of recent packets], thread_id: threadid }
    - Output: { response_text: str, tokens_used: int }
    - Timeout: 30 seconds
    - Error: If fails, store error packet, return 200 to Slack (prevent redelivery loop)
  
  sideeffects:
    - Action 1: Store inbound packet
      Service: substrateservice.writepacket
      Packet: PacketEnvelopeIn(packettype="slack.in", threadid=threadid, payload={...})
    - Action 2: Store outbound reply packet
      Service: substrateservice.writepacket
      Packet: PacketEnvelopeIn(packettype="slack.out", threadid=threadid, payload={response_text: ...})
    - Action 3: Send reply to Slack
      Service: slackclient.postmessage
      Args: { channel: source_channel, thread_ts: thread_ts, text: response_text }
```

**Key Principle**: No step is implicit. Every operation is explicit.

---

### Pass 5: Configure Idempotency & Error Handling

**Input**: External system guarantees, packet storage model from Passes 1–4  
**Output**: `idempotency` and `errorpolicy` sections

#### Idempotency (From L9_IDEMPOTENCY_SSOT.md)

Specify the deduplication strategy:

```yaml
idempotency:
  enabled: true/false
  mechanism: event_id_check | composite_key | substrate_lookup | inmemory_cache
  
  dedupekey:
    primary: Slack event_id (guaranteed unique per Slack workspace)
    fallback: sha256(team_id + channel + ts + user_id)
  
  onduplicate: return { ok: true, dedupe: true, packet_id: original_id }, HTTP 200
  
  threadid:
    type: UUIDv5
    namespace: module.l9.internal
    components: [sourceid, channelid, threadidentifier]
  
  durability: none  # Slack event_id uniqueness is guaranteed by Slack; we rely on external guarantee
  notes: "Idempotency is NOT persistent across process restart for Slack (in-memory cache only). Substrate-backed lookup planned for v1.2."
```

#### Error Policy (5 Required Categories)

```yaml
errorpolicy:
  invalidsignature:
    status: 401
    action: Reject immediately, do not process
    log: signature_verification_failed
    log_fields: [toolid, expected_sig, received_sig]
  
  staletimestamp:
    status: 401
    action: Reject immediately, do not process
    log: timestamp_stale
    log_fields: [toolid, timestamp, current_time, tolerance_seconds]
  
  aiosfailure:
    status: 200  # ALWAYS 200 to prevent external service redelivery loops
    action: Log error, store error packet, return success to external service
    log: aios_call_failed
    log_fields: [toolid, error, traceback, context]
    store_error_packet: true
  
  sideeffectfailure:
    status: 200  # ALWAYS 200
    action: Log error, do not reply to user, store error packet
    log: reply_failed
    log_fields: [toolid, error, traceback, external_service]
    store_error_packet: true
  
  storagefailure:
    status: 200  # ALWAYS 200
    action: Log error, continue processing (best-effort)
    log: packet_storage_failed
    log_fields: [toolid, error, packet_type]
    store_error_packet: false  # Storage failed, so skip this
```

---

### Pass 6: Finalize & Quality Gate

**Input**: Spec from Passes 1–5  
**Output**: Module-Spec-v2.5.yaml ready for Perplexity code generation

**Quality Checklist** (ALL must pass):

#### Pre-Generation Checks

- [ ] **moduleid_format**: lowercase, snake_case, no spaces (e.g., `slack_adapter`, NOT `SlackAdapter`)
- [ ] **goals_specificity**: Goals are specific and measurable, not generic
- [ ] **nongoals_locked**: These MUST be present:
  - `No new database tables`
  - `No new migrations`
  - `No parallel memory/logging/config systems`
- [ ] **threaduuid_deterministic**: (Tier 2+) `threadid.type` is `UUIDv5`, never `uuid4`
- [ ] **httpclient_standard**: (Tier 2+) `standards.httpclient.library` is `httpx`
- [ ] **logging_standard**: All modules use `structlog`, never stdlib `logging`
- [ ] **no_placeholders**: Zero `<placeholder>`, `{FIXME}`, `[TODO]` tokens

#### Post-Generation Checks

- [ ] **acceptance_coverage**: Every orchestration step has ≥1 acceptance criterion
- [ ] **errorpolicy_completeness**: All 5 error categories defined (invalidsignature, staletimestamp, aiosfailure, sideeffectfailure, storagefailure)
- [ ] **envvar_naming**: Environment variables follow `MODULE_PREFIX_NAME` format
- [ ] **file_manifest_consistency**: Every file in `allowednewfiles` used in orchestration or tests
- [ ] **interface_completeness**: Every interface has exact method, path, auth, timeout

#### Tier-Specific Checks

**Tier 1**:
- [ ] No packet types declared (stateless)
- [ ] No threading or UUIDv5 (stateless)
- [ ] No database reads or writes (stateless)

**Tier 2**:
- [ ] Thread UUID formula provided with platform mappings
- [ ] Idempotency mechanism declared (durability level clear)
- [ ] Signature verification algorithm explicit (header, algorithm, secret source)
- [ ] Timestamp freshness window explicit (seconds)
- [ ] AIOS endpoint, timeout, input/output explicit
- [ ] External API client declared (if outbound calls made)
- [ ] Error policy complete (5 categories, always 200 to webhook)
- [ ] Logging config (9 events, structlog, field names)
- [ ] File manifest complete (adapter, router, tests, docs)
- [ ] Acceptance tests (6 minimum)

**Tier 3**:
- [ ] State machine fully defined (states, transitions, invariants)
- [ ] Startup dependencies ordered (blocking/non-blocking)
- [ ] Packet types defined (ingress, egress, shapes)
- [ ] Governance integration points explicit
- [ ] Tool registry integration explicit
- [ ] Error recovery explicit (what state is left behind)
- [ ] Acceptance tests (8+ minimum, all state paths + error cases)
- [ ] Wiring snippet for server.py provided

**FINAL GATE**: If any check fails, return spec to spec author with explicit failure reason. Do NOT generate code.

---

## RUNTIME WIRING & DEPLOYMENT REALITY

These sections MUST appear in every spec and connect directly to production:

### Section: `runtime_wiring`

```yaml
runtime_wiring:
  # Placement: Where does this module run?
  placement: fastapi_route_handler | service_layer | background_task
  
  # Startup dependencies: What must be initialized before this module?
  startup_dependency:
    - service_name: memory_substrate_service
      blocking: true  # Module cannot start without this
      healthcheck: GET /memory/health
      timeout_seconds: 30
  
  # Does module startup block system boot?
  blocks_boot: false  # Tier 2 false; Tier 3 varies
  
  # Docker Compose: Which service does this run in?
  docker_service: l9-api
  
  # External surface: What is exposed?
  external_surface:
    inbound: [webhook_route_/slack/events]
    outbound: [aios_api_endpoint, external_api_optional]
  
  # Packet types: What packets does this emit/consume?
  packet_types: [slack.in, slack.out, slack.error]
  
  # Port bindings (if applicable)
  ports: []
  
  # Environment variables required at runtime
  env_required:
    - SLACK_SIGNING_SECRET
    - AIOS_BASE_URL
  
  # Failure modes that prevent boot
  fail_boot_if:
    - SLACK_SIGNING_SECRET not set
    - memory_substrate_service health check fails
```

### Section: `dependency_contract`

```yaml
dependency_contract:
  # Services this module requires
  requires:
    - service: memory_substrate_service
      interface: MemorySubstrateService (PacketEnvelopeIn)
      contract: writepacket(PacketEnvelopeIn) -> PacketWriteResult
      used_for: [packet_storage, context_retrieval]
  
  # Services this module provides
  provides:
    - interface: slack_webhook_handler
      contract: POST /slack/events -> JSON response
  
  # Dependency order (if any)
  order: [memory_substrate_service must be ready before any webhook processed]
  
  # Circular dependency check
  circular_deps: false
```

### Section: `packet_contract`

```yaml
packet_contract:
  # Packets consumed
  ingress:
    - packettype: slack.in
      schema:
        eventid: str  # Slack event_id
        source: "slack"
        channel: str  # Slack channel
        payload: dict  # Original Slack event JSON
      metadata_attached:
        threadid: UUID  # UUIDv5(deterministic)
        source: "slack"
        domain: "plasticbrokerage"
  
  # Packets emitted
  egress:
    - packettype: slack.out
      schema:
        response_text: str
        channel: str
        thread_ts: str
      metadata_attached:
        threadid: UUID
    - packettype: slack.error
      schema:
        error_type: str
        error_message: str
        task_id: str
```

---

## MODULE SPEC v2.5 TEMPLATE (REQUIRED STRUCTURE)

Every module spec MUST use this exact structure (no omissions, no additions):

```yaml
module:
  id: module_id                    # CANONICAL IDENTITY (toolid)
  name: Module Name                # Display only
  purpose: One-line description
  system: L9
  language: python
  runtime: python3.11
  owner: Boss

goals:
  - Goal 1 (specific, measurable)
  - Goal 2 (specific, measurable)

nongoals:
  - Module-specific non-goal
  - No new database tables        # LOCKED
  - No new migrations              # LOCKED
  - No parallel memory/logging/config systems  # LOCKED

repo:
  rootpath: /Users/ib-mac/Projects/L9
  allowednewfiles:
    - api/module_adapter.py
    - api/routes/module.py
    - tests/test_module_adapter.py
  allowedmodifiedfiles:
    - api/server.py

# ========== RUNTIME WIRING ==========
runtime_wiring:
  service: "{{api | worker | scheduler | memory}}"
  startup_phase: "{{early | normal | late}}"
  depends_on:
    - "{{postgres | redis | memory.service | ...}}"
  blocks_startup_on_failure: "{{true | false}}"

# ========== DEPENDENCY CONTRACT ==========
dependency_contract:
  inbound:
    - from_module: "{{caller_module}}"
      interface: "{{http | tool}}"
      endpoint: "{{inbound_route}}"
  outbound:
    - to_module: "{{target_module}}"
      interface: "{{http | tool}}"
      endpoint: "{{target_endpoint}}"

# ========== PACKET CONTRACT ==========
packet_contract:
  emits:
    - "{{module}}.in"
    - "{{module}}.out"
    - "{{module}}.error"
  requires_metadata:
    - "task_id"
    - "thread_uuid"
    - "source"
    - "tool_id"

interfaces:
  inbound:
    - name: webhook_name
      method: POST
      route: /module/events
      headers: [X-Signature, X-Timestamp]
      payloadtype: JSON
      auth: hmac-sha256
  
  outbound:
    - name: aios_chat
      endpoint: /chat
      method: POST
      timeoutseconds: 30
      retry: false

environment:
  required:
    - name: MODULE_SIGNING_SECRET
      description: Secret for HMAC verification
      example: "your_secret"
  optional:
    - name: SEMANTIC_SEARCH_ENABLED
      description: Enable semantic search
      default: "false"

orchestration:
  validation:
    - Verify signature HMAC-SHA256
    - Check timestamp freshness (5 minutes)
  
  contextreads:
    - method: substrateservice.searchpackets
      filter: threaduuid match
      purpose: Get conversation history
  
  aioscalls:
    - endpoint: /chat
      input: "message + context"
      output: "responsetext"
  
  sideeffects:
    - action: Reply to external service
      service: moduleclient.postmessage
    - action: Store inbound packet
      service: substrateservice.writepacket
      packettype: module.in

idempotency:
  pattern: "{{event_id | composite_key | substrate_lookup}}"
  source: "{{platform_event_id | webhook_header | computed_hash}}"
  durability: "{{in_memory | substrate}}"

errorpolicy:
  invalidsignature:
    status: 401
    action: Reject immediately
    log: signature_invalid
  staletimestamp:
    status: 401
    action: Reject immediately
    log: timestamp_stale
  aiosfailure:
    status: 200
    action: Log error, return ok
    log: aios_call_failed
  sideeffectfailure:
    status: 200
    action: Log error, return ok
    log: reply_failed
  storagefailure:
    status: 200
    action: Log error, continue
    log: packet_storage_failed

acceptance:
  required:
    - criterion: Signature verification blocks invalid requests
      test: test_invalid_signature_returns_401
    - criterion: Valid requests are processed
      test: test_valid_request_processes
    - criterion: Duplicate events are idempotent
      test: test_duplicate_events_skipped

forbidden:
  - Creates new database tables
  - Uses module-level singletons
  - Reads env vars at import time
  - Uses aiohttp instead of httpx
  - Uses stdlib logging instead of structlog
  - Uses toolname instead of toolid

observability:
  requiredlogs:
    - event: request_received
      level: info
      fields: [eventid, source, channel]
    - event: aios_call_complete
      level: info
      fields: [elapsedms, status]
  metrics:
    - module_requests_total
    - module_errors_total
    - module_latency_seconds

standards:
  identity:
    canonicalidentifier: toolid
    description: Always use module.id, never toolname
  logging:
    library: structlog
    forbidden: [logging, print]
  httpclient:
    library: httpx
    forbidden: [aiohttp, requests]

notesforperplexity:
  - Use REPOCONTEXTPACK imports exactly
  - Use PacketEnvelopeIn for all packets
  - Use UUIDv5 for threadid, never uuid4
  - All handlers accept injected services (no singletons)
  - Route handlers get services from request.app.state
  - Include all tests from acceptance.required
  - Include WIRINGSNIPPET for server.py initialization
```

---

## THE 35 MODULE ROADMAP (TIER-CLASSIFIED, DEPENDENCY-ORDERED)

### Tier 0: OS Kernel (3 modules) — **BLOCKING BOOT**

1. **tool.registry** (Tier 3) — Central tool dispatch, schema validation, governance-gated
2. **governance.engine** (Tier 3) — Policy evaluation, deny-by-default enforcement
3. **agent.executor** (Tier 3) — Agent instantiation, tool binding, execution loop

### Tier 1: Integrations (12 modules) — **DO NOT BLOCK BOOT**

4. **slack.adapter** (Tier 2) — HMAC-verified webhooks (REWRITE)
5. **email.adapter** (Tier 2) — IMAP/SMTP threading (ALIGN)
6. **twilio.adapter** (Tier 2) — SMS/Voice webhooks (REWRITE)
7. **waba.adapter** (Tier 2) — WhatsApp Business (REWRITE)
8. **calendar.adapter** (Tier 1–2) — Google/Apple calendar
9. **web.adapter** (Tier 1–2) — Web scraping
10. **webhook.receiver** (Tier 1) — Generic webhook receiver
11. **mac.automation** (Tier 2) — AppleScript/GUI control (WIRE)
12. **mac.finder** (Tier 1–2) — File operations
13. **mac.notifications** (Tier 1–2) — System notifications

### Tier 2: Agent Infrastructure (4 modules) — **TIER 2–3 COMPLEXITY**

14. **agent.lifecycle** — Spawn, monitor, terminate agents
15. **agent.session** — Session state, context window
16. **agent.capability** — Runtime capability grants (EXTEND existing)
17. **agent.health** — Heartbeat, health checks

### Tier 3: Memory Services (4 modules)

18. **memory.search** — Unified search (packetstore + semantic + facts) (WRAP)
19. **memory.summarizer** — Thread summarization
20. **memory.gc** — Garbage collection, TTL enforcement (WRAP)
21. **memory.export** — Export to external systems

### Tier 4: Scheduling (4 modules)

22. **task.scheduler** — Cron-like scheduling
23. **task.queue** — Persistent priority queue (ADD Redis)
24. **event.bus** — Pubsub, topic-based routing
25. **event.replay** — Event replay, debugging

### Tier 5: Domain Plugin (4 modules)

26. **domain.registry** — Domain registration, discovery
27. **domain.manifest** — Domain manifest schema
28. **domain.isolation** — Domain sandboxing, isolation
29. **domain.events** — Domain event bridge

### Tier 6: Security (4 modules)

30. **secrets.vault** — Secure secret storage
31. **secrets.rotation** — Automatic key rotation
32. **auth.gateway** — Centralized auth (EXTEND)
33. **audit.log** — Immutable audit trail

### Tier 7: Observability (4 modules)

34. **metrics.collector** — Prometheus-style metrics
35. **tracing.distributed** — OpenTelemetry integration
36. **alerts.engine** — Alert rules, thresholds
37. **dashboard.api** — Metrics/status API

---

## DECISION MATRIX (AUTOMATED RESOLUTION)

When spec author encounters a choice point, resolve automatically (no user input needed):

| **Scenario** | **Condition** | **Decision** |
|---|---|---|
| External API client needed? | Module sends replies to external platform | Include `api_module_client.py` |
| | Module only receives webhooks, no replies | Omit client file |
| Custom ingest logic? | Non-standard thread UUID or packet transformation | Include `memory_module_ingest.py` |
| | Standard write via `substrateservice.writepacket` | Omit ingest file |
| Semantic search enabled? | Benefits from similar past conversations | `enabled: true` |
| | Simple request-response, no history | `enabled: false` or omit |
| Auth method | Slack integration | `hmac-sha256` + `X-Slack-Signature` |
| | WhatsApp Business API | Bearer token or webhook verification |
| | Twilio | `X-Twilio-Signature` HMAC-SHA256 |
| | Generic webhook | `hmac-sha256` or apikey |
| AIOS timeout | Complex reasoning task | 60 seconds |
| | Simple response generation | 15 seconds |
| | Default | 30 seconds |
| Retries enabled? | AIOS calls | `false` (let orchestrator handle) |
| | External API calls | `true` (exponential backoff) |
| | Substrate writes | `false` (fail-fast) |
| Startup blocking? | Core orchestration (Tier 3) | `blocks_boot: true` |
| | Integration (Tier 1–2) | `blocks_boot: false` |

---

## THREAD UUID FORMULA (UNIVERSAL, TIER 2+)

**MANDATORY**: Use UUIDv5 with deterministic components. Never use uuid4 for threads.

```python
from uuid import uuid5, NAMESPACE_DNS

MODULE_NAMESPACE = uuid5(NAMESPACE_DNS, "module.l9.internal")

def generate_thread_uuid(sourceid: str, channelid: str, threadts: str) -> UUID:
    """Generate deterministic thread UUID from stable identity components."""
    identity = f"{sourceid}:{channelid}:{threadts}"
    return uuid5(MODULE_NAMESPACE, identity)

# Test: Same inputs → Same UUID (proof of determinism)
assert generate_thread_uuid("T001", "C123", "ts_001") == generate_thread_uuid("T001", "C123", "ts_001")
```

### Platform-Specific Mappings (Exact)

| Platform | sourceid | channelid | threadts |
|----------|----------|-----------|----------|
| **Slack** | team_id | channel_id | thread_ts or ts |
| **WhatsApp** | phone_number_id | from_number | wamid or message_id |
| **Email** | account_id | thread_id or subject_hash | date |
| **Twilio** | phone_number_id | sender_number | message_date |
| **Generic** | tenant_id or source_system | conversation_id or session_id | timestamp or message_id |

---

## LOGGING STANDARD (structlog Only — Non-Negotiable)

**FORBIDDEN**: `logging`, `print()`, `sys.stdout`  
**MANDATORY**: `structlog`

```python
import structlog

log = structlog.get_logger(__name__)

# Structured event logging with context binding
log.info(
    "request_received",
    toolid="slack_adapter",           # module.id
    eventid=event_id,                  # platform event ID
    source="slack",                    # platform name
    channel=channel_id,                # channel/conversation
    timestamp=datetime.utcnow().isoformat()
)

# On signature verification failure
log.warning(
    "signature_verification_failed",
    toolid="slack_adapter",
    expected=expected_sig,
    received=actual_sig,
    reason="HMAC mismatch"
)

# On AIOS call completion
log.info(
    "aios_call_complete",
    toolid="slack_adapter",
    elapsedms=elapsed,
    status=response.status_code,
    tokens=response.usage.total_tokens,
    result_length=len(response.content)
)

# On error
log.error(
    "handler_error",
    toolid="slack_adapter",
    error=str(e),
    errortype=type(e).__name__,
    traceback=traceback.format_exc(),
    context="webhook_processing"
)
```

### Required Log Events (All Tier 2 Modules)

1. `request_received` (info) — Webhook received
2. `signature_verified` (debug) — After signature check
3. `threaduuid_generated` (debug) — UUID computed
4. `dedupecheck` (debug) — Deduplication lookup done
5. `aioscall_start` (info) — Before AIOS call
6. `aioscall_complete` (info) — After AIOS call
7. `packet_stored` (info) — Packet persisted
8. `reply_sent` (info) — Reply sent to external service
9. `handler_error` (error) — Exception occurred

---

## QUALITY GATES (ALL SPECS MUST PASS)

### Pre-Generation Gates (Blocking)

- ✓ `moduleid_format`: lowercase, snake_case, no spaces
- ✓ `goals_specificity`: Specific and measurable
- ✓ `nongoals_locked`: Three locked non-goals present
- ✓ `threaduuid_deterministic`: UUIDv5 (Tier 2+)
- ✓ `httpclient_standard`: httpx (Tier 2+)
- ✓ `logging_standard`: structlog (all)
- ✓ `no_placeholders`: Zero `<placeholder>` tokens

### Post-Generation Gates (Blocking)

- ✓ `acceptance_coverage`: Each orchestration step has ≥1 criterion
- ✓ `errorpolicy_completeness`: All 5 categories defined
- ✓ `envvar_naming`: `MODULE_PREFIX_NAME` format
- ✓ `file_manifest_consistency`: Every file used or tested
- ✓ `tier_constraints`: No Tier 1 with packets, no Tier 3 missing state machine, etc.

### Failure = REJECT

If any gate fails, return spec to author with explicit reason. Do NOT generate code.

---

## SUCCESS CRITERIA

✅ **SPEC GENERATION COMPLETE** when:

1. ✓ All 35 modules specified (one Module-Spec-v2.5.yaml per module)
2. ✓ Zero placeholders (every field filled with real values)
3. ✓ All imports from MANUS_CONTEXT_PACK (no invented patterns)
4. ✓ All quality gates passing (no exceptions)
5. ✓ Dependency graph validated (no cycles, all blocking deps satisfied)
6. ✓ Tier 2 file manifests complete (all adapter/client/ingest files listed)
7. ✓ All acceptance criteria testable (test names match criteria)
8. ✓ Idempotency strategies documented (primary key, fallback, durability level)
9. ✓ Runtime wiring complete (docker service, startup deps, blocks_boot)
10. ✓ Packet contracts defined (ingress, egress, exact field shapes)

---

## EXECUTION PLAN

### Phase 1: Research (1 hour)
- Read all SSOT files (DOCTRINE, L9_RUNTIME_SSOT, L9_DEPENDENCIES_SSOT, L9_IDEMPOTENCY_SSOT, MANUS_CONTEXT_PACK)
- Extract patterns, imports, existing code locations
- Map dependency graph (Tier 0 → 1 → 2 → 3 + blocking/non-blocking)

### Phase 2: Specification (6–8 hours)
- Apply 6-Pass Workflow to each tier in order (Tier 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7)
- Apply Tier-Specific Operational Expansion Blocks for each tier
- Generate Module-Spec-v2.5.yaml for each module
- **DO NOT SKIP** Pass 6 quality gates

### Phase 3: Validation (1 hour)
- Run all 35 specs through quality gates
- Check for placeholder leaks
- Validate dependency graph (no cycles)
- Verify integration points (every spec can wire into runtime)

---

## APPENDIX: Quick Reference

### Core Imports (Copy-Paste)

```python
# Core schemas (MANUS_CONTEXT_PACK.md)
from core.agents.schemas import AgentTask, AgentConfig, AIOSResult, ToolCallRequest, ToolCallResult
from memory.substratemodels import PacketEnvelope, PacketEnvelopeIn, PacketMetadata, PacketLineage
from core.governance.schemas import Capability, AgentCapabilities, EvaluationRequest, EvaluationResult

# Services
from memory.substrateservice import MemorySubstrateService
from core.agents.executor import AgentExecutorService
from core.governance.engine import GovernanceEngine
from core.tools.registry_adapter import ToolRegistry

# Utilities
from uuid import uuid5, NAMESPACE_DNS
import structlog
import httpx
from fastapi import APIRouter, Request, Header, Depends
```

### Packet Type Naming

```
module.in              # Inbound webhook event
module.out             # Outbound response
module.error           # Error event
module.state.start     # State machine start (Tier 3)
module.state.transition # State transition (Tier 3)
module.audit           # Audit trail (Tier 3)
```

### Service Injection Pattern

```python
# ✓ CORRECT
@router.post("/events")
async def handle_webhook(request: Request, packet_in: PacketEnvelopeIn):
    service = request.app.state.substrateservice  # Injected at startup
    result = await service.writepacket(packet_in)
    return result

# ✗ WRONG
from memory.substrateservice import service  # Global singleton
@router.post("/events")
async def handle_webhook(packet_in: PacketEnvelopeIn):
    result = await service.writepacket(packet_in)  # NOT ALLOWED
```

### Thread UUID Test

```python
def test_threaduuid_deterministic():
    """Thread UUID must be deterministic."""
    uuid1 = generate_thread_uuid("T001", "C123", "ts_001")
    uuid2 = generate_thread_uuid("T001", "C123", "ts_001")
    assert uuid1 == uuid2, "Thread UUID must be deterministic"
```

---

**END OF CANONICAL SUPERPROMPT**

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 2.5.0 | 2025-12-17 | **HARDENED**: Added Tier-Specific Operational Expansion Blocks, runtime_wiring/dependency_contract/packet_contract sections, SSOT binding, DOCTRINE integration, pre/post gates, decision matrix, 6-Pass Workflow preserved |
| 2.1.0 | 2025-12-16 | Initial SuperPrompt with 6-Pass Workflow, decision matrix, Tier guidance |
| 1.0.0 | 2025-12-15 | Original MANUS module prompt |

---

## AUTHORITY & BINDING

This SuperPrompt is **CANONICAL**. 

Authority hierarchy (highest to lowest):
1. **DOCTRINE-Module-Spec.md** — Enterprise doctrine
2. **L9_RUNTIME_SSOT.md** — Deployment reality
3. **This SuperPrompt** — Orchestration and responsibility
4. **Module-Spec-v2.5.yaml** — Individual module schema

When in doubt, consult the SSOTs in this order: **L9_RUNTIME_SSOT.md**, **L9_DEPENDENCIES_SSOT.md**, **L9_IDEMPOTENCY_SSOT.md**, **MANUS_CONTEXT_PACK.md**.

**Conflict Resolution**: If this SuperPrompt conflicts with any SSOT, the SSOT wins. If conflict exists, escalate to Boss (decision owner).

---

**For Perplexity P-Prompt**: This is your authoritative source. Generate specs that satisfy all gates. Do NOT generate code if any gate fails.

**For C-Prompt (Code Generator)**: Expect specs that satisfy all gates. Consume spec fields directly. Do NOT invent behavior.

**For CI Gates**: Validate specs against gates before merge. Enforce deterministically.

---

**STATUS**: 🟢 PRODUCTION READY — Enterprise Deployment Grade  
**LAST UPDATED**: 2025-12-17  
**MAINTAINED BY**: L9 Architecture Team
