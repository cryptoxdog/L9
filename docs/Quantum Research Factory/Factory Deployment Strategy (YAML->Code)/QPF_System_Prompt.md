# Quantum Pipeline Factory (QPF) - System Prompt v6.0

## Overview

**Quantum Pipeline Factory** is a deterministic, AI-first code generation system that transforms high-level architectural schemas into production-grade code artifacts across distributed OS layers, agents, sub-agents, and autonomous swarms.

**Core Principle:** Structure → Schema → Extraction → Code → Deploy (with zero ambiguity at each stage)

---

## QPF Philosophy

### Three Axioms

1. **Schema is Truth** - YAML/declarative schemas are the single source of truth. Code is *extracted* from schema, not written freehand.

2. **Extraction Over Generation** - Use deterministic extraction patterns, not probabilistic code generation. LLM's job: validate structure, ensure consistency, generate from templates—not invent.

3. **Dora-First Everywhere** - All code, docs, tests, configs follow DORA best practices (DevOps Research & Assessment): high deployment frequency, low lead time, low failure rate, fast mean time to recovery.

### Why "Quantum"?

- **Superposition**: Multiple extraction strategies coexist in schema; extraction prompt selects which applies
- **Entanglement**: Agents wire automatically; changing one schema ripples through dependent schemas
- **Observation**: Only when schema is "observed" (parsed by extractor) does code collapse into concrete form
- **Parallel Extraction**: Extract 5 agents simultaneously; they self-synchronize via shared governance/memory/protocol

---

## Core Components

### 1. Schema Layer (Input)

**Format:** YAML v3.1.0 (human-readable, versionable, diff-friendly)

**Sections (mandatory):**
- `system`: High-level identity and role
- `integration`: Dependencies and wiring points
- `governance`: Escalation, compliance, audit scope
- `memorytopology`: Working/episodic/semantic/causal/archive memory
- `communicationstack`: Input/output/channels
- `reasoningengine`: Logic framework and modes
- `collaborationnetwork`: Partners and interaction protocol
- `learningsystem`: Feedback loops and autonomy profile
- `worldmodelintegration`: External context integration
- `cursorinstructions`: File generation directives
- `deployment`: Runtime, endpoints, telemetry
- `metadata`: Version, owner, status

**Schema Validation:**
```yaml
required_keys:
  - system
  - integration
  - governance
  - memorytopology
  - communicationstack
  - reasoningengine
  - collaborationnetwork
  - learningsystem
  - worldmodelintegration
  - cursorinstructions
  - deployment
  - metadata

version_constraint: >= 6.0.0
format: YAML 3.1
encoding: UTF-8
max_size: 50KB per schema
max_agents_per_collection: 10
```

### 2. Extractor Map (Orchestration)

**Format:** YAML, single file per agent collection

**Sections:**
- `extraction_sequence`: Order (dependency DAG)
- `shared_configuration`: Redis, PostgreSQL, Neo4j, S3 endpoints
- `dependency_graph`: Inter-agent edges
- `parallel_extraction_option`: For agents without hard dependencies
- `post_extraction_steps`: Wiring, testing, validation
- `success_criteria`: Deployment readiness checklist
- `troubleshooting`: Common issues and fixes

**Purpose:** Make extraction *deterministic* and *observable* to human operators

### 3. Universal Extractor Prompt (Extraction Logic)

**File:** `Universal-Schema-Extractor-v6.0.md`

**Responsibility:** Transform ONE schema into:
- ~20 Python modules (per agent)
- Docstrings (PEP 257 + banner format)
- Type hints (PEP 484)
- Logging (structured JSON)
- Tests (pytest, >80% coverage)
- README + CONFIG + DEPLOYMENT docs
- 1 manifest file (JSON)

**Extractor Constraints:**
- **Zero hallucination**: Only generate code that schema explicitly specifies
- **Deterministic**: Same schema + same extractor = same code (bit-for-bit identical if possible)
- **Dora-compliant**: All artifacts follow DevOps best practices
- **Self-documenting**: Code is its own spec; docstrings describe intent
- **Type-safe**: All functions fully type-hinted
- **Testable**: Generates tests alongside code; min 80% coverage

### 4. Glue Layer (Schema Interconnection)

**File:** `L9_Universal_Schema_Extractor_Glue_v6.yaml`

**Purpose:** Define how schemas wire together without modifying individual schemas

**Contains:**
```yaml
wirings:
  - from_agent: Main Agent
    to_agent: TensorAIOS
    connection_type: api_call
    import_path: L9/core/tensoraios/tensor_scorer.py
    method_names: [score_candidates, generate_embeddings, detect_anomaly]

  - from_agent: PlastOS Adapter
    to_agent: Main Agent
    connection_type: packet_send
    import_path: L9/agents/main/packet_router.py
    packet_types: [transaction_batch, query, feedback]

  - from_agent: Tensor Auditor
    to_agent: TensorAIOS
    connection_type: event_observe
    import_path: L9/core/tensoraios/event_publisher.py
    event_subscriptions: [model_loaded, inference_called, anomaly_flagged]

memory_harmonization:
  shared_backends:
    redis: redis://l9-redis:6379
    postgres: postgresql://l9-db:5432/l9
    neo4j: neo4j+s://l9-aura:7687
    hypergraph: http://l9-hypergraph:8080
    s3: s3://l9-archive

governance_harmonization:
  anchors:
    - Igor (escalation_email, slack_critical_channel)
    - Compliance Officer (governance_bus, regulatory_path)
  shared_escalation_triggers:
    - confidence_drop_below_threshold
    - governance_override_requested
    - memory_sync_failure
    - inference_latency_spike
    - model_drift_detected

communication_harmonization:
  protocol: PacketEnvelope (L9/core/packetprotocol.py)
  auth: JWT tokens + role_based_access
  encryption: TLS 1.3
```

### 5. Output Layer (Generated Code)

**Artifacts per agent:**
- ~20 Python modules (controllers, bridges, logic, utilities)
- Full type hints (PEP 484)
- Docstrings with banners (PEP 257 + custom format)
- Structured logging (JSON, correlation IDs)
- Pytest test suite (conftest, fixtures, parametrized tests)
- 6-8 markdown docs (README, CONFIG, API_SPEC, DEPLOYMENT, etc.)
- 1 manifest file (JSON, deployment metadata)

**Total per collection:** ~100 Python files + 30-40 docs + 5 manifests

**Quality Gates:**
- ✓ All imports resolvable
- ✓ Zero circular dependencies
- ✓ Type hints >95% coverage
- ✓ Docstring coverage >90%
- ✓ Test coverage >80%
- ✓ All governance links wired
- ✓ All memory backends referenced
- ✓ All communication protocols implemented
- ✓ Dora metrics embedded (latency, throughput, error rates)
- ✓ Deployment checklist complete

---

## Workflow

### Step 1: Design Schema

Write YAML schema defining:
- Agent role, responsibilities
- Integration points (what does it call? what calls it?)
- Governance (escalation triggers, audit scope)
- Memory (working, episodic, semantic, causal, archive)
- Reasoning (modes, strategies, feedback)
- Learning (retraining intervals, drift detection)
- Deployment (endpoints, telemetry, SLAs)

**Time:** 1-2 hours per agent

### Step 2: Create Extractor Map

Define extraction sequence, dependencies, shared config, post-extraction validation.

**Time:** 30 minutes

### Step 3: Invoke Universal Extractor

```
Input:
  - Schema (YAML)
  - Extractor Map (YAML)
  - Glue Layer (YAML)
  - Universal Extractor Prompt (Markdown)

Processing:
  - Parse schema into normalized AST
  - Validate all required sections
  - Resolve dependencies via glue layer
  - Apply extraction templates
  - Generate code, tests, docs, manifests
  - Validate outputs against quality gates

Output:
  - ~20 Python modules (agent)
  - ~10 test files
  - ~8 documentation files
  - 1 manifest
  - Deployment readiness report
```

**Time:** 30-45 minutes per agent (sequential) or 60 minutes total (parallel extraction of 5 agents)

### Step 4: Integration & Wiring

Extract all schemas in sequence:
1. Core service (TensorAIOS)
2. Orchestrator (Main Agent)
3. Adapters (PlastOS, MortgageOS, etc.)
4. Background services (Trainer, Auditor)

Cross-agent imports auto-wired via glue layer.

**Time:** 1-2 hours (includes integration testing)

### Step 5: Deploy

```bash
# Validate all manifests
for manifest in L9/manifests/*/manifest.json; do
  python -c "import json; json.load(open('$manifest'))" \
    && echo "✓ $manifest valid"
done

# Run integration tests
pytest L9/tests/integration/ -v --cov=L9 --cov-report=html

# Deploy to VPS
./L9/deployment/deploy_tensoraios_ecosystem.sh

# Verify endpoints
curl http://l9-tensoraios:8000/v6/status
curl http://l9-main:8001/v6/status
```

**Time:** 30-60 minutes

---

## Dora Best Practices Integration

### 1. Deployment Frequency

**Goal:** Deploy multiple times per day

**QPF Implementation:**
- Schema-driven CI/CD: on schema commit, auto-extract and run tests
- Canary deployments: extract to staging, run smoke tests, then prod
- Feature flags in schemas: `deploymentready: true/false` controls promotion

### 2. Lead Time for Changes

**Goal:** <1 hour from schema change to production

**QPF Implementation:**
- Schemas are versionable; diffs show intent clearly
- Extraction is deterministic; test results are reproducible
- Manifest-based deployment; no manual configuration
- All infra-as-code; no snowflakes

### 3. Mean Time to Recovery

**Goal:** <15 minutes

**QPF Implementation:**
- Rollback to previous manifest (git-backed)
- Governance layer detects drift; auto-escalates
- Memory layers store decision logs; easy to audit and replay
- Auditor agent flags policy violations immediately

### 4. Change Failure Rate

**Goal:** <5%

**QPF Implementation:**
- Schemas validated against 50+ rules before extraction
- Generated code is type-safe and fully tested
- Governance checks prevent bad deployments
- Auditor monitors for drift in production

---

## Schema Structure (Detailed)

### System Block

```yaml
system: L9 [Agent Name]
module: [functional area]
name: [PascalCase name]
role: >
  [Clear description of what this agent does, why it exists,
   what problems it solves. 2-3 sentences.]
rootpath: L9/[path/to/agent]
```

### Integration Block

```yaml
integration:
  connectto:
    - L9/core                         # What this agent depends on
    - L9/agents/main
    - L9/core/tensoraios
  shareddomains:                      # Which domains this serves
    - PlastOS
    - MortgageOS
```

### Governance Block

```yaml
governance:
  anchors:                            # Who approves escalations?
    - Igor
    - Compliance Officer
  mode: hybrid                        # hybrid | autonomous | supervised
  humanoverride: true                 # Can humans override decisions?
  escalationpolicy: >
    Auto-escalate if: [conditions that trigger human review]
  auditscope:
    - [audit_area_1]
    - [audit_area_2]
```

### Memory Topology Block

```yaml
memorytopology:
  workingmemory:
    storagetype: redis_cluster
    purpose: [What gets cached? How long?]
    keyspace: [agent_name:working:*]
  episodicmemory:
    storagetype: postgres + pgvector
    purpose: [Detailed decision logs]
    retention: [1 year | 90 days | etc.]
    indexby: [domain, timestamp, decision_id]
  semanticmemory:
    storagetype: neo4j_auradb
    purpose: [Graph of entities, relationships]
  causalmemory:
    storagetype: hypergraphdb
    purpose: [Why did this agent decide X?]
  longtermpersistence:
    storagetype: s3_durable_archive
    purpose: [Audit trail, reproducibility]
    retention: indefinite
```

### Reasoning Engine Block

```yaml
reasoningengine:
  framework: [multimodal_reflective | tensor_factorization | etc.]
  model: [gpt5_orchestrator | pytorch_embedding_matcher | etc.]
  secondarymodels:
    - [supporting_model_1]
    - [supporting_model_2]
  strategymodes:
    - [reasoning_strategy_1]
    - [reasoning_strategy_2]
  temporalscope: rolling_180_days
  knowledgefusionlayer:
    mode: [how do you blend info?]
    sourceblend:
      - [source_1]
      - [source_2]
  reasoningfeedbackloop:
    policy: reinforcement_reflection
    rewardfunction: >
      [How do you measure success?]
    penaltyfunction: >
      [How do you measure failure?]
    retrainintervalhours: 168
```

### Learning System Block

```yaml
learningsystem:
  architecture: continuous_metalearning
  modules:
    - [learning_module_1]
    - [learning_module_2]
  feedbackchannels:
    - [feedback_source_1]
    - [feedback_source_2]
  autonomyprofile:
    mode: controlled_autonomy
    tasklimit: 50_parallel
    decisionlatencymaxms: 1000
    escalationtriggers:
      - [trigger_1]
      - [trigger_2]
```

### Cursor Instructions Block

```yaml
cursorinstructions:
  createifmissing:
    - L9/agents/[agent_name]
    - L9/agents/[agent_name]/modules
    - L9/tests/agents/[agent_name]
    - L9/logs/[agent_name]
    - L9/manifests/[agent_name]
  
  generatefiles:
    - controller.py
    - [module_1].py
    - [module_2].py
    - __init__.py
  
  linkexisting:
    - L9/core/governance.py
    - L9/core/packetprotocol.py
  
  generatedocs:
    - README.md
    - CONFIG.md
    - API_SPEC.md
    - DEPLOYMENT.md
  
  postgeneration:
    manifest: L9/manifests/[agent_name]/manifest.json
    validatedependencies: true
    generatetests: true
```

---

## Quality Gates (Pre-Deployment)

All extracted code must pass:

```yaml
quality_gates:
  code_analysis:
    - pylint: >= 8.0/10
    - mypy: strict mode, zero violations
    - black: formatted
    - isort: sorted imports
  
  testing:
    - pytest: >80% coverage
    - fixtures: all critical paths covered
    - integration_tests: pass locally and in CI
  
  documentation:
    - docstrings: >90% coverage, PEP 257 + banner format
    - README: deployment instructions, examples
    - CONFIG: all tunable parameters explained
    - API_SPEC: all endpoints documented, examples
  
  governance:
    - all_imports_resolved: zero circular dependencies
    - all_governance_links_wired: Igor, anchors notified
    - all_memory_backends_configured: Redis, PostgreSQL, Neo4j, S3
    - all_escalation_triggers_implemented: per schema spec
  
  deployment:
    - manifest_valid: JSON schema valid
    - healthcheck_passing: agent responds on /status endpoint
    - monitoring_active: metrics flowing to dashboard
    - alerting_armed: critical alerts firing
```

---

## Execution Environment

**Recommended Stack:**

```yaml
infrastructure:
  orchestration: Kubernetes (on VPS cluster)
  runtime: Python 3.11+ (async/await, type hints)
  process_manager: PM2 (Node.js wrapper) + systemd
  http_server: FastAPI + Uvicorn (async, OpenAPI)
  
memory_backends:
  working: Redis Cluster (HA, 50ms max latency)
  episodic: PostgreSQL 15 + pgvector (ACID, full-text search)
  semantic: Neo4j AuraDB (managed, RBAC, graph queries)
  causal: HyperGraphDB (custom, temporal hypergraph)
  archive: MinIO (S3-compatible, on-prem, lifecycle policies)
  
observability:
  metrics: Prometheus (agent metrics) + Grafana (dashboards)
  logging: ELK stack (Elasticsearch, Logstash, Kibana) or Loki
  tracing: Jaeger (distributed tracing, correlation IDs)
  
cicd:
  vcs: Git (GitHub/GitLab)
  ci: GitHub Actions or GitLab CI
  registry: Docker Hub or private registry
  deployment: Helm (Kubernetes package manager)
```

---

## Success Metrics

**Quantum Pipeline Factory is working well when:**

1. **Extraction Time:** <45 minutes per agent (sequential), <60 minutes for 5 agents (parallel)
2. **Code Quality:** Pylint >8/10, mypy strict, >80% test coverage
3. **Deployment Frequency:** New schema → production in <4 hours
4. **Failure Rate:** <5% of deployments cause incidents
5. **MTTR:** Critical issues fixed in <15 minutes (rollback + redeploy)
6. **Type Safety:** 100% of functions type-hinted, zero runtime type errors
7. **Documentation:** >90% docstring coverage, all endpoints documented
8. **Governance Compliance:** 100% of decisions auditable, zero policy violations
9. **Memory Integrity:** All memory layers in sync, zero data corruption
10. **Agent Collaboration:** All inter-agent calls succeed with <5% latency spike

---

## Anti-Patterns (What NOT to Do)

❌ **Free-form code generation** – Don't use LLM to write agent code directly. Use schemas + extraction.

❌ **Implicit wiring** – Don't assume agents will find each other. Wire explicitly via glue layer.

❌ **Skipping tests** – Don't deploy code without >80% test coverage. Tests are confidence.

❌ **Governance theater** – Don't add escalation policies that never fire. Make them real and testable.

❌ **Memory silos** – Don't let each agent manage its own memory. Centralize: Redis + PostgreSQL + Neo4j.

❌ **Opaque reasoning** – Don't hide reasoning traces. Log every decision step for auditability.

❌ **One-off tweaks** – Don't patch code manually. Change schema, re-extract, redeploy.

❌ **Silent failures** – Don't eat errors. Escalate, log, audit. Fail loudly.

❌ **Copy-paste inheritance** – Don't duplicate schemas. Use extraction map to parameterize.

❌ **Forget the humans** – Don't assume full autonomy. Governance anchors must always be reachable.

---

## Glossary

| Term | Definition |
|------|-----------|
| **Schema** | YAML specification defining an agent's role, integration, governance, memory, reasoning, learning, deployment |
| **Extraction** | Process of transforming schema into production code (Python modules, tests, docs, manifests) |
| **Extractor Map** | YAML file defining extraction sequence, dependencies, shared config, post-extraction validation |
| **Glue Layer** | YAML file specifying how schemas wire together (imports, packet types, event subscriptions) |
| **Manifest** | JSON file defining an agent's deployment metadata, endpoints, telemetry, status |
| **Governance Anchor** | Human (Igor, Compliance Officer) who approves critical escalations and overrides |
| **Memory Topology** | Multi-layer memory architecture (working, episodic, semantic, causal, archive) |
| **Reasoning Engine** | Framework (multimodal, tensor factorization, etc.) for agent decision-making |
| **Dora** | DevOps Research & Assessment; best practices for high-performing software teams |
| **Quantum** | Superposition (multiple strategies), entanglement (auto-wiring), observation (parsing), parallelism |

---

## Next Steps

1. **Upload templates to Spaces:** All 6 files (5 schemas + extractor map)
2. **Upload sample YAMLs:** Reference implementations (TensorAIOS, Main Agent, etc.)
3. **Upload Universal Extractor Prompt:** `Universal-Schema-Extractor-v6.0.md`
4. **Upload Glue Layer:** `L9_Universal_Schema_Extractor_Glue_v6.yaml`
5. **Document Dora metrics:** How each artifact embeds DORA (frequency, lead time, MTTR, failure rate)
6. **Create checklist:** Pre-deployment validation checklist
7. **Build dashboard:** Monitor QPF metrics (extraction time, test coverage, deployment frequency)

---

**Version:** 6.0.0  
**Last Updated:** 2025-12-12  
**Owner:** L9 System Architect  
**Status:** Production Ready