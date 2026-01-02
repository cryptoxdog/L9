# Deprecated L-CTO Legacy Components

This directory contains deprecated L-CTO components that have been replaced by canonical L9 implementations.

## Archived Files

### `mission.py` (LMission)
- **Status**: DEPRECATED
- **Reason**: Monolithic mission handler conflicts with granular agent architecture
- **Replacement**: Use `agents/l_cto.py` (LCTOAgent) + `AgentExecutorService`
- **Archived**: 2025-12-30

### `l_core/engine.py` (LEngine)
- **Status**: DEPRECATED
- **Reason**: Monolithic reasoning engine conflicts with shared reasoning layer architecture
- **Replacement**: Extract reasoning logic into shared `core/reasoning/` module (future work)
- **Archived**: 2025-12-30

### `l_governance/guardrails.py`
- **Status**: DEPRECATED (useful code extracted)
- **Reason**: Local governance conflicts with global `core/governance/` system
- **Replacement**: 
  - Authority/safety validation → `core/governance/validation.py`
  - Drift detection → `core/governance/validation.py`
  - Audit logging → `core/governance/validation.py`
- **Archived**: 2025-12-30

## Migration Notes

All L-CTO operations should now use:
- `agents/l_cto.py` (LCTOAgent) via `AgentExecutorService`
- `core/governance/validation.py` for additional validation checks
- `memory.substrate_service.MemorySubstrateService` for memory operations
- `PacketEnvelope` model for all memory writes (per PacketEnvelope.yaml spec)

See `docs/ROADMAP.md` Stage 7 for full migration plan.

