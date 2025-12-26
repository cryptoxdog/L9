# ============================================================================
# L9 MODULE SPEC GENERATOR PROMPT FOR MANUS — v1.0.0
# ============================================================================
# Purpose: Generate complete Module Specs for ALL L9 modules
# Audience: Manus.im — Strategic spec generator
# Input: Repo summary files (repo_facts.md, repo_index.md, repo_supplement.md, code_index.md)
# Output: Complete Module-Spec-v2.0.yaml for EVERY module in L9 roadmap
# ============================================================================

SYSTEM:
  name: "L9 Module Spec Generator"
  version: "1.0.0"
  mode: "COMPREHENSIVE_SPEC_GENERATION"
  role: "You are an architect generating complete module specifications for L9 AI-OS"
  constraint: "Generate specs that align EXACTLY with existing repo patterns"

# ============================================================================
# SECTION 1: YOUR MISSION
# ============================================================================
MISSION:
  objective: |
    Generate COMPLETE Module Specs for ALL modules that L9 AI-OS needs.
    Each spec MUST follow Module-Spec-v2.0.yaml template EXACTLY.
    Each spec MUST be ready for Perplexity to generate wire-ready code.
    
  deliverables:
    - "One Module-Spec-v2.0.yaml per module"
    - "All specs follow identical structure"
    - "All specs reference existing repo patterns"
    - "All specs are comprehensive (no placeholders left)"
    
  success_criteria:
    - "Perplexity can generate code directly from each spec"
    - "Generated code wires into repo with zero drift"
    - "No ambiguity — every field is filled"

# ============================================================================
# SECTION 2: READ THESE FILES FIRST (MANDATORY)
# ============================================================================
REQUIRED_READING:
  priority_1_architecture:
    - file: "repo_facts.md"
      extract: "Core architectural constraints, patterns, forbidden behaviors"
    - file: "repo_index.md"
      extract: "File structure, existing modules, directory layout"
      
  priority_2_implementation:
    - file: "repo_supplement.md"
      extract: "Detailed code patterns, function signatures, import statements"
    - file: "code_index.md"
      extract: "All existing functions, classes, their signatures"
      
  priority_3_config:
    - file: "docker-compose.yml.md"
      extract: "Service configuration, environment variables"
      
  action: |
    READ ALL FILES COMPLETELY before generating any specs.
    Extract:
    - Existing import patterns
    - Function signature patterns
    - Service names and how they're used
    - Environment variable patterns
    - Error handling patterns
    - Packet types already defined

# ============================================================================
# SECTION 3: L9 MODULE ROADMAP (COMPLETE — 35 MODULES)
# ============================================================================
# Generate specs for ALL of these modules in dependency order
# ============================================================================
MODULE_ROADMAP:
  
  # ==========================================================================
  # TIER 0: OS KERNEL (P0 — Build First, Everything Depends on These)
  # ==========================================================================
  tier_0_os_kernel:
    - id: "tool.registry"
      name: "Tool Registry + Dispatcher"
      priority: "P0"
      tier: 0
      dependencies: []
      description: "Central tool registration, schema validation, governance-gated dispatch"
      interfaces:
        - "tools.register(tool_def) -> None"
        - "tools.list(tags, side_effects) -> list[ToolDef]"
        - "tools.get(tool_name) -> ToolDef | None"
        - "tools.validate(tool_name, args) -> ValidationResult"
        - "tools.select(intent, context, candidates) -> ToolSelection"
        - "tools.dispatch(tool_name, args, context) -> ToolResult"
      
    - id: "governance.engine"
      name: "Governance Policy Engine"
      priority: "P0"
      tier: 0
      dependencies: ["tool.registry"]
      description: "Policy evaluation, approval workflows, deny-by-default enforcement"
      interfaces:
        - "governance.evaluate(action, context) -> Decision"
        - "governance.request_approval(action) -> ApprovalTask"
        - "governance.check_capability(agent, tool) -> bool"
        - "governance.audit_log(decision) -> None"
      
    - id: "agent.executor"
      name: "Agent Executor"
      priority: "P0"
      tier: 0
      dependencies: ["tool.registry", "governance.engine"]
      description: "Agent instantiation, tool binding, capability-scoped execution loop"
      interfaces:
        - "executor.create(config, capabilities) -> Agent"
        - "executor.bind_tools(agent, tool_list) -> None"
        - "executor.run(agent, task) -> TaskResult"
        - "executor.terminate(agent_id) -> None"

  # ==========================================================================
  # TIER 1: INTEGRATION ADAPTERS (P1 — External IO Channels)
  # ==========================================================================
  tier_1_integrations:
    - id: "slack.adapter"
      name: "Slack Integration Adapter"
      priority: "P1"
      tier: 1
      dependencies: ["tool.registry"]
      description: "HMAC-verified webhooks, events, commands, thread management"
      has_existing_code: true
      existing_file: "api/webhook_slack.py"
      action: "REWRITE to align with Module-Spec pattern"
      
    - id: "email.adapter"
      name: "Email Integration Adapter"
      priority: "P1"
      tier: 1
      dependencies: ["tool.registry"]
      description: "IMAP/SMTP, email parsing, thread tracking"
      has_existing_code: true
      existing_file: "email_agent/"
      action: "ALIGN to use PacketEnvelopeIn and tool.registry"
      
    - id: "mac.automation"
      name: "Mac Automation Controller"
      priority: "P1"
      tier: 1
      dependencies: ["tool.registry", "governance.engine"]
      description: "AppleScript execution, app control, system commands as governed tools"
      has_existing_code: true
      existing_file: "mac_agent/"
      action: "WIRE to tool.registry and governance.engine"
      
    - id: "twilio.adapter"
      name: "Twilio SMS/Voice Adapter"
      priority: "P1"
      tier: 1
      dependencies: ["tool.registry"]
      description: "SMS/Voice webhooks, signature verification"
      has_existing_code: true
      existing_file: "api/webhook_twilio.py"
      action: "REWRITE to align with Module-Spec pattern"
      
    - id: "waba.adapter"
      name: "WhatsApp Business Adapter"
      priority: "P1"
      tier: 1
      dependencies: ["tool.registry"]
      description: "WhatsApp webhooks, message handling"
      has_existing_code: true
      existing_file: "api/webhook_waba.py"
      action: "REWRITE to align with Module-Spec pattern"
      
    - id: "calendar.adapter"
      name: "Calendar Integration Adapter"
      priority: "P2"
      tier: 1
      dependencies: ["tool.registry"]
      description: "Google/Apple calendar sync, event management"
      
    - id: "web.adapter"
      name: "Web Scraping Adapter"
      priority: "P2"
      tier: 1
      dependencies: ["tool.registry"]
      description: "URL fetching, content extraction, caching"
      
    - id: "webhook.receiver"
      name: "Generic Webhook Receiver"
      priority: "P2"
      tier: 1
      dependencies: ["tool.registry"]
      description: "Universal webhook ingestion with configurable signature verification"

  # ==========================================================================
  # TIER 2: AGENT INFRASTRUCTURE (P1 — Agent Lifecycle)
  # ==========================================================================
  tier_2_agent_infra:
    - id: "agent.lifecycle"
      name: "Agent Lifecycle Manager"
      priority: "P1"
      tier: 2
      dependencies: ["agent.executor"]
      description: "Spawn, monitor, terminate agents; restart on failure"
      interfaces:
        - "lifecycle.spawn(config) -> AgentHandle"
        - "lifecycle.terminate(agent_id) -> None"
        - "lifecycle.list_active() -> list[AgentHandle]"
        - "lifecycle.restart(agent_id) -> AgentHandle"
      
    - id: "agent.session"
      name: "Agent Session Manager"
      priority: "P1"
      tier: 2
      dependencies: ["agent.executor"]
      description: "Session state, context window management, memory scope"
      interfaces:
        - "session.create(agent_id, config) -> Session"
        - "session.get_context(session_id, depth) -> Context"
        - "session.checkpoint(session_id) -> CheckpointID"
        - "session.restore(checkpoint_id) -> Session"
      
    - id: "agent.capability"
      name: "Agent Capability Service"
      priority: "P1"
      tier: 2
      dependencies: ["governance.engine"]
      description: "Runtime capability grants, revocation, scoping"
      has_existing_code: true
      existing_file: "core/schemas/capabilities.py"
      action: "EXTEND with runtime grant/revoke APIs"
      
    - id: "agent.health"
      name: "Agent Health Monitor"
      priority: "P2"
      tier: 2
      dependencies: ["agent.lifecycle"]
      description: "Heartbeat, health checks, anomaly detection, auto-restart"

  # ==========================================================================
  # TIER 3: MEMORY SERVICES (P1 — Enhanced Memory Operations)
  # ==========================================================================
  tier_3_memory:
    - id: "memory.search"
      name: "Memory Search Service"
      priority: "P1"
      tier: 3
      dependencies: []
      description: "Unified search API across packet_store, semantic_memory, knowledge_facts"
      interfaces:
        - "search.query(query, filters) -> SearchResults"
        - "search.context(thread_id, depth) -> ContextPackets"
        - "search.similar(packet_id, top_k) -> list[PacketEnvelope]"
      has_existing_code: true
      existing_file: "memory/retrieval.py"
      action: "WRAP as dedicated service with API routes"
      
    - id: "memory.summarizer"
      name: "Memory Summarizer"
      priority: "P2"
      tier: 3
      dependencies: ["memory.search"]
      description: "Thread summarization, context compression, memory consolidation"
      
    - id: "memory.gc"
      name: "Memory Garbage Collector"
      priority: "P2"
      tier: 3
      dependencies: []
      description: "Scheduled housekeeping, TTL enforcement, orphan cleanup"
      has_existing_code: true
      existing_file: "memory/housekeeping.py"
      action: "WRAP with scheduler integration"
      
    - id: "memory.export"
      name: "Memory Export Service"
      priority: "P3"
      tier: 3
      dependencies: ["memory.search"]
      description: "Export memory to external systems, backup, migration"

  # ==========================================================================
  # TIER 4: SCHEDULING & ASYNC (P1 — Time-Based Operations)
  # ==========================================================================
  tier_4_scheduling:
    - id: "task.scheduler"
      name: "Task Scheduler"
      priority: "P1"
      tier: 4
      dependencies: ["agent.executor"]
      description: "Cron-like scheduling, deferred execution, recurring tasks"
      interfaces:
        - "scheduler.schedule(task, cron_expr) -> ScheduledTask"
        - "scheduler.defer(task, run_at) -> DeferredTask"
        - "scheduler.cancel(task_id) -> None"
        - "scheduler.list_pending() -> list[ScheduledTask]"
      
    - id: "task.queue"
      name: "Task Queue Service"
      priority: "P1"
      tier: 4
      dependencies: []
      description: "Persistent priority queue with Redis backing"
      has_existing_code: true
      existing_file: "runtime/task_queue.py"
      action: "ADD Redis persistence, dead-letter handling"
      
    - id: "event.bus"
      name: "Event Bus"
      priority: "P2"
      tier: 4
      dependencies: []
      description: "Pub/sub for internal events, topic-based routing"
      interfaces:
        - "bus.publish(topic, event) -> None"
        - "bus.subscribe(topic, handler) -> Subscription"
        - "bus.unsubscribe(subscription_id) -> None"
      
    - id: "event.replay"
      name: "Event Replay Service"
      priority: "P3"
      tier: 4
      dependencies: ["event.bus"]
      description: "Event replay for debugging, time-travel debugging"

  # ==========================================================================
  # TIER 5: DOMAIN OS PLUGIN SYSTEM (P2 — Extensibility)
  # ==========================================================================
  tier_5_domain_plugin:
    - id: "domain.registry"
      name: "Domain OS Registry"
      priority: "P2"
      tier: 5
      dependencies: ["tool.registry"]
      description: "Domain OS registration, discovery, version management"
      interfaces:
        - "domains.register(manifest) -> DomainHandle"
        - "domains.list() -> list[DomainManifest]"
        - "domains.get(domain_id) -> DomainManifest"
        - "domains.unregister(domain_id) -> None"
      
    - id: "domain.manifest"
      name: "Domain Manifest Schema"
      priority: "P2"
      tier: 5
      dependencies: ["domain.registry"]
      description: "Schema for domain declarations: tools, capabilities, events"
      
    - id: "domain.isolation"
      name: "Domain Isolation Service"
      priority: "P2"
      tier: 5
      dependencies: ["domain.registry", "governance.engine"]
      description: "Domain sandboxing, resource limits, fault isolation"
      
    - id: "domain.events"
      name: "Domain Event Bridge"
      priority: "P2"
      tier: 5
      dependencies: ["domain.registry", "event.bus"]
      description: "Domain event subscription, cross-domain messaging"

  # ==========================================================================
  # TIER 6: SECURITY & SECRETS (P2 — Production Hardening)
  # ==========================================================================
  tier_6_security:
    - id: "secrets.vault"
      name: "Secrets Vault"
      priority: "P2"
      tier: 6
      dependencies: []
      description: "Secure secret storage, encryption at rest"
      interfaces:
        - "vault.get(key, scope) -> SecretValue"
        - "vault.set(key, value, scope) -> None"
        - "vault.delete(key) -> None"
        - "vault.list_scopes() -> list[str]"
      
    - id: "secrets.rotation"
      name: "Secret Rotation Service"
      priority: "P3"
      tier: 6
      dependencies: ["secrets.vault", "task.scheduler"]
      description: "Automatic key rotation, expiry management"
      
    - id: "auth.gateway"
      name: "Auth Gateway"
      priority: "P2"
      tier: 6
      dependencies: []
      description: "Centralized auth: API keys, OAuth, JWT validation"
      has_existing_code: true
      existing_file: "api/auth.py"
      action: "EXTEND with OAuth, JWT, multi-tenant support"
      
    - id: "audit.log"
      name: "Audit Log Service"
      priority: "P2"
      tier: 6
      dependencies: []
      description: "Immutable audit trail, compliance logging"
      has_existing_code: true
      action: "DEDICATED service with retention policies"

  # ==========================================================================
  # TIER 7: OBSERVABILITY (P3 — Operations)
  # ==========================================================================
  tier_7_observability:
    - id: "metrics.collector"
      name: "Metrics Collector"
      priority: "P3"
      tier: 7
      dependencies: []
      description: "Prometheus-style metrics, counters, histograms"
      
    - id: "tracing.distributed"
      name: "Distributed Tracing"
      priority: "P3"
      tier: 7
      dependencies: []
      description: "OpenTelemetry integration, trace propagation"
      
    - id: "alerts.engine"
      name: "Alerts Engine"
      priority: "P3"
      tier: 7
      dependencies: ["metrics.collector"]
      description: "Alert rules, thresholds, notification routing"
      
    - id: "dashboard.api"
      name: "Dashboard API"
      priority: "P3"
      tier: 7
      dependencies: ["metrics.collector"]
      description: "Metrics/status API for UI dashboards"

  # ==========================================================================
  # MAC DOMAIN OS EXTENSIONS (P2 — Mac-Specific)
  # ==========================================================================
  mac_extensions:
    - id: "mac.finder"
      name: "Mac Finder Integration"
      priority: "P2"
      tier: 1
      dependencies: ["mac.automation"]
      description: "File operations, folder management, Spotlight search"
      
    - id: "mac.notifications"
      name: "Mac Notifications Handler"
      priority: "P2"
      tier: 1
      dependencies: ["mac.automation"]
      description: "System notifications, alerts, user prompts"

# ============================================================================
# SECTION 4: SPEC TEMPLATE (USE THIS EXACTLY)
# ============================================================================
SPEC_TEMPLATE: |
  # ============================================================================
  # L9 MODULE SPEC: {{MODULE_NAME}}
  # ============================================================================
  # Generated by: Manus
  # Template version: 2.0.0
  # Ready for: Perplexity code generation
  # ============================================================================
  
  module:
    id: "{{module_id}}"
    name: "{{Module Name}}"
    purpose: "{{One-line purpose from MODULE_ROADMAP}}"
    system: "L9"
    language: "python"
    runtime: "python>=3.11"
    owner: "Boss"
  
  goals:
    - "{{Primary goal}}"
    - "{{Secondary goal}}"
    - "{{Third goal if needed}}"
  
  non_goals:
    - "{{What this module does NOT do}}"
    - "No new database tables"
    - "No new migrations"
    - "No parallel memory/logging/config systems"
  
  repo:
    root_path: "/Users/ib-mac/Projects/L9"
    allowed_new_files:
      - "{{List all files this module will create}}"
    allowed_modified_files:
      - "api/server.py"
    must_import_and_use:
      - "{{From repo_supplement.md — exact imports}}"
    must_not_create:
      - "parallel {{domain}} layer"
      - "duplicate services"
  
  interfaces:
    inbound:
      - name: "{{interface_name}}"
        method: "{{POST|GET}}"
        route: "/{{module}}/{{action}}"
        headers:
          - "{{Required headers}}"
        payload_type: "JSON"
        auth: "{{hmac-sha256|bearer|api_key|internal}}"
    outbound:
      - name: "{{outbound_call}}"
        endpoint: "{{endpoint}}"
        method: "POST"
        timeout_seconds: {{timeout}}
        retry: {{true|false}}
  
  environment:
    required:
      - name: "{{ENV_VAR_NAME}}"
        description: "{{What it's for}}"
        example: "{{example_value}}"
    optional:
      - name: "{{OPTIONAL_VAR}}"
        description: "{{What it's for}}"
        default: "{{default_value}}"
  
  orchestration:
    validation:
      - "{{Step 1}}"
      - "{{Step 2}}"
    context_reads:
      - method: "{{method_name}}"
        filter: "{{filter}}"
        purpose: "{{why}}"
    aios_calls:
      - endpoint: "/chat"
        input: "{{what goes in}}"
        output: "{{what comes out}}"
    side_effects:
      - action: "{{What happens}}"
        service: "{{service.method}}"
        packet_type: "{{module}}.{{in|out}}"
  
  idempotency:
    enabled: {{true|false}}
    dedupe_key:
      primary: "{{primary_key}}"
      fallback: "{{fallback_key}}"
    on_duplicate: "return {ok: true, dedupe: true}"
    thread_id:
      type: "UUIDv5"
      namespace: "{{module}}.l9.internal"
      components:
        - "{{component_1}}"
        - "{{component_2}}"
  
  error_policy:
    invalid_signature:
      status: 401
      action: "Reject immediately"
      log: "signature_invalid"
    aios_failure:
      status: 200
      action: "Log error, return ok"
      log: "aios_call_failed"
    side_effect_failure:
      status: 200
      action: "Log error, return ok"
      log: "{{action}}_failed"
    storage_failure:
      status: 200
      action: "Log error, continue"
      log: "packet_storage_failed"
  
  acceptance:
    required:
      - criterion: "{{What must be true}}"
        test: "test_{{criterion_snake_case}}"
    forbidden:
      - "Creates new database tables"
      - "Duplicates memory substrate code"
      - "Uses module-level singletons"
      - "Reads env vars at import time"
      - "Uses aiohttp instead of httpx"
  
  observability:
    required_logs:
      - event: "{{event_name}}"
        level: "{{info|debug|error}}"
        fields: ["{{field1}}", "{{field2}}"]
    metrics:
      - "{{module}}_requests_total"
      - "{{module}}_errors_total"
      - "{{module}}_latency_seconds"
  
  data_contracts:
    {{Define any module-specific data structures}}
  
  notes_for_perplexity:
    - "Use REPO_CONTEXT_PACK imports exactly"
    - "Use PacketEnvelopeIn for all packets"
    - "Use UUIDv5 for thread_id (not uuid4)"
    - "All handlers accept injected services (no singletons)"
    - "Route handlers get services from request.app.state"
    - "Include all tests from acceptance.required"
    - "Include WIRING_SNIPPET for server.py"

# ============================================================================
# SECTION 5: GENERATION RULES
# ============================================================================
GENERATION_RULES:
  
  R1_NO_PLACEHOLDERS:
    rule: "Every {{placeholder}} MUST be replaced with actual values"
    violation: "Spec is incomplete — do not output"
    
  R2_MATCH_REPO_PATTERNS:
    rule: "All imports, patterns, signatures MUST match repo_supplement.md"
    example: |
      CORRECT: "from memory.substrate_service import MemorySubstrateService"
      WRONG: "from memory.service import SubstrateService"
      
  R3_REALISTIC_INTERFACES:
    rule: "Interfaces must be implementable — no fantasy APIs"
    example: |
      CORRECT: route "/slack/events" with headers X-Slack-Signature
      WRONG: route "/magic/do_everything" with no auth
      
  R4_COMPLETE_ACCEPTANCE:
    rule: "Every acceptance criterion MUST have a corresponding test name"
    example: |
      criterion: "Signature verification blocks invalid requests"
      test: "test_invalid_signature_returns_401"
      
  R5_IDEMPOTENCY_KEYS:
    rule: "Dedupe keys MUST be unique identifiers from the source system"
    example: |
      Slack: event_id or message_ts
      Email: message_id
      Webhook: X-Request-ID header
      
  R6_PACKET_TYPES:
    rule: "Packet types follow pattern: {{module}}.{{direction}}"
    examples:
      - "slack.in" — inbound Slack event
      - "slack.out" — outbound Slack response
      - "tool.call.request" — tool call initiated
      - "tool.call.result" — tool call completed

# ============================================================================
# SECTION 6: OUTPUT FORMAT
# ============================================================================
OUTPUT_FORMAT:
  structure: |
    For EACH module in MODULE_ROADMAP, output:
    
    ---
    ## Module Spec: {{module.name}}
    
    ```yaml
    [Complete Module-Spec-v2.0.yaml with ALL fields filled]
    ```
    
    ---
    
  order:
    1: "Core modules (P0) first"
    2: "Integration modules (P1) second"
    3: "Mac modules"
    4: "Memory modules"
    5: "Utility modules"
    
  completeness_check:
    before_outputting_each_spec:
      - "[ ] All {{placeholders}} replaced"
      - "[ ] Imports match repo patterns"
      - "[ ] All acceptance criteria have tests"
      - "[ ] Error policy is complete"
      - "[ ] Idempotency config makes sense"
      - "[ ] Environment variables are realistic"

# ============================================================================
# SECTION 7: EXTRACTION CHECKLIST
# ============================================================================
EXTRACTION_CHECKLIST:
  from_repo_facts:
    - "Core architectural constraints"
    - "Forbidden patterns"
    - "Required patterns"
    
  from_repo_index:
    - "Existing file structure"
    - "Where new files should go"
    - "Naming conventions"
    
  from_repo_supplement:
    - "Exact import statements"
    - "Function signatures"
    - "Class definitions"
    - "Error handling patterns"
    
  from_code_index:
    - "All existing functions by file"
    - "All existing classes"
    - "What's already implemented"
    
  from_docker_compose:
    - "Service names"
    - "Environment variables"
    - "Port mappings"

# ============================================================================
# SECTION 8: QUALITY GATES
# ============================================================================
QUALITY_GATES:
  
  gate_1_completeness:
    check: "No {{placeholders}} remain in output"
    action: "Scan each spec for {{ and }}"
    
  gate_2_consistency:
    check: "All specs use same patterns"
    action: "Compare imports across specs"
    
  gate_3_implementability:
    check: "Each spec can be implemented"
    action: "Verify interfaces are realistic"
    
  gate_4_testability:
    check: "Each acceptance criterion is testable"
    action: "Verify test names are specific"

# ============================================================================
# SECTION 9: FINAL OUTPUT
# ============================================================================
FINAL_OUTPUT:
  format: |
    # L9 AI-OS Module Specifications
    
    Generated: {{date}}
    Total Modules: 35
    
    ## Summary by Tier
    
    | Tier | Name | Count | Priority |
    |------|------|-------|----------|
    | T0 | OS Kernel | 3 | P0 |
    | T1 | Integrations | 10 | P1-P2 |
    | T2 | Agent Infra | 4 | P1-P2 |
    | T3 | Memory Services | 4 | P1-P3 |
    | T4 | Scheduling | 4 | P1-P3 |
    | T5 | Domain Plugin | 4 | P2 |
    | T6 | Security | 4 | P2-P3 |
    | T7 | Observability | 4 | P3 |
    | **TOTAL** | | **35** | |
    
    ## Module Index
    
    | # | Module ID | Name | Tier | Priority | Dependencies |
    |---|-----------|------|------|----------|--------------|
    | 1 | tool.registry | Tool Registry | T0 | P0 | - |
    | 2 | governance.engine | Governance Engine | T0 | P0 | tool.registry |
    | 3 | agent.executor | Agent Executor | T0 | P0 | tool.registry, governance.engine |
    | ... | ... | ... | ... | ... | ... |
    
    ---
    
    ## Module Specs (35 total)
    
    [Each complete spec in YAML format, grouped by tier]
    
    ---
    
    ## Generation Notes
    
    - Patterns extracted from: repo_supplement.md
    - File structure from: repo_index.md
    - Constraints from: repo_facts.md
    - Existing code identified for: ALIGN/REWRITE/WIRE actions
    
  attestation: |
    ## MANUS ATTESTATION
    
    | Check | Status |
    |-------|--------|
    | All repo files read | ✅ |
    | All 35 modules specified | ✅ |
    | No placeholders remaining | ✅ |
    | Imports match repo | ✅ |
    | Dependencies validated | ✅ |
    | Existing code flagged | ✅ |
    | All acceptance testable | ✅ |
    | Ready for Perplexity | ✅ |

# ============================================================================
# SECTION 10: INSTRUCTIONS FOR MANUS
# ============================================================================
INSTRUCTIONS:
  role: |
    You are a module architect. Your job is to:
    1. Read ALL repo summary files
    2. Understand L9's architecture and patterns
    3. Generate COMPLETE specs for EVERY module
    4. Ensure specs are ready for Perplexity code generation
    
  workflow: |
    1. READ all files in Repo-Summary folder
    2. EXTRACT patterns, imports, signatures
    3. For EACH module in MODULE_ROADMAP:
       - Fill SPEC_TEMPLATE completely
       - Replace ALL placeholders
       - Verify against GENERATION_RULES
       - Pass QUALITY_GATES
    4. Output all specs in OUTPUT_FORMAT
    5. Include FINAL_OUTPUT attestation
    
  critical_rules: |
    - Do NOT leave any {{placeholders}}
    - Do NOT invent imports not in repo
    - Do NOT create fantasy interfaces
    - Do NOT skip any module
    - Every spec MUST be Perplexity-ready

# ============================================================================
# END OF MANUS PROMPT
# ============================================================================

