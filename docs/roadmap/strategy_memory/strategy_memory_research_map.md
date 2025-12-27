# STRATEGY MEMORY FOR REPEAT TASK OPTIMIZATION
## Research Synthesis & L9 Integration Map

---

## 📊 RANKED RESEARCH SOURCES

### **TIER 1: DIRECT IMPLEMENTATION VALUE (9-10)**

---

#### **1. Case-Based Reasoning for LLM Agents** ⭐
**Source:** Hatalis et al., 2025 | Review of Case-Based Reasoning for LLM Agents
**Integration Score:** 10/10

**Key Concepts:**
- **CBR Cycle:** Retrieve → Adapt → Apply → Learn (5R cycle)
- **For LLM agents:** Solves structural knowledge gaps, hallucination mitigation, contextual memory
- **Multi-dimensional retrieval:** Similarity matching on problem features, prior solutions, outcome traces
- **Cognitive dimensions:** Self-reflection, introspection, curiosity-driven autonomy via goal-driven mechanisms

**Applicable Code/Math:**
```python
# CBR case structure for L9 strategy memory
Case = Tuple[ProblemDescription, ContextEmbedding, SolutionStrategy, OutcomeScore]

# Similarity function (hybrid: symbolic + embedding)
similarity(case_past, task_current) = 
    α * embedding_similarity(case_past.context, task_current.context) +
    β * symbolic_match(case_past.features, task_current.features) +
    γ * outcome_relevance(case_past.score, task_current.goal)

# Adaptation: RAFA planner modifies retrieved case
adapted_strategy = rafa.refine(retrieved_case.solution, new_context)
```

**Suggested Use in L9:**
- **Primary engine** for Strategy Matcher (CEO → Strategy Search)
- Store cases in Neo4j as `Strategy(id, context_embedding, graph_signature, performance_score, last_used)`
- Leverage RAFA Strategic Planner for case adaptation (not just direct replay)
- Pair with self-reflection loop: outcomes feed back into case quality scores

---

#### **2. Episodic Control & Policy Reuse** ⭐
**Source:** Blundell et al. 2016 (Episodic Control for RL); Fernández & Veloso 2006 (Policy Reuse)
**Integration Score:** 9/10

**Key Concepts:**
- **Episodic memory:** Non-parametric storage of past experiences (state, action, return)
- **Fast reuse:** Retrieve past trajectories; apply directly or as initialization (no backprop needed)
- **Policy Library:** Basis library of core strategies, incrementally built; new tasks select/adapt from library
- **Successor Features:** Reuse policies across tasks with different reward functions via feature decomposition

**Applicable Code/Math:**
```python
# Episodic MC-return retrieval
retrieved_state_action = episodic_memory.nearest_neighbor(current_state)
mc_return_past = sum(discounted_rewards(retrieved_state_action.trajectory))

# Hybrid critic update: blend MC-return with TD
critic_loss = MSE(V_critic(state), alpha * mc_return_past + (1-alpha) * td_target)

# Policy Library selection via Bayesian belief
P(task_type | observed_trajectory) ∝ P(obs | task) * P(task)
selected_policy = argmax_policy likelihood(policy, observations)
```

**Suggested Use in L9:**
- **Strategy Capture:** Store trajectories as episodic traces in PacketEnvelope
- **Episodic MC-return:** Use observed_reward + trajectory_return as performance signal for strategy_score
- **CoPlanner integration:** CoPlanner reads episodic returns to initialize sub-task sequencing
- **Agent Q:** Learn which strategies (from library) apply to which task signatures

---

#### **3. Hierarchical Task Networks (HTN) Planning** ⭐
**Source:** Erol et al. 1994 (UMCP); HATP (Geib); HDDL 2.1 (Temporal HTN)
**Integration Score:** 9/10

**Key Concepts:**
- **Task decomposition:** Recursively break compound tasks into primitives via domain methods
- **Method library:** Reusable decomposition rules; task encodes high-level intent, methods encode "how-to"
- **Partially ordered task networks:** DAG structure; dependencies explicit
- **Semantic attachments:** Procedural logic (e.g., check feasibility with simulator) embedded in decomposition

**Applicable Code/Math:**
```python
# HTN method definition
Method = NamedTuple(
    abstract_task: TaskName,
    precondition: Fluent,  # state guard
    subtask_network: PartiallyOrderedSet[Task]
)

# Example: "ExecuteStrategy(goal, context)" decomposes to
method_1 = Method(
    abstract_task="ExecuteStrategy",
    precondition=lambda s: s.similarity_match > 0.7,
    subtask_network=[(RetrieveStrategy, Adapt, Execute, Feedback)]
)

# Decomposition search
def decompose(task, state):
    applicable_methods = [m for m in methods if m.precondition(state)]
    for method in applicable_methods:
        # Recursively decompose subtasks
        primitive_plan = decompose_all(method.subtask_network, state)
        return primitive_plan
```

**Suggested Use in L9:**
- **Strategy Graph as HTN library:** Each stored strategy = method that decomposes goal into agent actions
- **RAFA Planner = HTN Decomposer:** Treat strategy adaptation as method refinement/selection
- **Neo4j stores:** Hierarchical task networks as decomposition chains; edges = dependencies
- **CEO Agent:** Top-level task selector (which strategy/method matches current goal?)

---

#### **4. Graph-Based Memory for Agents** ⭐
**Source:** ApX ML (2025); FalkorDB AI Agents Memory; Knowledge Graph Reasoning (Sparkco 2025)
**Integration Score:** 9/10

**Key Concepts:**
- **Explicit graph representation:** Nodes = states/plans/concepts; edges = transitions/dependencies/relationships
- **Dynamic construction:** Graphs updated as agent reasons/acts/observes
- **Multi-layer graphs:** Planning graphs (DAG of tasks), state-space graphs, knowledge graphs (entities + relations)
- **Traversal algorithms:** BFS/DFS for exploration; centrality for importance; community detection for clustering

**Applicable Code/Math:**
```python
# Neo4j schema for strategy memory
CREATE (s:Strategy {
    id: UUID,
    context_embedding: Vector[384],  // pgvector
    graph_signature: String,  // hash of task DAG
    performance_score: Float,
    last_used: DateTime,
    tags: List[String]
})

// Task DAG as subgraph
CREATE (s)-[:DECOMPOSES_TO]->(subtask:Task)
CREATE (subtask)-[:DEPENDS_ON]->(prerequisite:Task)

// Retrieval query: similarity + graph matching
MATCH (strategy:Strategy)
WHERE 
    vector_similarity(strategy.context_embedding, @current_context) > 0.75 AND
    graph_edit_distance(strategy.graph_signature, @current_goal_graph) < 2
RETURN strategy ORDER BY performance_score DESC LIMIT 5
```

**Suggested Use in L9:**
- **Primary storage layer:** Neo4j already in L9; extend schema for strategy graphs
- **Semantic search:** Combine embedding-based + graph-based matching for retrieval
- **Reasoning support:** Use graph centrality to identify critical task dependencies
- **Memory Substrate integration:** Strategies stored as PacketEnvelope with graph metadata

---

### **TIER 2: COMPLEMENTARY MECHANISMS (7-8)**

---

#### **5. Episodic Policy Gradient Training (EPGT)** 
**Source:** Le et al. (Episodic Policy Gradient Training)
**Integration Score:** 8/10

**Key Concepts:**
- **Hyperparameter optimization via episodic memory:** Reuse hyperparameter settings that worked for past training states
- **Non-parametric, fast adaptation:** Select learning rate, entropy coefficient based on past "similar" optimum
- **Training context awareness:** Recognize when learning hits a local optimum and apply prior-learned hyperparameters

**Suggested Use in L9:**
- **Agent Q optimization:** Learn which strategy adaptation parameters (RAFA pruning depth, edit distance threshold) work for which task classes
- **Feedback loop:** Track strategy adaptation quality; adjust agent's strategy-selection heuristics
- **Noise resilience:** Use EPGT to tune strategy matching tolerance under perturbation

---

#### **6. Successor Feature Neural Episodic Control (SFNEC)**
**Source:** Novati et al. 2021; Temporally Extended SFNEC 2024
**Integration Score:** 8/10

**Key Concepts:**
- **Successor features:** Decompose policy into basis features + learned weights per task
- **Flexible transfer:** Reuse basis across different reward structures
- **Episodic + feature learning:** Combine fast episodic lookup with slow generalization

**Suggested Use in L9:**
- **Strategy basis library:** Learn core "features" (e.g., "retrieve", "adapt", "execute", "feedback")
- **Cross-task reuse:** Different goals weight these features differently; reuse feature weights
- **Agent Q learning:** Learn task → feature weights mapping

---

#### **7. Learning from Demonstration (LfD) with Trajectory Priors**
**Source:** Learning Generalizable Robot Skills (Levine et al.); Learn2Decompose (Rana et al. 2024)
**Integration Score:** 7/10

**Key Concepts:**
- **Trajectory prior:** Learn probability distribution over successful motions from demos
- **Importance weighting:** Down-weight demo segments influenced by obstacles (avoid encoding spurious constraints)
- **Problem decomposition:** Learn from multi-step demos; extract sub-task structure

**Suggested Use in L9:**
- **Strategy capture from logs:** Analyze past successful agent runs; extract task decompositions
- **Robustness:** Weight recent/high-confidence strategies higher; discount noisy execution traces
- **Learn2Decompose pattern:** Given complex goal + demo of solution, extract reusable subtask structure

---

### **TIER 3: VALIDATION & SAFETY (6-7)**

---

#### **8. Perturbation Testing & Robustness**
**Source:** Multiple episodic control papers (2024-2025)
**Integration Score:** 6/10

**Key Concepts:**
- **Perturbation sensitivity:** Add noise to task embedding; verify strategy still works
- **False positive detection:** Ensure retrieved strategy is genuinely applicable (not spurious match)

**Suggested Use in L9:**
- **Memory hit rate validation:** Test retrieval under task variations; measure precision/recall
- **Strategy drift tracking:** Monitor if reused strategies degrade over time; trigger self-repair

---

#### **9. Multi-Agent Policy Transfer & Scaling**
**Source:** Knowledge Reuse in MARL (2022); Selective Policy Transfer (2024)
**Integration Score:** 7/10 (secondary)

**Key Concepts:**
- **Experience sharing:** Agents share learned experiences to accelerate convergence
- **Policy transferring:** New agent inherits best policy from team, then refines

**Suggested Use in L9:**
- **CoPlanner coordination:** Share strategy insights across agent instances
- **Scaling to heterogeneous agents:** Transfer strategies between L9 instances with different roles

---

## 🏗️ INTEGRATION ARCHITECTURE

### **Signal Flow Diagram (Refined)**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           NEW TASK INPUT                                 │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │   CEO AGENT        │
                    │ (Task Classifier)  │
                    └────────┬───────────┘
                             │
                             ▼
          ┌──────────────────────────────────────────┐
          │  STRATEGY MATCHER (Neo4j + Embeddings)   │
          │  ─────────────────────────────────────   │
          │  1. Embedding similarity (pgvector)      │
          │  2. Graph edit distance (HTN matching)   │
          │  3. Symbolic feature match               │
          │  4. Outcome relevance score              │
          └──────────────────┬───────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
            ▼                                 ▼
    ┌───────────────────┐         ┌──────────────────────┐
    │  NO MATCH         │         │ MATCH FOUND (Top-5)  │
    │  ─────────────    │         │ ──────────────────── │
    │  De novo planning │         │ Retrieved strategies │
    │  (traditional)    │         │ with confidence      │
    └────────┬──────────┘         └──────────┬───────────┘
             │                               │
             │                   ┌───────────▼──────────────┐
             │                   │  RAFA ADAPTER            │
             │                   │  ──────────────────      │
             │                   │  • Edit graph signature  │
             │                   │  • Prune task branches   │
             │                   │  • Re-parameterize       │
             │                   │  • Estimate adaptation   │
             │                   │    success probability   │
             │                   └───────────┬──────────────┘
             │                               │
             └───────────────┬───────────────┘
                             │
                             ▼
                ┌────────────────────────────┐
                │  COPLANNER ORCHESTRATOR    │
                │  ──────────────────────    │
                │  • Sub-task sequencing     │
                │  • Dependency resolution   │
                │  • Parallel coordination   │
                └────────────┬───────────────┘
                             │
                             ▼
                ┌────────────────────────────┐
                │  AGENT EXECUTION CHAIN     │
                │  ──────────────────────    │
                │  • Execute primitive tasks │
                │  • Collect outcomes        │
                │  • Monitor performance     │
                └────────────┬───────────────┘
                             │
                             ▼
            ┌────────────────────────────────────┐
            │  STRATEGY UPDATER & FEEDBACK       │
            │  ──────────────────────────────    │
            │  1. Compute performance delta      │
            │  2. Update strategy score          │
            │  3. Tag successes/failures         │
            │  4. Learn adaptation parameters   │
            └────────────┬─────────────────────┘
                         │
                         ▼
            ┌────────────────────────────────────┐
            │  NEO4J STRATEGY STORE               │
            │  ────────────────────────────      │
            │  Update: performance_score         │
            │          last_used, tags,          │
            │          adaptation_log            │
            └────────────────────────────────────┘
```

---

## 🔧 IMPLEMENTATION SPEC

### **Component: Strategy Memory Layer**

#### **1. Neo4j Schema**
```cypher
// Core strategy node
CREATE (s:Strategy {
    id: UUID,
    name: String,
    context_embedding: Vector[384],  // from Substrate semantic layer
    graph_signature: String,  // hash of task decomposition DAG
    performance_score: Float,  // 0-1, exponential smoothing
    generality_score: Float,  // tasks_adapted / max_possible
    last_used: DateTime,
    creation_datetime: DateTime,
    adaptation_history: [Map],  // [{context, success, delta_time}]
    tags: [String]  // e.g. ["planning", "coordination", "error_recovery"]
})

// Task hierarchy
CREATE (s)-[:DECOMPOSES_INTO]->(t:Task {
    order: Int,
    task_type: String,  // e.g. "agent_action", "check", "coordination"
    agent_target: String,  // which agent (e.g. AgentQ, RAFA)
    parameters: Map
})

// Dependency edges
CREATE (t1)-[:DEPENDS_ON]->(t2)
CREATE (t1)-[:COORDINATES_WITH]->(t2)

// Outcome tracking
CREATE (exec:Execution {
    strategy_id: UUID,
    task_context: Vector[384],
    success: Boolean,
    time_elapsed: Int,
    resource_cost: Float,
    feedback_score: Float
})
CREATE (s)-[:EXECUTED_AS]->(exec)

// Strategy similarity/lineage
CREATE (s1)-[:DERIVED_FROM {
    adaptation_method: String,  // "graph_edit", "feature_reweight", "etc"
    edit_distance: Int
}]->(s2)
```

#### **2. Retrieval Algorithm**

**Input:** `current_task_embedding`, `current_goal_graph_signature`, `task_deadline_seconds`

**Output:** `Top-K strategies` with confidence scores

```python
def retrieve_strategies(task_embedding, goal_graph, k=5, threshold=0.6):
    # Parallel queries
    q1 = embedding_similarity(task_embedding)  # pgvector cosine
    q2 = graph_edit_distance(goal_graph)  # Neo4j GDS
    q3 = symbolic_tag_match(task_type)  # full-text search
    
    # Hybrid score
    results = []
    for strategy in (q1 ∪ q2 ∪ q3):
        score = (
            0.4 * normalize(embedding_sim) +
            0.4 * (1 / (1 + graph_distance)) +
            0.2 * tag_relevance
        )
        if score > threshold:
            results.append((strategy, score))
    
    # Rank by performance & recency
    results.sort(key=lambda x: (
        x.strategy.performance_score * exponential_decay(x.strategy.last_used),
        -x.score  # confidence secondary
    ))
    
    return results[:k]
```

#### **3. RAFA Adaptation Interface**

```python
# RAFA receives retrieved strategy graph + current context
def adapt_strategy(
    strategy_graph: HTNGraph,
    current_context: Dict,
    adaptation_budget: float = 0.3  # allowed deviation from original
) -> AdaptedStrategy:
    
    # 1. Symbolic pruning: remove inapplicable branches
    for task in strategy_graph.tasks:
        if not check_precondition(task.precondition, current_context):
            strategy_graph.remove_subtree(task)
    
    # 2. Parameter re-optimization
    adapted_params = optimize_parameters(
        strategy_graph,
        current_context,
        budget=adaptation_budget
    )
    
    # 3. Estimate success probability
    success_prob = estimate_adaptation_quality(
        original_graph=original_strategy.graph,
        adapted_graph=strategy_graph,
        adaptation_steps=len(changes)
    )
    
    return AdaptedStrategy(
        graph=strategy_graph,
        parameters=adapted_params,
        confidence=success_prob,
        adaptation_trace=changes
    )
```

#### **4. Agent Q Integration**

```python
# Agent Q learns: task_context → select_best_strategy_idx
class StrategySelector(AgentQ):
    def forward(self, task_embedding: Tensor) -> Tensor:
        # DQN-style Q-learning
        # State: task_embedding + current_state
        # Action: select from Top-K retrieved strategies
        # Reward: task_success + (-time_delta) + (-resource_cost)
        q_values = self.q_network(task_embedding)
        return q_values
    
    def learn_from_execution(self, strategy_id, outcome):
        reward = compute_reward(outcome)
        td_target = reward + gamma * max(q_next)
        loss = mse(q_value, td_target)
        self.optimizer.step(loss)
```

#### **5. Feedback Loop: Strategy Update**

```python
def update_strategy_after_execution(
    strategy_id: UUID,
    outcome: ExecutionOutcome,
    execution_time: int
):
    strategy = neo4j.get(Strategy, id=strategy_id)
    
    # Exponential smoothing for performance
    success_signal = 1.0 if outcome.success else 0.0
    strategy.performance_score = (
        0.7 * strategy.performance_score +
        0.3 * success_signal
    )
    
    # Track adaptation success rate
    if strategy.adaptation_history:
        adaptation_success_rate = count_successes(
            strategy.adaptation_history
        ) / len(strategy.adaptation_history)
        strategy.generality_score = adaptation_success_rate
    
    # Tag emerging patterns
    if outcome.success and execution_time < baseline_time:
        strategy.tags.append("fast_execution")
    if outcome.failure_reason:
        strategy.tags.append(f"fails_on_{outcome.failure_reason}")
    
    neo4j.save(strategy)
```

---

## 📋 EVALUATION PROTOCOL

### **Metrics Implementation**

| Metric | Formula | Neo4j Query |
|--------|---------|------------|
| **Strategy Reuse Rate** | (tasks_with_match / total_tasks) × 100 | `MATCH (e:Execution)-[:USED]->(s:Strategy) WHERE e.success RETURN count(distinct s) / count(e)` |
| **Performance Delta** | (time_reuse - time_novo) / time_novo | Compare execution times: matched vs. de novo paths |
| **Adaptation Success** | (adapted_strategies_succeed / adapted_strategies_attempted) | `MATCH (s:Strategy)-[:ADAPTED_TO]->(exec:Execution) RETURN sum(exec.success) / count(exec)` |
| **Strategy Generality** | distinct_task_types / max_possible | Count unique task contexts that matched strategy |
| **Memory Hit Rate** | (matches_with_confidence > 0.6) / retrieval_attempts | `MATCH (e:Execution)-[:RETRIEVED]->(s:Strategy) RETURN count(*) WHERE s.score > 0.6 / count(e)` |

### **A/B Testing Protocol**

```
Experiment: Reused vs. De Novo Strategy Selection

Control Group:
- CEO Agent: always de novo planning (RAFA from scratch)
- Metric: execution_time, success_rate, resource_cost

Treatment Group:
- CEO Agent: hybrid (retrieve + adapt if confidence > 0.7, else de novo)
- Metric: same as control

Success Criteria:
- treatment.execution_time < control.execution_time (target: -20%)
- treatment.success_rate >= control.success_rate (no regression)
- treatment.resource_cost < control (target: -15%)
```

### **Robustness: Perturbation Testing**

```python
def perturbation_test(strategy_id, perturbation_sigma=0.15):
    """
    Add Gaussian noise to task embedding;
    verify strategy still matches
    """
    strategy = neo4j.get(Strategy, id=strategy_id)
    
    for trial in range(100):
        noisy_embedding = strategy.context_embedding + np.random.normal(
            0, perturbation_sigma, size=embedding_dim
        )
        
        retrieved = retrieve_strategies(noisy_embedding, k=5)
        
        if strategy in retrieved:
            precision += 1
        else:
            miss += 1
    
    return precision / 100, (100 - miss) / 100
```

---

## ⚠️ MITIGATION STRATEGIES

| Challenge | Root Cause | Mitigation |
|-----------|-----------|-----------|
| **Overfitting to past solutions** | Strategy heavily tuned to old context | Diversity penalty: reduce score if used >N times in similar context; periodic refresh heuristics |
| **Partial strategy applicability** | Retrieved strategy only ~60% relevant | Allow RAFA pruning depth control; set confidence threshold; fall back to de novo if confidence < 0.5 |
| **Memory bloat** | Strategy library grows unbounded | Prune strategies with performance_score < 0.3; cluster similar strategies; compress task DAGs |
| **Retrieval imprecision** | Embedding-only matching misses context | Hybrid matching: combine 3 signals (embedding + graph + symbolic); enforce minimum confidence threshold |
| **Strategy drift over time** | Reused strategies degrade as environment changes | Track failure_rate by age; implement self-repair: re-optimize parameters if failure_rate > threshold; archive old strategies |

---

## 🔌 L9 WIRING

### **Packet Flow: Memory Substrate Integration**

```
PacketEnvelope[StrategyRequest]:
  metadata:
    packet_type: "strategy_query"
    sender: "CEO Agent"
    task_embedding: Vector[384]  // from Substrate semantic layer
    goal_description: String
    deadline_ms: Int
  
  payload:
    current_state: AgentStateVector
    task_context: Dict

  ──▶ Memory Substrate Service ──▶ Neo4j Strategy Retrieval
                                  ──▶ PacketEnvelope[StrategyResponse]
                                      {
                                        matched_strategies: [Strategy],
                                        confidence_scores: [Float],
                                        recommendations: CoPlanner input
                                      }

PacketEnvelope[StrategyFeedback]:
  metadata:
    packet_type: "strategy_execution_outcome"
    sender: "Agent Executor"
    strategy_id: UUID
    success: Boolean
    metrics: {execution_time, resource_cost, ...}
  
  ──▶ Strategy Updater ──▶ Neo4j Update
```

### **Governance Policy Integration**

```yaml
# policy_engine.yml additions
policies:
  strategy_memory:
    - action: "retrieve_from_strategy_store"
      effect: "read_only"
      approval_required: false
      audit_log: true
    
    - action: "execute_adapted_strategy"
      effect: "side_effect"
      approval_required: if confidence < 0.6
      constraints:
        - max_adaptation_distance: 3  # graph edits
        - min_confidence: 0.5
        - timeout_ms: 5000
```

---

## 📝 IMPLEMENTATION ROADMAP

**Phase 1 (Weeks 1-2):** Neo4j schema + retrieval service
**Phase 2 (Weeks 3-4):** RAFA adapter interface; feedback loop
**Phase 3 (Weeks 5-6):** Agent Q integration; A/B testing
**Phase 4 (Weeks 7-8):** Robustness testing; production optimization

---

## 🎓 KEY TAKEAWAYS

1. **CBR + HTN = Dual-Layer Matching:** Use embeddings (fast, semantic) + graph edit distance (precise, structural)
2. **RAFA is Adapter, Not Just Retriever:** Strategy reuse's power comes from intelligent adaptation, not blind replay
3. **Neo4j is Natural Fit:** Graph structure encodes task dependencies; pgvector enables semantic search; GDS provides edit distance
4. **Agent Q Learns the Meta-Problem:** Not "which action next?" but "which past strategy applies here?"
5. **Feedback Loop is Critical:** Performance scores must decay; adaptation success must be tracked; strategies must self-repair
6. **Measure Early:** A/B test against de novo planning; track memory hit rate, adaptation success, generality score
7. **Bounded Adaptation:** Allow RAFA pruning/refinement but enforce confidence threshold; fall back to de novo if uncertain

---

## 🔗 CROSS-REFERENCE MAP

| L9 Component | Research Connection | Artifact |
|-------------|-------------------|----------|
| CEO Agent | CBR task classification | Hatalis et al. 2025 |
| Strategy Matcher | Embedding + Graph matching | ApX ML; FalkorDB |
| RAFA Planner | HTN decomposition + adaptation | Erol 1994; HATP; Learn2Decompose |
| CoPlanner | Task network orchestration | HDDL 2.1; Alford GTN |
| Agent Q | Policy selection learning | Episodic control + DQN |
| Memory Substrate | Graph + semantic memory | Neo4j + pgvector |
| Feedback Loop | Episodic performance tracking | EPGT; Episodic Memory Actor-Critic |

---

**Status:** Ready for implementation review + Neo4j schema finalization
**Next Step:** Spin up schema + retrieval service prototype; validate with synthetic task set
