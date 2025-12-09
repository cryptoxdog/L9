# L9 Modular AGI Runtime - Modules Index

**Generated:** 2025-11-23  
**Total Modules:** 13  
**Total Files:** 42 Python files

---

## 📁 Module Structure Overview

```
modules/
├── ace/              # Autonomous Capital Engine
├── coordination/     # GNN-Based Multi-Agent Coordination
├── psi/              # Prerequisite Sequence Intelligence
├── psr/              # Predictive State Representation v2
├── ril/              # Relational Intelligence Layer
├── routing/          # Multi-Agent Routing & Dispatch
├── safety/           # Safety, Alignment & Governance
├── shared/           # Shared Utilities & Tools
├── simulation/       # Dreamer-V3 Model-Based RL
├── tot/              # Tree-of-Thoughts Reasoning
├── transforms/       # Data Transformation & Serialization
└── utils/            # Common Utilities & Helpers
```

---

## 📦 Module Details

### 1. **ACE** - Autonomous Capital Engine
**Path:** `modules/ace/`  
**Version:** 1.0.0  
**Purpose:** Financial risk modeling, strategy optimization, and capital allocation

**Capabilities:**
- Risk scoring
- Strategy optimization
- Simulation
- Capital allocation

**Files:**
- `__init__.py` - Module initialization
- `adapter.py` - ACE adapter (wraps core/capital/ace_*.py)

**Commands:**
- `ace`, `capital`, `capital_engine`
- `ace_risk_score`
- `ace_optimize`
- `ace_simulate`

---

### 2. **Coordination** - GNN-Based Multi-Agent Coordination
**Path:** `modules/coordination/`  
**Version:** 1.0.0  
**Purpose:** Graph-based cooperative planning for multi-agent systems

**Capabilities:**
- GNN planning
- Multi-agent coordination
- Cooperative planning

**Files:**
- `__init__.py` - Module initialization
- `gnn_plan.py` - GNN planning implementation (scaffold)
- `gnn_adapter.py` - Coordination adapter interface

**Commands:**
- `coordinate_gnn`, `coordinate_plan`
- `gnn_coordinate`

**Research:**
- GNN-CoPlan (graph-based cooperative planning)
- Multi-Agent Coordination (arXiv:2502.14743)

---

### 3. **PSI** - Prerequisite Sequence Intelligence
**Path:** `modules/psi/`  
**Version:** 1.0.0  
**Purpose:** Cross-domain knowledge transfer and learning path identification

**Capabilities:**
- Trace prerequisites
- Suggest learning paths
- Cross-domain transfer

**Files:**
- `__init__.py` - Module initialization
- `adapter.py` - PSI-KT adapter (wraps core/learning/psi_kt.py)

**Commands:**
- `psi`, `psi_kt`
- `psi_trace`
- `psi_suggest`
- `psi_transfer`

---

### 4. **PSR** - Predictive State Representation v2
**Path:** `modules/psr/`  
**Version:** 1.0.0  
**Purpose:** Predictive state inference for modeling dynamical systems and POMDPs

**Capabilities:**
- Predictive state update
- Belief update
- Long-horizon prediction
- Likelihood computation

**Files:**
- `__init__.py` - Module initialization
- `psr_v2.py` - PSR implementation (scaffold)
- `psr_adapter.py` - PSR adapter interface

**Commands:**
- `psr`, `psr_update`
- `psr_predict`
- `psr_likelihood`
- `psr_belief`

**Research:**
- Predictive State Representations (various)
- Predictive State Inference for POMDPs (arXiv:1207.4167)

---

### 5. **RIL** - Relational Intelligence Layer
**Path:** `modules/ril/`  
**Version:** 1.0.0  
**Purpose:** Emotional and relational intelligence for agent interactions

**Capabilities:**
- Analyze sentiment
- Adjust output (empathy/charisma/professionalism)
- Policy guard
- Set/get controls

**Files:**
- `__init__.py` - Module initialization
- `adapter.py` - RIL adapter (wraps core/agents/relational_intelligence.py)
- `relation_transformer.py` - Relation transformer implementation (scaffold)
- `rel_adapter.py` - Relation transformer adapter interface

**Commands:**
- `ril`, `ril_analyze`
- `ril_adjust`
- `ril_controls`
- `ril_rel`, `ril_graph_attention`, `ril_message_pass`, `ril_edge_prediction`

**Research:**
- Graph Attention Networks (arXiv:1710.10903)
- Relational Transformer architectures

---

### 6. **Routing** - Multi-Agent Routing & Dispatch
**Path:** `modules/routing/`  
**Version:** 1.0.0  
**Purpose:** Route directives to appropriate agents and coordinate execution

**Capabilities:**
- Route directive
- Dispatch task
- Select agent
- Plan execution

**Files:**
- `__init__.py` - Module initialization
- `adapter.py` - Routing adapter (wraps core/coordination/coplanner.py)

**Commands:**
- `route`, `router`, `dispatch`
- `route_directive`
- `select_agent`

---

### 7. **Safety** - Safety, Alignment & Governance
**Path:** `modules/safety/`  
**Version:** 1.0.0  
**Purpose:** Policy enforcement, violation detection, and safety validation

**Capabilities:**
- Policy guard
- Violation detection
- Anomaly detection
- Safety validation

**Files:**
- `__init__.py` - Module initialization
- `adapter.py` - Safety adapter (wraps core/governance/meta_oversight.py)
- `reflexion.py` - Reflexion-2 self-critique implementation (scaffold)
- `reflexion_adapter.py` - Reflexion adapter interface
- `constitution.py` - Constitutional AI implementation (scaffold)
- `constitution_adapter.py` - Constitution adapter interface

**Commands:**
- `safety`, `guard`, `policycheck`
- `reflect`, `safety_critique`
- `safety_rules`, `validate_constraints`

**Research:**
- Reflexion (arXiv:2303.11366)
- Constitutional AI (arXiv:2212.08073)

---

### 8. **Shared** - Shared Utilities & Tools
**Path:** `modules/shared/`  
**Version:** 1.0.0  
**Purpose:** Common utilities for curriculum learning, memory, tools, RAG, and adapters

**Sub-modules:**

#### 8.1 Curriculum Learning
- `curriculum.py` - Auto-curriculum learning (scaffold)
- `curriculum_adapter.py` - Curriculum adapter
- **Commands:** `curriculum`, `generate_curriculum`, `estimate_difficulty`

#### 8.2 Structured Long-Term Memory (SLTM)
- `sltm.py` - SLTM implementation (scaffold)
- `sltm_adapter.py` - SLTM adapter
- **Commands:** `memory_store`, `memory_retrieve`, `memory_consolidate`

#### 8.3 Toolformer-2
- `toolformer.py` - Tool discovery & use (scaffold)
- `toolformer_adapter.py` - Toolformer adapter
- **Commands:** `tool_discover`, `tool_score`, `tool_compose`

#### 8.4 FlashRAG
- `flashrag.py` - Ultra-fast retrieval (scaffold)
- `flashrag_adapter.py` - FlashRAG adapter
- **Commands:** `flashrag`, `fast_retrieve`, `build_index`

#### 8.5 Adapter Management
- `adapters.py` - AdapterFusion/QLoRA-2 (scaffold)
- `adapters_adapter.py` - Adapters adapter
- **Commands:** `adapter_load`, `adapter_fuse`, `adapter_manage`

**Research:**
- Auto-Curriculum Learning (various)
- Structured Long-Term Memory (various)
- Toolformer (arXiv:2302.04761)
- FlashRAG (various)
- AdapterFusion (arXiv:2005.00247)
- QLoRA (arXiv:2305.14314)

---

### 9. **Simulation** - Dreamer-V3 Model-Based RL
**Path:** `modules/simulation/`  
**Version:** 1.0.0  
**Purpose:** Model-based reinforcement learning with latent dynamics

**Capabilities:**
- Latent rollouts
- Model-based planning
- Imagination simulation
- Reward prediction

**Files:**
- `__init__.py` - Module initialization
- `dreamer.py` - Dreamer-V3 implementation (scaffold)
- `dreamer_adapter.py` - Dreamer adapter interface

**Commands:**
- `simulate`, `dream`
- `simulate_rollout`, `latent_rollout`

**Research:**
- Dreamer-V3 (arXiv:2301.04104)

---

### 10. **ToT** - Tree-of-Thoughts Reasoning
**Path:** `modules/tot/`  
**Version:** 1.0.0  
**Purpose:** Multi-step deliberate reasoning with branch expansion and pruning

**Capabilities:**
- Expand proposal
- Select top thoughts
- Merge thoughts
- Generate branches

**Files:**
- `__init__.py` - Module initialization
- `adapter.py` - ToT adapter (wraps core/reasoning/toth.py)
- `deliberate.py` - Deliberate reasoning implementation (scaffold)
- `deliberate_adapter.py` - Deliberate adapter interface

**Commands:**
- `tot`, `tot_expand`, `tree-of-thoughts`
- `tot_deliberate`, `tot_expand`, `tot_prune`, `tot_rerank`

**Research:**
- DeepSeek-R1 (arXiv:2402.03300)
- Tree-of-Thoughts (arXiv:2305.10601)

---

### 11. **Transforms** - Data Transformation & Serialization
**Path:** `modules/transforms/`  
**Version:** 1.0.0  
**Purpose:** Data serialization, encoding, decoding, and format conversion

**Capabilities:**
- Serialize
- Deserialize
- Encode
- Decode
- Format convert

**Files:**
- `__init__.py` - Module initialization
- `adapter.py` - Transforms adapter

**Commands:**
- `transform`, `encode`, `decode`
- `transforms_to_json`, `transforms_to_yaml`
- `transforms_from_json`, `transforms_from_yaml`
- `transforms_base64_encode`, `transforms_base64_decode`

---

### 12. **Utils** - Common Utilities & Helpers
**Path:** `modules/utils/`  
**Version:** 1.0.0  
**Purpose:** Metrics collection, retry logic, and common utility functions

**Capabilities:**
- Metrics collection
- Retry logic
- Performance measurement
- Utility functions

**Files:**
- `__init__.py` - Module initialization
- `adapter.py` - Utils adapter (wraps core/utils/metrics.py, retry.py)

**Commands:**
- `util`, `tools`, `helper`
- `utils_record_metric`
- `utils_retry`

---

## 📊 Module Status Summary

### Production-Ready Modules (Phase 1 Complete)
- ✅ **ACE** - Capital Engine adapter
- ✅ **PSI** - PSI-KT adapter
- ✅ **RIL** - Relational Intelligence adapter
- ✅ **Routing** - Multi-agent routing adapter
- ✅ **Safety** - Meta-oversight adapter
- ✅ **ToT** - Tree-of-Thoughts adapter
- ✅ **Transforms** - Data transformation adapter
- ✅ **Utils** - Common utilities adapter

### Scaffold Modules (Phase 1 Complete, Phase 2 Pending)
- 🏗️ **Coordination** - GNN planning (scaffold ready)
- 🏗️ **PSR** - Predictive State Representation (scaffold ready)
- 🏗️ **Safety (Extended)** - Reflexion + Constitution (scaffold ready)
- 🏗️ **Shared** - All 5 sub-modules (scaffold ready)
- 🏗️ **Simulation** - Dreamer-V3 (scaffold ready)
- 🏗️ **ToT (Extended)** - Deliberate reasoning (scaffold ready)
- 🏗️ **RIL (Extended)** - Relation transformer (scaffold ready)

---

## 🔗 Module Dependencies

### Core Dependencies (from `core/`)
- `core/capital/ace_*.py` → `modules/ace/adapter.py`
- `core/learning/psi_kt.py` → `modules/psi/adapter.py`
- `core/agents/relational_intelligence.py` → `modules/ril/adapter.py`
- `core/coordination/coplanner.py` → `modules/routing/adapter.py`
- `core/governance/meta_oversight.py` → `modules/safety/adapter.py`
- `core/reasoning/toth.py` → `modules/tot/adapter.py`
- `core/utils/metrics.py`, `retry.py` → `modules/utils/adapter.py`

### Scaffold Modules (No Core Dependencies Yet)
- `modules/coordination/` - New research implementation
- `modules/psr/` - New research implementation
- `modules/simulation/` - New research implementation
- `modules/shared/*` - New research implementations
- `modules/safety/reflexion*.py` - New research implementation
- `modules/safety/constitution*.py` - New research implementation
- `modules/tot/deliberate*.py` - New research implementation
- `modules/ril/relation*.py` - New research implementation

---

## 📝 Module Interface Standard

All modules implement the standard L9 Modular AGI Runtime interface:

```python
def handles(command: str) -> bool:
    """Check if this module handles the given command."""
    pass

def run(task: dict) -> dict:
    """
    Execute the task.
    
    Args:
        task: Task dictionary with 'command' and parameters
        
    Returns:
        JSON-serializable dict with structure:
        {
            "success": bool,
            "module": str,
            "operation": str,
            "output": dict | list,
            "error": str (if success=False)
        }
    """
    pass
```

---

## 🎯 Module Categories

### Reasoning & Planning
- **ToT** - Tree-of-Thoughts reasoning
- **PSR** - Predictive state inference
- **Coordination** - Multi-agent planning

### Learning & Knowledge
- **PSI** - Prerequisite sequence intelligence
- **Shared/Curriculum** - Auto-curriculum learning
- **Shared/SLTM** - Structured long-term memory

### Agent Interaction
- **RIL** - Relational intelligence
- **Routing** - Agent routing & dispatch

### Safety & Governance
- **Safety** - Policy enforcement & validation
- **Safety/Reflexion** - Self-critique
- **Safety/Constitution** - Constitutional AI

### Tools & Utilities
- **Shared/Toolformer** - Tool discovery
- **Shared/FlashRAG** - Fast retrieval
- **Shared/Adapters** - Adapter management
- **Transforms** - Data transformation
- **Utils** - Common utilities

### Capital & Simulation
- **ACE** - Capital engine
- **Simulation** - Model-based RL

---

## 📚 Research Integration Status

### Fully Integrated (Production)
- Tree-of-Thoughts (core/reasoning/toth.py)
- Relational Intelligence (core/agents/relational_intelligence.py)
- PSI-KT (core/learning/psi_kt.py)
- ACE Capital Engine (core/capital/ace_*.py)
- Meta-Oversight (core/governance/meta_oversight.py)
- CoPlanner (core/coordination/coplanner.py)

### Scaffold Ready (Phase 2 Pending)
- DeepSeek-R1 / Deliberate Reasoning
- GNN-CoPlan / Multi-Agent Coordination
- Dreamer-V3 / Model-Based RL
- Reflexion-2 / Self-Critique
- Constitutional AI
- Predictive State Representations
- Graph Attention Networks
- Auto-Curriculum Learning
- Structured Long-Term Memory
- Toolformer-2
- FlashRAG
- AdapterFusion / QLoRA-2

---

## 🔄 Module Lifecycle

1. **Phase 1: Scaffold** ✅ Complete
   - Create module structure
   - Generate research-aligned stubs
   - Set up adapter interfaces
   - Establish documentation templates

2. **Phase 2: Implementation** 🏗️ Pending
   - Extract algorithms from papers
   - Pull code from GitHub repos
   - Fill stubs with real implementations
   - Test and validate

3. **Phase 3: Integration** 📋 Future
   - Integrate with L9 runtime
   - Add governance hooks
   - Add execution trace logging
   - Production deployment

---

**Last Updated:** 2025-11-23  
**Maintained By:** L9 Development Team

