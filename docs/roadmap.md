# L9 Development Roadmap

## Completed ✅

### Stage 1: Basic Wiring & Interfaces
- [x] Memory Substrate schema and repository
- [x] Semantic search with pgvector
- [x] World Model engine and state
- [x] WebSocket agent protocol
- [x] PacketEnvelope schema

### Stage 2: Memory + World Model Integration
- [x] Slack ingest → thread context retrieval
- [x] Slack ingest → semantic memory hits
- [x] Insights → World Model orchestrator propagation
- [x] `MemorySubstrateService.trigger_world_model_update()`

### Stage 3: Autonomous Execution
- [x] Mac Agent shell executor (with LocalAPI whitelist)
- [x] Mac Agent browser executor (Playwright automation)
- [x] Mac Agent Python executor (Docker sandbox with subprocess fallback)

---

### Stage 4: LLM-Powered Artifact Generation
- [x] `generate_artifact_with_llm()` function for plans, code, docs
- [x] `draft_work_node` now generates real artifacts via GPT-4
- [x] Context-aware generation (governance rules, project history)
- [x] Auto-detect when code/docs artifacts are needed

---

## In Progress 🔄

### Stage 3.5: Proactive World Model Updates
- [x] `MemorySubstrateService.query_packets()` for world model polling
- [x] `MemorySubstratePacketSource` implementation
- [x] `create_runtime_with_substrate()` factory function
- [ ] Integration with API server startup
- [ ] Background task for `runtime.run_forever()`

---

## Planned 📋

### Stage 4: LLM-Powered Artifact Generation
- [ ] `long_plan_graph.py` → LLM code generation in planning nodes
- [ ] `long_plan_graph.py` → LLM documentation generation
- [ ] Artifact storage and versioning
- [ ] Plan → Executable workflow conversion

### Stage 5: Research Swarm
- [ ] `orchestrators/research_swarm/orchestrator.py` → Implement orchestration logic
- [ ] `orchestrators/research_swarm/convergence.py` → Implement convergence/specialized logic

### Stage 6: Persistence & Reliability
- [ ] World Model snapshots persisted to storage
- [ ] World Model restore from snapshot
- [ ] Checkpoint-based recovery
- [ ] Event sourcing for state reconstruction

---

## Future (Deferred) 🔮

### Self-Evolution Capabilities
> ⚠️ **DEFERRED** - Requires careful security review and governance framework.

The following capabilities are intentionally deferred until proper safety mechanisms are in place:

- **Code self-modification**: Evolution engine reading/writing its own source code
- **Autonomous refactoring**: L9 proposing and applying changes to itself
- **Capability expansion**: L9 adding new tools/executors without human approval

**Prerequisites before implementation:**
1. Comprehensive governance framework
2. Human-in-the-loop approval workflow
3. Rollback mechanisms with full audit trail
4. Sandboxed testing environment for self-modifications
5. Rate limiting on self-modification operations
6. External monitoring and kill switch

**Related stubs (not to be implemented without approval):**
- `orchestrators/evolution/apply_engine.py` → `_read_file()`, `_write_file()`
- Any code that would allow L9 to modify files in its own repository

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2025-12-26 | Initial roadmap created |

