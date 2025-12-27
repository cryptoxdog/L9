# STRATEGY MEMORY: L9 INTEGRATION CHECKLIST & PROTO SCHEMA

---

## ✅ IMPLEMENTATION CHECKLIST

### **Phase 1: Neo4j Schema & Retrieval (Week 1-2)**

- [ ] **Neo4j Schema Design**
  - [ ] Define Strategy node with all fields (id, embedding, graph_signature, score, tags)
  - [ ] Define Task node (order, type, agent_target, parameters)
  - [ ] Define Execution node (strategy_id, context, success, metrics)
  - [ ] Create relationship types: `:DECOMPOSES_INTO`, `:DEPENDS_ON`, `:EXECUTES_AS`
  - [ ] Add pgvector extension for embedding storage

- [ ] **Retrieval Service**
  - [ ] Implement embedding similarity query (cosine distance)
  - [ ] Implement graph edit distance via Neo4j GDS
  - [ ] Implement hybrid scoring function (40/40/20 split)
  - [ ] Add confidence threshold filtering (default: 0.6)
  - [ ] Add result ranking by performance_score + recency

- [ ] **Memory Substrate Integration**
  - [ ] Add StrategyRequest packet type
  - [ ] Add StrategyResponse packet type
  - [ ] Wire substrate_service.py to call Neo4j retrieval
  - [ ] Test semantic layer → embedding → Neo4j flow

- [ ] **Testing**
  - [ ] Unit test: hybrid similarity scoring
  - [ ] Integration test: task embedding → retrieved strategies
  - [ ] Benchmark: retrieval latency <100ms for 10k strategies

---

### **Phase 2: RAFA Adapter & Feedback Loop (Week 3-4)**

- [ ] **RAFA Adapter Interface**
  - [ ] Design adapter input/output Pydantic models
  - [ ] Implement precondition checking (symbolic pruning)
  - [ ] Implement parameter optimization (gradient-free)
  - [ ] Implement confidence estimation (graph edit distance metric)
  - [ ] Define adaptation_trace logging

- [ ] **Strategy Update Pipeline**
  - [ ] Implement performance_score update (exponential smoothing)
  - [ ] Implement generality_score tracking (adaptation success rate)
  - [ ] Implement tag management (success/failure patterns)
  - [ ] Implement strategy pruning logic (score < 0.3)
  - [ ] Add drift detection (failure_rate increase over time)

- [ ] **Packet Flow Integration**
  - [ ] Create StrategyFeedback packet type
  - [ ] Wire AgentExecutor → feedback service
  - [ ] Implement Neo4j update transaction
  - [ ] Add audit logging to policy_engine

- [ ] **Testing**
  - [ ] Unit test: adaptation scoring
  - [ ] Integration test: execution outcome → strategy update
  - [ ] Regression test: strategy scores improve with feedback

---

### **Phase 3: Agent Q & Learning (Week 5-6)**

- [ ] **Agent Q Integration**
  - [ ] Design strategy selection MDP (state=task_embedding, action=select_strategy_idx)
  - [ ] Implement Q-network forward pass (task_embedding → q_values)
  - [ ] Implement reward function (success + time_bonus + cost_penalty)
  - [ ] Implement TD learning update
  - [ ] Add epsilon-greedy exploration

- [ ] **Cross-Agent Learning**
  - [ ] Design experience sharing protocol (MARL)
  - [ ] Implement policy transfer for heterogeneous agents
  - [ ] Test Agent Q convergence on repeated task types

- [ ] **Testing**
  - [ ] Unit test: Q-learning update correctness
  - [ ] Integration test: Agent Q improves strategy selection over time
  - [ ] Convergence test: success_rate → 95%+ on seen task types

---

### **Phase 4: Robustness & Production (Week 7-8)**

- [ ] **Robustness Testing**
  - [ ] Implement perturbation test (Gaussian noise on embeddings)
  - [ ] Measure retrieval precision/recall under perturbation
  - [ ] Test strategy drift tracking (age-based decay)
  - [ ] Test self-repair (parameter re-optimization on failure)

- [ ] **A/B Testing**
  - [ ] Set up control group (de novo planning only)
  - [ ] Set up treatment group (hybrid: retrieve + adapt)
  - [ ] Run 100+ trials per group
  - [ ] Measure: execution_time, success_rate, resource_cost
  - [ ] Target: -20% time, no regression on success, -15% cost

- [ ] **Production Hardening**
  - [ ] Optimize Neo4j queries (add indexes on embedding, graph_signature)
  - [ ] Implement memory cleanup (prune old executions)
  - [ ] Add rate limiting to retrieval service
  - [ ] Add monitoring/alerting for memory bloat
  - [ ] Document operational procedures

- [ ] **Documentation**
  - [ ] Write API docs for retrieval service
  - [ ] Write troubleshooting guide for failed matches
  - [ ] Create schema migration scripts
  - [ ] Document strategy taxonomy (tags, types)

---

## 📐 NEO4J PROTO SCHEMA (Cypher)

```cypher
// ============================================================================
// STRATEGY MEMORY SCHEMA v1.0
// ============================================================================

// 1. CREATE CONSTRAINTS
CREATE CONSTRAINT strategy_id_unique IF NOT EXISTS
  FOR (s:Strategy) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT task_strategy_order IF NOT EXISTS
  FOR (t:Task) REQUIRE (t.strategy_id, t.order) IS UNIQUE;

CREATE CONSTRAINT execution_id_unique IF NOT EXISTS
  FOR (e:Execution) REQUIRE e.id IS UNIQUE;

// 2. CREATE INDEXES
CREATE INDEX strategy_score IF NOT EXISTS FOR (s:Strategy) ON (s.performance_score);
CREATE INDEX strategy_generality IF NOT EXISTS FOR (s:Strategy) ON (s.generality_score);
CREATE INDEX strategy_tags IF NOT EXISTS FOR (s:Strategy) ON (s.tags);
CREATE INDEX strategy_creation IF NOT EXISTS FOR (s:Strategy) ON (s.creation_datetime);
CREATE INDEX task_strategy IF NOT EXISTS FOR (t:Task) ON (t.strategy_id);
CREATE INDEX execution_strategy IF NOT EXISTS FOR (e:Execution) ON (e.strategy_id);

// 3. CORE NODES

// Strategy: Reusable plan decomposition
CREATE (s:Strategy {
  id: "str_001",
  name: "RetrieveAndExecuteStrategy",
  
  // Embeddings & matching
  context_embedding: [0.1, 0.2, ...],  // 384-dim pgvector
  graph_signature: "hash_abc123",  // SHA256(task DAG structure)
  
  // Performance tracking
  performance_score: 0.85,  // exponential smoothing, [0, 1]
  generality_score: 0.72,  // % of tasks it's been adapted to
  
  // Metadata
  creation_datetime: datetime("2025-12-19T08:30:00Z"),
  last_used: datetime("2025-12-19T08:45:00Z"),
  usage_count: 5,
  
  // Tags for semantic search
  tags: ["planning", "coordination", "fast_execution"],
  
  // Adaptation tracking
  adaptation_history: [
    {
      context_id: "ctx_042",
      success: true,
      time_delta_ms: 150,
      confidence_delta: -0.05
    },
    {context_id: "ctx_041", success: false, ...}
  ],
  
  // Metadata for self-repair
  failure_rate: 0.1,  // rolling window
  age_days: 2
})

// Task: Primitive action in strategy
CREATE (t:Task {
  id: "task_001",
  strategy_id: "str_001",
  order: 1,  // execution order
  
  type: "agent_action",  // enum: {agent_action, check, coordination}
  agent_target: "RAFA",  // which agent executes
  
  // Task definition
  name: "RetrieveStrategy",
  description: "Query strategy memory based on task embedding",
  
  // Execution parameters
  parameters: {
    retrieval_threshold: 0.6,
    max_results: 5,
    timeout_ms: 1000
  },
  
  // Dependency info (denormalized for performance)
  depends_on: ["task_000"],  // task IDs
  coordinates_with: []
})

// Execution: Record of a strategy's run
CREATE (e:Execution {
  id: "exec_001",
  strategy_id: "str_001",
  
  // Context
  task_context_embedding: [...],
  task_description: "Find and execute cached strategy for task X",
  
  // Outcome
  success: true,
  failure_reason: null,  // e.g., "precondition_failed", "timeout"
  
  // Metrics
  execution_time_ms: 245,
  resource_cost: 0.15,  // normalized CPU/memory
  feedback_score: 0.92,  // user-provided or inferred
  
  // Metadata
  executor_id: "agent_q_001",
  timestamp: datetime("2025-12-19T08:45:30Z"),
  
  // Adaptation details
  was_adapted: true,
  adaptation_distance: 2,  // graph edits
  adaptation_confidence: 0.78
})

// 4. RELATIONSHIPS

// Strategy decomposes into tasks
MATCH (s:Strategy {id: "str_001"}), (t:Task {id: "task_001"})
CREATE (s)-[:DECOMPOSES_INTO]->(t)

// Task depends on another task
MATCH (t1:Task {id: "task_001"}), (t2:Task {id: "task_000"})
CREATE (t1)-[:DEPENDS_ON]->(t2)

// Task coordinates with another
MATCH (t1:Task {id: "task_001"}), (t2:Task {id: "task_002"})
CREATE (t1)-[:COORDINATES_WITH]->(t2)

// Strategy was executed
MATCH (s:Strategy {id: "str_001"}), (e:Execution {id: "exec_001"})
CREATE (s)-[:EXECUTED_AS]->(e)

// Strategy lineage (derived from another via adaptation)
MATCH (s_new:Strategy {id: "str_002"}), (s_old:Strategy {id: "str_001"})
CREATE (s_new)-[:DERIVED_FROM {
  adaptation_method: "graph_edit",
  edit_distance: 2,
  timestamp: datetime("2025-12-19T08:40:00Z")
}]->(s_old)

// 5. QUERY EXAMPLES

// Retrieve strategies similar to current task
MATCH (s:Strategy)
WHERE vector_similarity(s.context_embedding, $current_embedding) > 0.75
ORDER BY s.performance_score DESC
LIMIT 5
RETURN s.id, s.name, s.performance_score

// Find strategies applicable to task type
MATCH (s:Strategy)
WHERE "planning" IN s.tags AND "fast_execution" IN s.tags
AND s.performance_score > 0.7
RETURN s.id, s.name

// Retrieve task decomposition for strategy
MATCH (s:Strategy {id: $strategy_id})
OPTIONAL MATCH (s)-[:DECOMPOSES_INTO]->(t:Task)
OPTIONAL MATCH (t)-[:DEPENDS_ON]->(t_dep:Task)
RETURN s, collect(t), collect(t_dep)
ORDER BY t.order

// Track execution history
MATCH (s:Strategy)-[:EXECUTED_AS]->(e:Execution)
WHERE s.id = $strategy_id
RETURN e.timestamp, e.success, e.execution_time_ms
ORDER BY e.timestamp DESC
LIMIT 100

// Monitor strategy drift
MATCH (s:Strategy)
WHERE s.performance_score < 0.5 AND s.age_days > 7
RETURN s.id, s.performance_score, s.age_days
// → Candidates for self-repair or archival

// Find strategy lineage (adaptation ancestry)
MATCH path = (s:Strategy)-[:DERIVED_FROM*0..5]->(ancestor:Strategy)
WHERE s.id = $strategy_id
RETURN nodes(path), relationships(path)
```

---

## 🔗 PACKET ENVELOPE EXTENSIONS

```python
# substrate_service.py additions

class StrategyRequestMetadata(BaseModel):
    packet_type: Literal["strategy_query"] = "strategy_query"
    sender: str  # e.g., "CEO Agent"
    task_embedding: List[float]  # 384-dim vector from semantic layer
    goal_description: str
    deadline_ms: int
    requested_confidence_threshold: float = 0.6
    max_results: int = 5

class StrategyRequestPayload(BaseModel):
    current_state: Dict[str, Any]
    task_context: Dict[str, Any]
    preferred_tags: Optional[List[str]] = None

class StrategyResponseMetadata(BaseModel):
    packet_type: Literal["strategy_response"] = "strategy_response"
    sender: str = "Memory Substrate"
    request_id: UUID
    retrieval_time_ms: float

class StrategyResponsePayload(BaseModel):
    matched_strategies: List[Dict]  # [{id, name, score, graph, ...}]
    confidence_scores: List[float]
    retrieval_status: Literal["success", "no_match", "error"]
    coplanner_input: Dict[str, Any]  # Pre-formatted for CoPlanner

class StrategyFeedbackMetadata(BaseModel):
    packet_type: Literal["strategy_execution_outcome"] = "strategy_execution_outcome"
    sender: str  # "Agent Executor"
    strategy_id: UUID
    execution_id: UUID

class StrategyFeedbackPayload(BaseModel):
    success: bool
    execution_time_ms: int
    resource_cost: float
    failure_reason: Optional[str]
    feedback_score: Optional[float] = None
    task_context_embedding: List[float]
    was_adapted: bool
    adaptation_distance: Optional[int]
```

---

## 🎯 SUCCESS METRICS (Q1 2026)

| Metric | Baseline (De Novo) | Target (Hybrid) | Unit |
|--------|-------------------|-----------------|------|
| Execution Time | 500 ms | <400 ms | ms |
| Success Rate | 92% | ≥92% | % |
| Resource Cost | 1.0 | <0.85 | normalized |
| Strategy Reuse Rate | 0% | >60% | % |
| Memory Hit Rate | N/A | >75% | % |
| Adaptation Success | N/A | >80% | % |
| Mean Retrieval Latency | N/A | <50 ms | ms |

---

## 🚨 FAILURE MODES & MITIGATION

| Failure Mode | Detection | Mitigation |
|-------------|-----------|-----------|
| **False positive match** | Execution fails after adaptation | Require confidence > 0.7; implement fallback to de novo |
| **Memory bloat** | Neo4j query time >500ms | Prune strategies with score < 0.3 monthly; archive to cold storage |
| **Embedding drift** | Retrieval precision drops over time | Retrain embedding model quarterly; implement semantic decay |
| **Cycle in task DAG** | Infinite loop during decomposition | Validate DAG on strategy creation; detect cycles in Neo4j |
| **Stale strategies** | Performance scores outdated | Implement age-based discount; re-evaluate old strategies under current conditions |
| **Policy overfitting** | Agent Q memorizes specific contexts | Add regularization to Q-loss; periodic policy reset; diversity bonus |

---

## 📋 SIGN-OFF

**Architect**: [Your Name]  
**Date**: 2025-12-19  
**Review Status**: Ready for implementation kickoff  
**Dependencies**:
- [ ] Neo4j cluster with pgvector extension running
- [ ] Semantic embedding layer in Memory Substrate stable
- [ ] RAFA Strategic Planner available for integration
- [ ] Agent Q executor ready for learning loop

**Next**: Spin up Phase 1 schema + create test dataset with 500+ synthetic strategies

