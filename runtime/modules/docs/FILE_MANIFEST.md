# MODULES File Manifest

Complete index of all files in the `modules` directory with one-sentence descriptions.

**Generated:** 2025-01-29  
**Total Files:** 45

---

## Root

- **MODULES_INDEX.md** - Comprehensive index documentation of all 13 modules with capabilities, commands, and integration details.

---

## ace/ (Autonomous Capital Engine)

- **__init__.py** - Module initialization file exporting ACE adapter interface.
- **adapter.py** - ACE adapter wrapping core/capital/ace_*.py functionality for risk scoring, strategy optimization, and capital allocation.

---

## coordination/ (GNN-Based Multi-Agent Coordination)

- **__init__.py** - Module initialization file exporting coordination adapter interface.
- **gnn_adapter.py** - Coordination adapter exposing GNN-based cooperative planning capabilities through standard L9 module interface.
- **gnn_plan.py** - GNN planning implementation scaffold for graph-based cooperative planning and multi-agent coordination.

---

## psi/ (Prerequisite Sequence Intelligence)

- **__init__.py** - Module initialization file exporting PSI adapter interface.
- **adapter.py** - PSI adapter wrapping core/learning/psi_kt.py PSIKTTracer functionality for prerequisite tracing and cross-domain knowledge transfer.

---

## psr/ (Predictive State Representation v2)

- **__init__.py** - Module initialization file exporting PSR adapter interface.
- **psr_adapter.py** - PSR adapter exposing predictive state representation capabilities through standard L9 module interface.
- **psr_v2.py** - PSR v2 implementation with predictive state update equations, observation likelihood computation, and long-horizon prediction logic.

---

## ril/ (Relational Intelligence Layer)

- **__init__.py** - Module initialization file exporting RIL adapter interface.
- **adapter.py** - RIL adapter wrapping core/agents/relational_intelligence.py RelationalIntelligence functionality for relationship-aware reasoning.
- **rel_adapter.py** - Relational adapter providing additional relational intelligence capabilities and graph-based reasoning.
- **relation_transformer.py** - Relation transformer implementation with graph attention updates, edge prediction, and multi-hop relational reasoning.

---

## routing/ (Multi-Agent Routing & Dispatch)

- **__init__.py** - Module initialization file exporting routing adapter interface.
- **adapter.py** - Routing adapter wrapping core/coordination/coplanner.py routing functionality for multi-agent task dispatch and coordination.

---

## safety/ (Safety, Alignment & Governance)

- **__init__.py** - Module initialization file exporting safety adapter interface.
- **adapter.py** - Safety adapter coordinating safety modules including constitutional AI and reflexion capabilities.
- **constitution.py** - Constitutional AI rule enforcement implementation with multi-constraint rule executor and violation detection.
- **constitution_adapter.py** - Constitutional AI adapter exposing rule enforcement capabilities through standard L9 module interface.
- **reflexion.py** - Reflexion implementation for self-reflection and error correction in agent reasoning.
- **reflexion_adapter.py** - Reflexion adapter exposing self-reflection capabilities through standard L9 module interface.

---

## shared/ (Shared Utilities & Tools)

- **adapters.py** - Shared adapters utility providing common adapter patterns and base classes.
- **adapters_adapter.py** - Adapter for shared adapters module exposing adapter utilities through standard L9 module interface.
- **curriculum.py** - Curriculum learning implementation for structured knowledge acquisition and skill progression.
- **curriculum_adapter.py** - Curriculum adapter exposing curriculum learning capabilities through standard L9 module interface.
- **flashrag.py** - FlashRAG ultra-fast retrieval implementation with optimized index construction and query optimization.
- **flashrag_adapter.py** - FlashRAG adapter exposing fast retrieval capabilities through standard L9 module interface.
- **sltm.py** - SLTM (Sequential Long-Term Memory) implementation for maintaining long-term context and memory.
- **sltm_adapter.py** - SLTM adapter exposing long-term memory capabilities through standard L9 module interface.
- **toolformer.py** - Toolformer-2 implementation for tool discovery, tool scoring, and tool composition.
- **toolformer_adapter.py** - Toolformer adapter exposing tool discovery and usage capabilities through standard L9 module interface.

---

## simulation/ (Dreamer-V3 Model-Based RL)

- **__init__.py** - Module initialization file exporting simulation adapter interface.
- **dreamer.py** - Dreamer-V3 implementation with latent rollouts, reward prediction networks, and imagination-based planning.
- **dreamer_adapter.py** - Dreamer-V3 adapter exposing model-based reinforcement learning simulation capabilities through standard L9 module interface.

---

## tot/ (Tree-of-Thoughts Reasoning)

- **__init__.py** - Module initialization file exporting ToT adapter interface.
- **adapter.py** - ToT adapter wrapping core/reasoning/toth.py Tree-of-Thoughts functionality for structured reasoning expansion.
- **deliberate.py** - Deliberate reasoning engine implementation with multi-step reasoning, branch expansion, and beam search.
- **deliberate_adapter.py** - Deliberate reasoning adapter exposing DeepSeek-R1 style deliberate reasoning capabilities through standard L9 module interface.

---

## transforms/ (Data Transformation & Serialization)

- **__init__.py** - Module initialization file exporting transforms adapter interface.
- **adapter.py** - Transforms adapter providing data transformation and serialization utilities including JSON, YAML, base64 encoding, and format conversion.

---

## utils/ (Common Utilities & Helpers)

- **__init__.py** - Module initialization file exporting utils adapter interface.
- **adapter.py** - Utils adapter wrapping core/utils/* utility functionality including metrics collection, retry logic, and common helpers.

---

## Summary Statistics

- **Total Files:** 45
- **Total Modules:** 13
- **File Types:**
  - Python (`.py`): 44 files
  - Markdown (`.md`): 1 file
  - System files (`.DS_Store`): 1 file

### Module Breakdown

1. **ace/** - 2 files (Autonomous Capital Engine)
2. **coordination/** - 3 files (GNN-Based Multi-Agent Coordination)
3. **psi/** - 2 files (Prerequisite Sequence Intelligence)
4. **psr/** - 3 files (Predictive State Representation v2)
5. **ril/** - 4 files (Relational Intelligence Layer)
6. **routing/** - 2 files (Multi-Agent Routing & Dispatch)
7. **safety/** - 6 files (Safety, Alignment & Governance)
8. **shared/** - 10 files (Shared Utilities & Tools)
9. **simulation/** - 3 files (Dreamer-V3 Model-Based RL)
10. **tot/** - 4 files (Tree-of-Thoughts Reasoning)
11. **transforms/** - 2 files (Data Transformation & Serialization)
12. **utils/** - 2 files (Common Utilities & Helpers)

### Implementation Status

- **Adapters:** All modules have adapter.py files implementing the standard L9 Modular AGI Runtime interface (handles/run)
- **Core Implementations:** Many modules include core implementation files (e.g., dreamer.py, deliberate.py, psr_v2.py)
- **Wrappers:** Several adapters wrap existing core/ functionality (ACE, PSI, RIL, ToT, Routing)
- **Scaffolds:** Some implementations are scaffolds marked with TODO comments (GNN planning, PSR, Dreamer-V3, etc.)

---

*This manifest was auto-generated. File descriptions are based on file names, paths, docstrings, and code structure.*

