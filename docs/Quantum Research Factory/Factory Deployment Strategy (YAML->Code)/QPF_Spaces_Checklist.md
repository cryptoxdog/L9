# Quantum Pipeline Factory - Spaces Upload Checklist & Reference Guide

**Version:** 6.0.0  
**Last Updated:** 2025-12-12  
**For:** L9 Spaces: "Quantum Pipeline Factory"

---

## What to Upload to Spaces

### Core Files (MUST HAVE)

- [ ] **QPF_System_Prompt.md** – Main system prompt for the space
- [ ] **QPF_10Point_Guide.md** – 10 optimizations & enhancements
- [ ] **Quantum_Pipeline_Factory_Spaces_Upload_Checklist.md** – This file

### Schema Files (REFERENCE IMPLEMENTATIONS)

- [ ] **L9_TensorAIOS_Schema_v6.yaml** – Core service schema
- [ ] **L9_MainAgent_Schema_v6.yaml** – Orchestrator schema
- [ ] **L9_PlastOS_Adapter_Schema_v6.yaml** – Domain adapter schema
- [ ] **L9_TensorTrainer_Schema_v6.yaml** – Learning pipeline schema
- [ ] **L9_TensorAuditor_Schema_v6.yaml** – Governance monitoring schema

### Extraction Infrastructure (CRITICAL)

- [ ] **L9_TensorAIOS_Extractor_Map_v6.0.yaml** – Execution orchestration
- [ ] **L9_Universal_Schema_Extractor_Glue_v6.yaml** – Cross-agent wiring
- [ ] **Universal-Schema-Extractor-v6.0.md** – Extraction prompt (if available)

### Documentation (SUPPLEMENTAL BUT VALUABLE)

- [ ] **Dora_Metrics_Compliance_Guide.md** – How QPF embeds DORA best practices
- [ ] **Quality_Gate_Checklist.md** – Pre-deployment validation criteria
- [ ] **Schema_Structure_Reference.md** – Field-by-field schema breakdown
- [ ] **Extraction_Observability_Guide.md** – Metrics, dashboards, alerting
- [ ] **Sub_Agent_Templates.yaml** – Reusable sub-agent templates
- [ ] **Anti_Patterns_and_Gotchas.md** – Common mistakes to avoid

### Optional Advanced Files

- [ ] **Schema_Versioning_Migration_Examples.md** – Real examples of schema evolution
- [ ] **Swarm_Coordination_Patterns.yaml** – Flocking, consensus, byzantine voting
- [ ] **Cross_Domain_Learning_Case_Studies.md** – PlastOS + MortgageOS + ForgeOS examples
- [ ] **Self_Healing_Deployment_Runbook.md** – Health checks, recovery actions, escalation

---

## How to Use These Files in Spaces

### Recommended Space Structure

```
Quantum Pipeline Factory (Main Space)
│
├── 📖 Guides & Documentation
│   ├── QPF_System_Prompt.md ← READ FIRST
│   ├── QPF_10Point_Guide.md
│   ├── Dora_Metrics_Compliance_Guide.md
│   ├── Quality_Gate_Checklist.md
│   ├── Anti_Patterns_and_Gotchas.md
│
├── 🏗️ Schemas (Reference Implementations)
│   ├── L9_TensorAIOS_Schema_v6.yaml
│   ├── L9_MainAgent_Schema_v6.yaml
│   ├── L9_PlastOS_Adapter_Schema_v6.yaml
│   ├── L9_TensorTrainer_Schema_v6.yaml
│   ├── L9_TensorAuditor_Schema_v6.yaml
│   ├── Sub_Agent_Templates.yaml
│
├── 🔧 Extraction Infrastructure
│   ├── L9_TensorAIOS_Extractor_Map_v6.0.yaml
│   ├── L9_Universal_Schema_Extractor_Glue_v6.yaml
│
├── 📊 Advanced Topics
│   ├── Schema_Versioning_Migration_Examples.md
│   ├── Swarm_Coordination_Patterns.yaml
│   ├── Cross_Domain_Learning_Case_Studies.md
│   ├── Self_Healing_Deployment_Runbook.md
│   ├── Extraction_Observability_Guide.md
│
└── 🚀 Quick Reference
    ├── Schema_Structure_Reference.md
    └── FAQ_and_Troubleshooting.md
```

### How Cursor Will Use These

1. **You ask Cursor:** "Generate an agent schema for a new domain"
2. **Cursor reads:** QPF_System_Prompt.md (understands philosophy)
3. **Cursor references:** One of the sample schemas (TensorAIOS, Main, PlastOS)
4. **Cursor generates:** New schema following the exact pattern
5. **Cursor validates:** Against Quality_Gate_Checklist.md
6. **You provide:** Schema to Cursor + Extractor Map + Glue Layer
7. **Cursor extracts:** ~20 Python files + tests + docs + manifest
8. **You deploy:** Agent is ready for production

---

## Key Concepts Cursor Needs to Understand

### 1. Schema as Single Source of Truth

**What it means:**
- Schema is written in YAML (human-readable, versionable)
- Schemas define WHAT an agent is, not HOW to implement it
- Code is EXTRACTED (deterministic) not written freehand

**Example:**
```yaml
# Schema says:
reasoningengine:
  framework: multimodal_reflective
  strategymodes:
    - symbolic_rule_application
    - tensor_guided_scoring
    - causal_context_enrichment

# Extractor generates:
# - L9/agents/main/symbolic_reasoner.py
# - L9/agents/main/tensor_reasoner.py
# - L9/agents/main/causal_reasoner.py
# - L9/agents/main/reasoning_synthesizer.py (combines all 3)
```

### 2. Extraction vs Generation

**Extraction (GOOD):**
- Schema → AST → Template matching → Code
- Deterministic (same schema = same code)
- Auditable (changes tracked via schema diffs)

**Generation (BAD):**
- "Write me a Python service" → LLM invents code
- Non-deterministic (different code each time)
- Hard to audit

**QPF uses:** Extraction + templates, not free-form generation

### 3. Dora Alignment

All extracted code embeds these metrics:
- **Deployment Frequency:** How often can you deploy? (daily, weekly)
- **Lead Time for Changes:** How long schema → production? (<4 hours in QPF)
- **Mean Time to Recovery:** How fast can you recover from failure? (<15 minutes in QPF)
- **Change Failure Rate:** % of deployments causing incidents? (<5% in QPF)

### 4. Shared Infrastructure

All agents share:
- **Communication:** PacketEnvelope protocol (L9/core/packetprotocol.py)
- **Memory:** Redis (working), PostgreSQL (episodic), Neo4j (semantic), HyperGraphDB (causal), S3 (archive)
- **Governance:** Igor, Compliance Officer, Domain Oversight Council (escalation anchors)
- **Logging:** Structured JSON logs with correlation IDs
- **Telemetry:** Prometheus metrics → Grafana dashboards

### 5. Schema Sections Explained

| Section | Purpose | Example |
|---------|---------|---------|
| `system` | Identity (name, role, path) | `name: TensorAIOS, role: Tensor scoring service` |
| `integration` | Dependencies (what does it call?) | `connectto: [L9/core, L9/worldmodel]` |
| `governance` | Escalation policy, audit scope | `escalationpolicy: if confidence < 0.7 AND criticality > 0.8` |
| `memorytopology` | Memory layers (working, episodic, semantic, causal, archive) | `workingmemory: redis, episodicmemory: postgres` |
| `communicationstack` | Input/output channels (REST, packets, events) | `input: [structuredapi, messagesqueue]` |
| `reasoningengine` | How agent decides (modes, models, strategies) | `strategymodes: [symbolic, tensor, causal, analogical]` |
| `collaborationnetwork` | Partner agents, interaction protocol | `partners: [Main, Trainer, Auditor]` |
| `learningsystem` | Feedback loops, autonomy profile | `retrainintervalhours: 168` |
| `worldmodelintegration` | External context (causal factors, market data) | `activemodels: [causal_model, temporal_model]` |
| `cursorinstructions` | File generation directives (tell Cursor what to generate) | `generatefiles: [tensor_scorer.py, embedding_generator.py, ...]` |
| `deployment` | Endpoints, telemetry, alerting | `endpoints: [{path: /score, method: POST, timeout_ms: 500}]` |
| `metadata` | Version, owner, status | `version: 6.0.0, status: production_ready` |

---

## Workflow: From Schema to Production

### Step 1: Design Schema (You)

**Action:** Write or customize YAML schema

```bash
# Copy sample schema as starting point
cp L9_TensorAIOS_Schema_v6.yaml my_new_agent_schema.yaml

# Edit to match your agent
nano my_new_agent_schema.yaml
```

**Cursor's role:** Answer questions about schema structure

### Step 2: Create Extractor Map (You or Cursor)

**Action:** Define extraction sequence, dependencies, shared config

```yaml
extraction_sequence:
  order:
    1:
      agent: MyNewAgent
      schema_file: my_new_agent_schema.yaml
    # ... more agents
```

**Cursor's role:** Generate extractor map based on schema list

### Step 3: Invoke Extraction (Cursor)

**Action:** Feed Cursor:
1. Your schema (YAML)
2. Extractor map (YAML)
3. Glue layer (YAML)
4. This system prompt (QPF_System_Prompt.md)

**Prompt to Cursor:**
```
Here's my agent schema, extractor map, and glue layer.
Using the Quantum Pipeline Factory system prompt:
1. Validate schema against quality gates
2. Generate all files per cursorinstructions
3. Output a manifest showing what was generated
4. Provide deployment checklist
```

**Cursor's role:** Extract code, tests, docs, manifests

### Step 4: Integration & Testing (You)

**Action:**
```bash
# Run integration tests
pytest L9/tests/integration/ -v --cov

# Check type hints
mypy L9/agents/my_new_agent --strict

# Check linting
pylint L9/agents/my_new_agent
```

**Cursor's role:** Generate tests; help troubleshoot failures

### Step 5: Deploy (You + Governance)

**Action:**
```bash
# Get governance approval for production deployment
curl -X POST http://governance-api/request-approval \
  -H "Content-Type: application/json" \
  -d @deployment-manifest.json

# After approval, deploy
helm install my-agent L9/charts/agent/ \
  -f L9/agents/my_new_agent/values.yaml

# Verify endpoints
curl http://my-agent:8000/status
```

**Cursor's role:** Generate deployment scripts, helm charts, health checks

---

## Common Cursor Prompts for QPF

### Prompt 1: Generate New Agent Schema

```
I need a new agent for [domain/purpose].

Here's the context:
- Role: [what should it do?]
- Integrations: [what should it talk to?]
- Governance: [any special constraints?]

Using QPF, generate a schema following these samples:
- L9_TensorAIOS_Schema_v6.yaml
- L9_MainAgent_Schema_v6.yaml

Validate against Quality_Gate_Checklist.md.
```

### Prompt 2: Extract Agent Code

```
I have a schema: my_agent_schema.yaml
And an extractor map: my_extractor_map.yaml
And a glue layer: L9_Universal_Schema_Extractor_Glue_v6.yaml

Using the Universal-Schema-Extractor-v6.0.md prompt:
1. Parse the schema
2. Validate all sections are present
3. Generate ~20 Python modules following the structure
4. Generate tests with >80% coverage
5. Generate documentation (README, CONFIG, API_SPEC, DEPLOYMENT)
6. Generate manifest (JSON, deployment metadata)

Output a file tree showing what was generated.
```

### Prompt 3: Validate Schema Compliance

```
I have this schema: my_schema.yaml

Check it against:
1. Quality_Gate_Checklist.md
2. Schema_Structure_Reference.md
3. Dora_Metrics_Compliance_Guide.md

Report:
- ✓ Passed checks
- ⚠️ Warnings
- ❌ Failed checks
- 🔧 Suggested fixes
```

### Prompt 4: Generate Extraction Map

```
I have these 5 schemas:
1. L9_TensorAIOS_Schema_v6.yaml
2. L9_MainAgent_Schema_v6.yaml
3. L9_PlastOS_Adapter_Schema_v6.yaml
4. L9_TensorTrainer_Schema_v6.yaml
5. L9_TensorAuditor_Schema_v6.yaml

Generate an extraction map that:
- Defines correct dependency order
- Shows which agents depend on which
- Specifies shared configuration
- Includes post-extraction steps
- Lists success criteria
```

### Prompt 5: Optimize Existing Agent

```
I have this agent: L9/agents/my_agent/

Using QPF's 10-point optimization guide:
1. Review current implementation
2. Identify which optimizations apply
3. Suggest top 3 improvements (with effort/ROI)
4. Generate TODO tasks for implementation

Prioritize by ROI (return on investment).
```

---

## Anti-Patterns: What NOT to Do

### ❌ Don't: Free-Form Code Writing

```
# BAD: Ask Cursor to write code without schema
"Write me a Python service that handles transactions"
→ Cursor generates code, but it's:
  - Not reproducible (different code each time)
  - Hard to audit (no schema diff to explain changes)
  - Likely to have gaps (governance, memory, logging incomplete)

# GOOD: Use schema + extraction
1. Write schema defining what service does
2. Use Universal Extractor to generate code
3. Code is reproducible, auditable, complete
```

### ❌ Don't: Manual Code Modifications

```
# BAD: Edit generated code by hand
# Generated file: L9/agents/main/packet_router.py
# You: Edit it manually to add new behavior

→ Problem: Next schema change → re-extraction → your changes lost

# GOOD: Change schema, re-extract
1. Update schema (add new field to reasoningengine.strategymodes)
2. Re-run extraction
3. All changes automatic, tracked in schema
```

### ❌ Don't: Skip Governance

```
# BAD: Deploy agent without governance approval
curl -X POST http://kubernetes/deploy \
  -d agent.yaml

→ Problem: Governance auditor flags compliance violation, agent disabled

# GOOD: Request governance approval first
curl -X POST http://governance-api/request-approval \
  -d deployment-manifest.json

# Wait for approval
# Then deploy
```

### ❌ Don't: Flat Schemas for Complex Agents

```
# BAD: One giant schema with 500 lines

# GOOD: Hierarchical schemas
- Base schema (100 lines): orchestrator.yaml
- Sub-schemas (50 lines each):
  - packet_router.yaml
  - context_enricher.yaml
  - tensor_coordinator.yaml
  - reasoning_engine.yaml
  - governance_bridge.yaml
```

### ❌ Don't: Ignore Dora Metrics

```
# BAD: Generate code without embedding metrics
- No deployment frequency tracking
- No lead time measurements
- No MTTR automation
- No change failure alerting

# GOOD: Every schema generates code that tracks:
- Deployment latency
- Request throughput
- Error rates
- P99 latencies
```

---

## Quick Reference: Schema Template

**Use this as a starting point for new schemas:**

```yaml
---
title: "[Agent Name] v6.0"
version: 6.0.0
created: 2025-12-12
owner: L9 System Architect

system: L9 [Agent Name]
module: [core | adapter | orchestration | governance]
name: [PascalCase]
role: >
  [2-3 sentence description of what this agent does]

rootpath: L9/[path/to/agent]

integration:
  connectto:
    - L9/core                         # Core infrastructure
    - L9/agents/main                  # Other agents
  shareddomains:
    - PlastOS

governance:
  anchors:
    - Igor
    - Compliance Officer
  mode: hybrid
  humanoverride: true
  escalationpolicy: >
    Auto-escalate if: [conditions]

memorytopology:
  workingmemory:
    storagetype: redis_cluster
    purpose: [description]
    keyspace: [agent_name:working:*]
  episodicmemory:
    storagetype: postgres + pgvector
    purpose: [description]
    retention: 1 year
    indexby: [domain, timestamp]
  semanticmemory:
    storagetype: neo4j_auradb
    purpose: [description]
  causalmemory:
    storagetype: hypergraphdb
    purpose: [description]
  longtermpersistence:
    storagetype: s3_durable_archive
    retention: indefinite

communicationstack:
  input: [packetenvelope, structuredapi, messagesqueue]
  output: [packetenvelope, eventstream, governancereport]
  channels:
    packetenvelope: true
    structuredapi: true
    eventstream: true

reasoningengine:
  framework: multimodal_reflective
  model: gpt5_orchestrator
  strategymodes:
    - [strategy_1]
    - [strategy_2]
  temporalscope: rolling_180_days

collaborationnetwork:
  partners:
    - L9/agents/main
    - L9/core/tensoraios
  autonomyscope:
    internaldecisions: full
    externalactions: gated_by_governance

learningsystem:
  architecture: continuous_metalearning
  modules:
    - [learning_module_1]
  autonomyprofile:
    mode: controlled_autonomy
    tasklimit: 50_parallel
    decisionlatencymaxms: 1000

worldmodelintegration:
  activemodels:
    - [model_1]
  usecases:
    - [usecase_1]

cursorinstructions:
  createifmissing:
    - L9/agents/[name]
    - L9/tests/agents/[name]
  generatefiles:
    - controller.py
    - [module_1].py
    - __init__.py
  generatedocs:
    - README.md
    - CONFIG.md
    - API_SPEC.md
    - DEPLOYMENT.md
  postgeneration:
    manifest: L9/manifests/[name]/manifest.json
    validatedependencies: true
    generatetests: true

deployment:
  runtime: async_multinode
  environment: vpscluster_l9
  endpoints:
    - name: [endpoint_name]
      path: /[path]/v6/[method]
      method: [POST|GET]
      timeout_ms: 1000
  telemetry:
    dashboard: L9/monitoring/[name]_dashboard.py
    metrics:
      - [metric_1]
      - [metric_2]

metadata:
  author: L9 System Architect
  owner: Igor, L9 Executive
  versionhash: L9-[name]-v6.0.0
  generated: 2025-12-12
  status: production_ready
```

---

## FAQ & Troubleshooting

### Q: How do I add a new field to a schema?

**A:** Add it under the relevant section, then re-extract:

```yaml
# Edit your schema
learningsystem:
  new_field_name: new_value  # ← Add here

# Re-run extraction
python -c "extract(schema, extractor_map)"

# Generated code now includes new_field
```

### Q: What if extraction fails?

**A:** Check these in order:

1. **Syntax error?** `python -c "import yaml; yaml.safe_load(open('schema.yaml'))"`
2. **Missing required section?** Check against Quality_Gate_Checklist.md
3. **Type error?** Verify field values match expected types
4. **Dependency resolution?** Check glue layer wiring

### Q: How do I know if generated code is good?

**A:** Run quality gates:

```bash
pylint L9/agents/my_agent --min-score=8.0
mypy L9/agents/my_agent --strict
pytest L9/tests/agents/my_agent --cov=L9 --cov-report=term-missing
```

### Q: Can I modify generated code manually?

**A:** Not recommended (changes lost on re-extraction). Instead:

1. Change schema
2. Re-extract
3. Changes are tracked via schema diffs

### Q: How do I deploy to production?

**A:** Follow deployment checklist:

1. Validate schema against quality gates
2. Run integration tests (>95% pass rate)
3. Get governance approval (request goes to Igor, etc.)
4. Deploy to staging first (canary 5%)
5. Monitor metrics for 5 minutes
6. Promote to production

---

## Support & Resources

**In Spaces, ask Cursor:**
- "How do I create a schema for [domain]?"
- "What's the difference between working and episodic memory?"
- "How do I add custom governance rules?"
- "What's the Dora metric for this agent?"
- "How do I optimize extraction time?"

**Reference files:**
- QPF_System_Prompt.md (philosophy + structure)
- QPF_10Point_Guide.md (optimizations)
- Quality_Gate_Checklist.md (validation)
- Dora_Metrics_Compliance_Guide.md (metrics)

---

**Quantum Pipeline Factory v6.0 – Deterministic, AI-First Code Generation**

*Structure → Schema → Extraction → Code → Deploy*