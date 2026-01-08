# ✅ /plan Command Created (v1.1.0 Protocol-Compliant)

## What Was Built

Created `/plan` slash command at:
- `$HOME/Dropbox/Cursor Governance/GlobalCommands/commands/plan.md`

## Protocol Integration

The command follows the canonical protocols from `.cursor/protocols/`:

| Protocol | Path | Loaded At |
|----------|------|-----------|
| GMP-System-Prompt-v1.0 | `docs/_GMP Execute + Audit/GMP-System-Prompt-v1.0.md` | Phase 0 |
| GMP-Action-Prompt-Canonical-v1.0 | `docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md` | Phase 4 |
| GMP-Audit-Prompt-Canonical-v1.0 | `docs/_GMP Execute + Audit/GMP-Audit-Prompt-Canonical-v1.0.md` | Phase 4 |

## Command Chain Flow

```
/plan invoked
    ↓
┌─────────────────────────────────────────┐
│ PHASE 0: /rules + PROTOCOL LOAD         │
│ → Load GMP-System-Prompt-v1.0           │
│ → Check L9 invariants                   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ PHASE 1: /analyze_evaluate              │
│ → Structure + health + cross-reference  │
│ → Tech debt + impact projection         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ PHASE 2: PLAN SYNTHESIS                 │
│ → Options with pros/cons                │
│ → Preliminary TODO plan                 │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ PHASE 3: /reasoning (RECURSIVE)         │
│ → Abductive (pattern discovery)         │
│ → Deductive (logical validation)        │
│ → Inductive (generalization)            │
│ → Confidence scoring                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ PHASE 4: APPROVAL GEN (PROTOCOL-COMPLIANT)│
│ → Load GMP-Action-Prompt-Canonical      │
│ → Load GMP-Audit-Prompt-Canonical       │
│ → Output canonical TODO format          │
│ → L9 invariant check                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ PHASE 5: /ynp (RECOMMENDATION)          │
│ → Approve + /gmp, OR refine, OR defer   │
└─────────────────────────────────────────┘
```

## Canonical TODO Format

Every TODO in the output follows GMP-Action-Prompt-Canonical:

```markdown
- [T1] File: `/Users/ib-mac/Projects/L9/path/to/file.py`
       Lines: 44-52
       Action: Replace
       Target: `function_name()`
       Change: Replace `old_call()` → `new_call()` without altering surrounding logic
       Gate: py_compile
       Imports: NONE
```

### Forbidden Words (per protocol)
- ❌ "maybe", "likely", "should", "consider", "probably"
- ✅ Use definitive: "Replace X with Y", "Insert Z at line N"

### L9 Invariants Protected
- docker-compose.yml
- kernel_loader.py  
- executor.py
- memory_substrate_service.py
- websocket_orchestrator.py

## Usage Examples

```bash
# Standard planning (loads all protocols)
/plan "Implement rate limiting for API endpoints"

# With target scope
/plan @core/agents/ "Add timeout handling to executor"

# Quick mode (skip reasoning)
/plan --quick "Simple task"

# With constraints
/plan --time 2h --risk LOW "Constrained plan"
```

## Key Guarantee

**The TODO plan output is directly executable by `/gmp` with zero reformatting.**

```bash
# After /plan completes, just run:
/gmp @generated/plans/PLAN-{timestamp}-{description}.md
```

---

**Ready to use!** Just type `/plan "your objective"` in any L9 session.

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | TOO-OPER-003 |
| **Component Name** | Scratchpad Ib |
| **Module Version** | 1.0.0 |
| **Created At** | 2026-01-08T03:17:26Z |
| **Created By** | L9_DORA_Injector |
| **Layer** | operations |
| **Domain** | tools |
| **Type** | schema |
| **Status** | active |
| **Governance Level** | medium |
| **Compliance Required** | True |
| **Audit Trail** | True |
| **Purpose** | Documentation for scratchpad ib |

---
