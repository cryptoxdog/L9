# STRATEGY MEMORY ARCHITECTURE: VISUAL REFERENCE & QUICK-START GUIDE

---

## 🏗️ SYSTEM ARCHITECTURE DIAGRAM

```
╔════════════════════════════════════════════════════════════════════════════╗
║                        L9 AUTONOMOUS AGENT SYSTEM                          ║
║                    Strategy Memory Enhancement (SMRT v1.0)                 ║
╚════════════════════════════════════════════════════════════════════════════╝

                          ┌─────────────────────┐
                          │   NEW TASK INPUT    │
                          │  (goal + context)   │
                          └──────────┬──────────┘
                                     │
                    ┌────────────────┴──────────────────┐
                    │                                   │
                    ▼                                   ▼
        ┌──────────────────────┐         ┌──────────────────────┐
        │   CEO AGENT          │         │  Semantic Embedding  │
        │  (Goal Classifier)   │         │  (Substrate Layer)   │
        │                      │         │                      │
        │  • Parse task        │         │  • Encode context    │
        │  • Infer intent      │         │  • Generate vector   │
        │  • Route to strategy │         │  • Cache embedding   │
        └──────┬───────────────┘         └──────┬───────────────┘
               │                                 │
               └─────────────────┬───────────────┘
                                 │
                 ┌───────────────▼──────────────┐
                 │  STRATEGY MATCHER (Neo4j)    │
                 │  ─────────────────────────   │
                 │  Hybrid Retrieval Engine      │
                 │                              │
                 │  • Embedding similarity      │
                 │    (pgvector cosine)         │
                 │  • Graph edit distance       │
                 │    (Neo4j GDS)               │
                 │  • Symbolic tag matching     │
                 │  • Confidence scoring        │
                 └────────────┬─────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
           Match Confidence >= 0.6       Match Not Found
              (Retrieve Top-5)               │
                    │                        │
                    ▼                        ▼
        ┌──────────────────────┐  ┌─────────────────────┐
        │  RAFA ADAPTER        │  │  De Novo Planning   │
        │  (Strategy Refiner)  │  │  (Traditional Path) │
        │                      │  │                     │
        │  • Check precond.    │  │  • RAFA from scratch│
        │  • Prune branches    │  │  • Full search      │
        │  • Optimize params   │  │  • Generate new     │
        │  • Estimate success  │  │    task network     │
        └──────────┬───────────┘  └────────────┬────────┘
                   │                           │
                   └────────────┬──────────────┘
                                │
                 ┌──────────────▼───────────────┐
                 │  COPLANNER ORCHESTRATOR      │
                 │  ──────────────────────      │
                 │  • Task sequencing            │
                 │  • Dependency resolution      │
                 │  • Parallel coordination      │
                 │  • Handle failures            │
                 └────────────┬────────────────┘
                              │
                 ┌────────────▼───────────────┐
                 │  AGENT EXECUTOR            │
                 │  ─────────────────────     │
                 │  • Execute primitives       │
                 │  • Monitor progress         │
                 │  • Collect signals          │
                 │  • Record outcomes          │
                 └────────────┬────────────────┘
                              │
                 ┌────────────▼────────────────┐
                 │  EXECUTION FEEDBACK         │
                 │  ──────────────────────     │
                 │  • success: bool            │
                 │  • time_ms: int             │
                 │  • resource_cost: float     │
                 │  • failure_reason: str      │
                 └────────────┬────────────────┘
                              │
                 ┌────────────▼──────────────┐
                 │  STRATEGY UPDATER         │
                 │  ───────────────────      │
                 │  • Update score           │
                 │  • Track generality       │
                 │  • Log adaptation         │
                 │  • Tag patterns           │
                 │  • Detect drift           │
                 └────────────┬──────────────┘
                              │
            ┌─────────────────┴──────────────────┐
            │                                    │
            ▼                                    ▼
    ┌─────────────────────┐        ┌──────────────────────┐
    │  NEO4J STORE        │        │   AGENT Q LEARNER    │
    │  ──────────────────│        │  ────────────────    │
    │  • Strategy nodes   │        │  • Select action     │
    │  • Task networks    │        │  • Update Q-value    │
    │  • Execution logs   │        │  • Improve matching  │
    │  • Lineage info     │        │  • Convergence test  │
    └─────────────────────┘        └──────────────────────┘
            ▲
            │
            └─── pgvector + GDS


╔════════════════════════════════════════════════════════════════════════════╗
║                       MEMORY SUBSTRATE INTEGRATION                          ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  PacketEnvelope[StrategyRequest]                                            ║
║  ├─ metadata.task_embedding ──▶ STRATEGY MATCHER                           ║
║  ├─ metadata.goal_description                                              ║
║  └─ payload.current_state                                                  ║
║                                    │                                        ║
║                                    ▼                                        ║
║                          PacketEnvelope[StrategyResponse]                   ║
║                          ├─ matched_strategies[]                           ║
║                          ├─ confidence_scores[]                            ║
║                          └─ coplanner_input{}                              ║
║                                                                              ║
║  PacketEnvelope[StrategyFeedback]                                           ║
║  ├─ strategy_id ────────────▶ STRATEGY UPDATER                             ║
║  ├─ execution_id             │                                             ║
║  └─ payload.outcome          ▼                                             ║
║                          Neo4j Update TX                                   ║
║                                                                              ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## 📊 COMPONENT INTERACTION MATRIX

| Component | Receives From | Sends To | Protocol | Latency SLA |
|-----------|--------------|----------|----------|-------------|
| **CEO Agent** | Task Input | Strategy Matcher | Native | <50 ms |
| **Semantic Layer** | CEO Agent | Strategy Matcher | Vector | <30 ms |
| **Strategy Matcher** | CEO + Embedding | RAFA or De Novo | Ranked List | <100 ms |
| **RAFA Adapter** | Strategy Matcher | CoPlanner | Adapted Graph | <200 ms |
| **CoPlanner** | RAFA or De Novo | Agent Executor | Task Network | <50 ms |
| **Agent Executor** | CoPlanner | Strategy Updater | Outcome Dict | <5 ms (async) |
| **Strategy Updater** | Agent Executor | Neo4j | Transaction | <200 ms |
| **Agent Q** | Strategy Updater | Strategy Matcher (indirect) | Q-weights | <500 ms |

---

## 🔑 KEY DATA STRUCTURES

### **Strategy Node (Neo4j)**
```
{
  id: UUID,
  name: String,
  context_embedding: Vector[384],      # pgvector
  graph_signature: String,              # Hash of task DAG
  performance_score: Float [0-1],       # Exponential moving average
  generality_score: Float [0-1],        # % of tasks adapted successfully
  creation_datetime: DateTime,
  last_used: DateTime,
  usage_count: Int,
  tags: [String],                       # e.g., ["planning", "fast"]
  adaptation_history: [
    {
      context_id: String,
      success: Bool,
      time_delta_ms: Int,
      confidence_delta: Float
    }
  ],
  failure_rate: Float [0-1],
  age_days: Int
}
```

### **Task Node (Neo4j)**
```
{
  id: UUID,
  strategy_id: UUID,
  order: Int,                           # Execution order
  type: Enum ["agent_action", "check", "coordination"],
  agent_target: String,                 # e.g., "RAFA", "CoPlanner"
  name: String,
  description: String,
  parameters: {                         # Task-specific config
    key: value, ...
  },
  depends_on: [UUID],                   # Task IDs (denormalized)
  coordinates_with: [UUID]
}
```

### **Execution Node (Neo4j)**
```
{
  id: UUID,
  strategy_id: UUID,
  task_context_embedding: Vector[384],
  task_description: String,
  success: Bool,
  failure_reason: String | Null,
  execution_time_ms: Int,
  resource_cost: Float,
  feedback_score: Float [0-1],
  executor_id: String,
  timestamp: DateTime,
  was_adapted: Bool,
  adaptation_distance: Int | Null,
  adaptation_confidence: Float | Null
}
```

---

## 🎯 QUICK-START: 4-PHASE TIMELINE

```
WEEK 1-2: FOUNDATION
├─ Create Neo4j schema (Strategy, Task, Execution nodes)
├─ Implement retrieval service (3-signal hybrid scoring)
├─ Wire to Memory Substrate (StrategyRequest/Response packets)
└─ Benchmark: retrieval latency <100ms, precision >85%

WEEK 3-4: ADAPTATION & FEEDBACK
├─ Build RAFA adapter (precondition → pruning → confidence)
├─ Implement strategy update pipeline (score + generality tracking)
├─ Wire feedback loop (outcome → Neo4j transaction)
└─ Test: adaptation success >80%, no regression on success_rate

WEEK 5-6: LEARNING & INTEGRATION
├─ Design Agent Q selector (task_embedding → strategy index)
├─ Implement Q-learning update (reward = success + time_bonus + cost_penalty)
├─ Test convergence on repeated task types
└─ Benchmark: Agent Q improves match quality over 100 episodes

WEEK 7-8: HARDENING & VALIDATION
├─ A/B test (hybrid vs. de novo planning)
├─ Robustness testing (perturbation, drift detection, self-repair)
├─ Production optimization (indexing, cleanup, monitoring)
└─ Target metrics: -20% execution time, no success regression, -15% cost
```

---

## 📈 PERFORMANCE TARGETS (Post-Launch)

### **Retrieval Performance**
- **Latency P50**: <50 ms (single query)
- **Latency P99**: <150 ms
- **Throughput**: 1000 queries/sec
- **Precision** (confidence > 0.6): >85%
- **Recall** (true matches): >90%

### **Strategy Effectiveness**
- **Reuse Rate**: >60% of tasks (vs. 0% baseline)
- **Performance Delta**: -20% execution time vs. de novo
- **Success Rate**: ≥92% (no regression)
- **Resource Cost**: -15% vs. de novo

### **Adaptation Quality**
- **Adaptation Success**: >80% of adapted strategies succeed
- **Confidence Calibration**: Expected success ≈ reported confidence
- **Generality**: Avg. strategy used on 3-5 different task variants

### **Memory Health**
- **Strategy Library Size**: 5,000-10,000 active strategies
- **Avg. Strategy Age**: <30 days (old strategies pruned)
- **Memory Bloat Risk**: <5% failure due to noise accumulation
- **Neo4j Cluster Health**: 99.9% uptime

---

## 🚦 DEPLOYMENT CHECKLIST

**Pre-Launch**
- [ ] Schema deployed and indexed
- [ ] Retrieval service at <100ms latency
- [ ] Adapter confidence estimation validated
- [ ] Feedback loop idempotent + auditable
- [ ] A/B test framework ready
- [ ] Monitoring/alerting configured

**Launch (Canary 5%)**
- [ ] Run 48h on 5% of traffic
- [ ] Monitor latencies, error rates, quality metrics
- [ ] Validate Neo4j performance under load

**Ramp (50% → 100%)**
- [ ] Gradual traffic increase
- [ ] Validate each 10% increment
- [ ] Watch for memory bloat, query plan changes
- [ ] Monitor Agent Q convergence

**Post-Launch (Weeks 1-4)**
- [ ] Weekly strategy pruning (score < 0.3 → archive)
- [ ] Monthly strategy re-evaluation (age-based)
- [ ] Quarterly embedding model refresh
- [ ] Monthly cost analysis (compute vs. savings)

---

## 🛠️ OPERATIONAL PROCEDURES

### **Diagnosing Low Retrieval Precision**
```
Symptom: Matched strategies fail during execution
│
├─ Check 1: Retrieval confidence scores
│  └─ If mostly >0.7: adapter failing (not retrieval)
│  └─ If mostly <0.6: reduce threshold or retrain embeddings
│
├─ Check 2: False positives in top-5
│  └─ Run perturbation test
│  └─ Compare embedding vs. graph similarity
│  └─ Consider increasing graph_edit_distance weight (0.4 → 0.5)
│
└─ Check 3: Strategy cache staleness
   └─ Query: SELECT avg(age_days) FROM Strategy
   └─ If >60 days: trigger batch re-evaluation
```

### **Handling Strategy Drift**
```
Symptom: Strategy performance declines over time
│
├─ Automatic Detection
│  └─ Query: SELECT * FROM Strategy WHERE failure_rate > 0.2
│
├─ Response Options
│  ├─ Option A: Self-repair
│  │  └─ RAFA re-optimizes parameters under current conditions
│  │  └─ Re-evaluate on 10 random task contexts
│  │  └─ If success_rate recovers: keep; else → archive
│  │
│  └─ Option B: Archive
│     └─ Move to cold storage (monthly batch)
│     └─ Can resurrect if environment changes back
│
└─ Root Cause Analysis
   └─ Was there a system update? (CoPlanner, Agent Executor changes)
   └─ Did task distribution shift? (new task types emerged)
   └─ Is embedding model outdated? (retrain if N strategies affected)
```

### **Memory Cleanup (Monthly)**
```sql
-- Prune low-scoring strategies
MATCH (s:Strategy)
WHERE s.performance_score < 0.3 AND s.age_days > 30
DETACH DELETE s;

-- Archive old executions (keep recent 1000 per strategy)
MATCH (s:Strategy)-[rel:EXECUTED_AS]->(e:Execution)
WHERE e.timestamp < now() - duration({days: 90})
DELETE rel, e;

-- Recompute derived metrics
MATCH (s:Strategy)-[:EXECUTED_AS]->(e:Execution)
WITH s, count(e) as recent_count, avg(e.success) as success_rate
SET s.usage_count = recent_count,
    s.generality_score = success_rate;
```

---

## 🔗 INTEGRATION POINTS CHECKLIST

| System | Integration Type | Status |
|--------|-----------------|--------|
| **CEO Agent** | Task classifier output | Ready |
| **Semantic Layer** | Embedding generation | Ready |
| **RAFA Planner** | Adapter interface | In design |
| **CoPlanner** | Task network input | Awaiting schema |
| **Agent Executor** | Feedback sink | In design |
| **Agent Q** | Learning signal | Pending policy design |
| **Policy Engine** | Side-effect approval | Update YAML |
| **Memory Substrate** | Packet types | Design stage |
| **Neo4j Cluster** | Storage backend | Verified |
| **Monitoring/Alerting** | Metrics collection | TBD |

---

## 📚 REFERENCE DOCUMENTS

| Document | Purpose | Location |
|----------|---------|----------|
| **strategy_memory_research_map.md** | Full research synthesis | artifact_id: 56 |
| **strategy_memory_checklist.md** | Implementation checklist | artifact_id: 57 |
| **L9_RUNTIME_SSOT.md** | Runtime architecture | Space files |
| **L9_CONTEXT_PACK.md** | Canonical schemas | Space files |
| **L9_OPERATIONAL-WIRING-MAP.md** | Module spec workflow | Space files |

---

**Version:** 1.0.0  
**Date:** 2025-12-19  
**Status:** ✅ Ready for Implementation Kickoff  
**Next:** Spinning up Neo4j schema + test data generation
