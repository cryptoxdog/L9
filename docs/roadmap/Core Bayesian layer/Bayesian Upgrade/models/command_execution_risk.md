---
# === SUITE 6 CANONICAL HEADER ===
suite: "Cursor Governance Suite 6 (L9 + Suite 6)"
version: "1.0.0"
component_id: "PROB-MOD-003"
component_name: "Command Execution Risk Model"
layer: "intelligence"
domain: "probabilistic_reasoning"
type: "probabilistic_model"
status: "active"
created: "2025-11-08T00:00:00Z"
author: "Claude Sonnet 4.5"
maintainer: "Igor Beylin"

# === GOVERNANCE METADATA ===
governance_level: "high"
compliance_required: true
audit_trail: true

# === TECHNICAL METADATA ===
dependencies: ["PROB-MOD-001"]
integrates_with: ["probabilistic_engine", "hybrid_kernel"]

# === BUSINESS METADATA ===
purpose: "Assess risk of command execution and determine approval requirements"
summary: "Probabilistic model evaluating command execution safety based on command type, targets, user patterns, and potential impact"
success_metrics: ["approval_accuracy > 0.92", "false_block_rate < 0.08"]
---

# Command Execution Risk Model

## Decision Context

When user issues commands (`/forge`, `/reasoning`, `/consolidate`, etc.), should I:

- **Auto-Approve** (execute immediately)
- **Confirm First** (show preview, await confirmation)
- **Require Detailed Review** (explain all changes, get explicit approval)

---

## Evidence Sources

### 1. Command Type Baseline Risk (Weight: 0.30)

| Command | Base Risk | Rationale |
|---------|-----------|-----------|
| `/reasoning` | 0.15 | Read-only analysis |
| `/analyze-toolkit` | 0.20 | Read-only evaluation |
| `/evaluate` | 0.25 | Analysis with recommendations |
| `/consolidate` | 0.65 | File moves, potential data loss |
| `/forge` | 0.70 | Heavy modifications |
| Custom/unknown | 0.50 | Unknown risk profile |

### 2. Target File Risk (Weight: 0.35)

| Target Location | Risk Score | Rationale |
|-----------------|------------|-----------|
| `foundation/` | 0.95 | Core governance |
| `intelligence/` | 0.85 | Intelligence layer |
| `.cursor-commands/` | 0.90 | Global commands |
| `execution/` | 0.75 | Execution layer |
| `operations/` | 0.65 | Operations |
| `Work Files/` | 0.25 | User workspace |
| Multiple layers | 0.80 | Cross-cutting changes |

### 3. User Approval Pattern (Weight: 0.20)

| Pattern | Risk Adjustment | Interpretation |
|---------|-----------------|----------------|
| Always approves as-is | 0.90 → 0.70 | High trust, reduce friction |
| Usually approves (80%+) | 0.90 → 0.75 | Good trust |
| Sometimes modifies (50-80%) | No change | Normal review |
| Often rejects (>30%) | 0.90 → 0.95 | Requires careful review |

### 4. Blast Radius (Weight: 0.10)

| Impact Scope | Score | Examples |
|--------------|-------|----------|
| 1-2 files | 0.30 | Localized changes |
| 3-10 files | 0.55 | Moderate scope |
| 11-50 files | 0.75 | Large refactor |
| 50+ files | 0.90 | System-wide changes |
| Cross-directory | 0.85 | Multiple subsystems |

### 5. Reversibility (Weight: 0.05)

| Reversibility | Score | Examples |
|---------------|-------|----------|
| Easily reversed | 0.20 | File renames, header updates |
| Moderately reversible | 0.50 | Code refactoring |
| Difficult to reverse | 0.75 | Schema migrations |
| Irreversible | 0.95 | Deletions, overwrites |

---

## Risk Calculation

```
P(CommandRisk) = 
    0.30 × command_baseline_risk +
    0.35 × target_file_risk +
    0.20 × (1 - user_trust_adjustment) +
    0.10 × blast_radius_score +
    0.05 × reversibility_risk
```

---

## Decision Thresholds

| Threshold | Value | Action |
|-----------|-------|--------|
| **high_risk** | >0.80 | Require detailed review + explicit approval |
| **medium_risk** | 0.55-0.80 | Show preview + confirm before execution |
| **low_risk** | <0.55 | Auto-approve with logging |

---

## Special Overrides

### Always Require Approval

- Deletions of governance files
- Changes to security configurations
- Modifications to `.cursor-commands/`
- Commands targeting >50 files

### Always Auto-Approve

- `/reasoning` (read-only)
- `/analyze-toolkit` (read-only)
- Commands on `Work Files/` only
- User explicitly said "always approve for this"

---

## Example Scenarios

### Scenario 1: /forge on Work Files

```
Evidence:
  command_type: /forge → 0.70
  target: Work Files/ → 0.25
  user_approval: 95% approval rate → 0.70 adjustment
  blast_radius: 8 files → 0.55
  reversibility: easily reversed → 0.20

Calculation:
  P = (0.70×0.30) + (0.25×0.35) + (0.30×0.20) + (0.55×0.10) + (0.20×0.05)
    = 0.210 + 0.0875 + 0.060 + 0.055 + 0.010
    = 0.4225

Decision: 0.4225 < 0.55 → AUTO_APPROVE
Confidence: 0.88

Reasoning: Heavy command but low-risk target area, high user trust, easily reversible.
```

### Scenario 2: /consolidate on foundation/

```
Evidence:
  command_type: /consolidate → 0.65
  target: foundation/ → 0.95
  user_approval: 70% approval → 0.80 adjustment
  blast_radius: 15 files → 0.75
  reversibility: moderately reversible → 0.50

Calculation:
  P = (0.65×0.30) + (0.95×0.35) + (0.20×0.20) + (0.75×0.10) + (0.50×0.05)
    = 0.195 + 0.3325 + 0.040 + 0.075 + 0.025
    = 0.6675

Decision: 0.6675 in [0.55, 0.80] → SHOW_PREVIEW_AND_CONFIRM
Confidence: 0.85

Reasoning: Medium risk due to critical target location and moderate blast radius. Preview recommended.
```

---

## Learning Signals

| User Response | Learning Action |
|---------------|-----------------|
| Approves without modification | ✅ Confirms risk assessment |
| Modifies before approval | ⚠️ Review what was changed, adjust model |
| Rejects completely | ⬆️ Increase risk sensitivity for this pattern |
| Says "just do it next time" | ⬇️ Reduce risk for this command/target combo |
| Approves but later reverts | ⬆️⬆️ Significantly increase risk assessment |

---

## Integration

Used by:
- Command parser (before execution)
- Forge mode (before heavy operations)
- Consolidation operations
- File reorganization

Default: Prefer showing preview over silent execution for medium-risk commands.

