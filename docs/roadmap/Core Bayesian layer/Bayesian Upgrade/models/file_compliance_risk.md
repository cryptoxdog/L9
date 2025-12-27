---
# === SUITE 6 CANONICAL HEADER ===
suite: "Cursor Governance Suite 6 (L9 + Suite 6)"
version: "1.0.0"
component_id: "PROB-MOD-001"
component_name: "File Compliance Risk Model"
layer: "intelligence"
domain: "probabilistic_reasoning"
type: "probabilistic_model"
status: "active"
created: "2025-11-08T00:00:00Z"
updated: "2025-11-08T00:00:00Z"
author: "Claude Sonnet 4.5"
maintainer: "Igor Beylin"

# === GOVERNANCE METADATA ===
governance_level: "high"
compliance_required: true
audit_trail: true
security_classification: "internal"

# === TECHNICAL METADATA ===
dependencies: ["FND-LG-003"]
integrates_with: ["probabilistic_engine", "hybrid_kernel", "governance-validator"]
api_endpoints: []
data_sources: ["file_metadata", "edit_history", "user_corrections", "meta-learning-log"]
outputs: ["risk_probability", "confidence_score", "subjective_logic_breakdown"]

# === OPERATIONAL METADATA ===
execution_mode: "realtime"
monitoring_required: true
logging_level: "debug"
performance_tier: "realtime"

# === BUSINESS METADATA ===
purpose: "Assess file compliance risk using probabilistic reasoning"
summary: "Probabilistic model that evaluates risk of file compliance violations based on multiple evidence sources, providing calibrated probability scores and confidence levels"
business_value: "Enables intelligent risk-based governance decisions instead of binary pass/fail"
success_metrics: ["calibration_ece < 0.05", "inference_latency < 10ms", "accuracy > 0.90"]
---

# File Compliance Risk Model

## Decision Context

When I encounter potential file compliance issues (missing headers, wrong structure, outdated format), should I:

- **Block** (high risk - critical governance file)
- **Warn** (medium risk - important but not critical)
- **Log Only** (low risk - user content or acceptable deviation)

---

## Model Definition

### Type
**Weighted Evidence Ensemble** (PAC-Bayesian inspired)

### Target Variable
**ComplianceRisk** - Probability that file non-compliance will cause governance problems

**Range:** 0.0 (no risk) to 1.0 (critical risk)

### Prior Probability
**Initial:** 0.50 (neutral - no assumption)  
**Learning:** Updated nightly from `outcome = 'correct'` rate in decision log

---

## Evidence Sources

### 1. File Location Tier (Weight: 0.30)

**Description:** Risk increases in critical governance directories

| Location Pattern | Risk Score | Rationale |
|------------------|------------|-----------|
| `foundation/logic/` | 0.95 | Core governance engine |
| `foundation/security/` | 0.90 | Security-critical |
| `foundation/` | 0.85 | Foundation layer |
| `intelligence/` | 0.80 | Intelligence layer |
| `execution/` | 0.70 | Execution layer |
| `operations/` | 0.65 | Operations layer |
| `telemetry/` | 0.55 | Monitoring only |
| `Work Files/` | 0.20 | User workspace |
| Other | 0.40 | Unknown territory |

### 2. File Type (Weight: 0.25)

**Description:** Some file types require strict governance

| File Type | Risk Score | Rationale |
|-----------|------------|-----------|
| `governance` | 0.90 | Core governance definitions |
| `security` | 0.85 | Security configurations |
| `config` | 0.80 | System configuration |
| `api` | 0.75 | API definitions |
| `command` | 0.75 | Command definitions |
| `template` | 0.60 | Reusable templates |
| `documentation` | 0.30 | User-facing docs |
| `markdown` | 0.25 | General markdown |
| `user_content` | 0.15 | User workspace files |

**Detection Logic:**
- Check file path patterns
- Inspect canonical header `type` field
- Analyze file extension and content

### 3. Edit Frequency (Weight: 0.20)

**Description:** Frequent edits to governance files indicate active development (higher risk of mistakes)

| Edits Per Week | Risk Score | Rationale |
|----------------|------------|-----------|
| 0-1 | 0.35 | Stable, established file |
| 2-5 | 0.50 | Normal activity |
| 6-10 | 0.65 | High activity, watch carefully |
| 11-20 | 0.75 | Very active, increased risk |
| 20+ | 0.85 | Extremely active, high risk |

**Data Source:** Git history or file modification timestamps

### 4. User Correction Count (Weight: 0.15)

**Description:** If user has corrected me on similar files, I should be less strict

| Correction Count | Risk Adjustment | Rationale |
|------------------|-----------------|-----------|
| 0 | 0.60 | No history, maintain caution |
| 1-2 | 0.50 | Some history, moderate trust |
| 3-4 | 0.35 | User knows this area |
| 5+ | 0.20 | User is expert here, be lenient |

**Data Source:** meta-learning-log.md entries where user said "too strict" for similar file types/locations

### 5. Cascading Impact (Weight: 0.10)

**Description:** Files referenced by many others have higher risk

| References Count | Risk Score | Rationale |
|------------------|------------|-----------|
| 0-1 | 0.30 | Isolated file |
| 2-4 | 0.50 | Some dependencies |
| 5-9 | 0.65 | Moderate dependencies |
| 10-19 | 0.75 | High dependencies |
| 20+ | 0.90 | Critical infrastructure file |

**Detection:** Grep for filename across codebase, count imports/includes

---

## Risk Calculation

### Formula

```
P(ComplianceRisk | Evidence) = 
    w₁ × file_location_score +
    w₂ × file_type_score +
    w₃ × edit_frequency_score +
    w₄ × (1 - user_correction_adjustment) +  // Note: inverse for corrections
    w₅ × cascading_impact_score

Where weights sum to 1.0:
    w₁ = 0.30 (file location)
    w₂ = 0.25 (file type)
    w₃ = 0.20 (edit frequency)
    w₄ = 0.15 (user corrections)
    w₅ = 0.10 (cascading impact)
```

### Correlation Adjustment (PAC-Bayesian)

If evidence sources are correlated (e.g., file_location and file_type often agree), reduce combined weight to avoid double-counting:

```
Adjusted_weight = Original_weight × (1 - correlation_penalty)

Example:
If correlation(file_location, file_type) = 0.75:
    penalty = 0.75 × 0.10 = 0.075
    w₂_adjusted = 0.25 × (1 - 0.075) = 0.23125
```

### Temperature Calibration

Raw probability is calibrated using learned temperature parameter:

```
P_calibrated = sigmoid((P_raw - 0.5) / T)

Where:
    T = learned temperature (starts at 1.0)
    Optimized to minimize ECE
```

---

## Subjective Logic Decomposition

Beyond single probability, track:

**Trust (T):** Evidence supporting "high risk"  
**Disbelief (D):** Evidence supporting "low risk"  
**Uncertainty (U):** Missing or ambiguous evidence

```
T + D + U = 1.0

Calculation:
    positive_evidence = sum of high-scoring evidence
    negative_evidence = sum of low-scoring evidence
    missing_evidence = count of unavailable evidence sources
    
    T = positive_evidence / total_possible
    D = negative_evidence / total_possible
    U = missing_evidence / total_evidence_sources
```

**Decision Enhancement:**

| Scenario | T | D | U | Interpretation | Action |
|----------|---|---|---|----------------|--------|
| Strong evidence | 0.80 | 0.10 | 0.10 | Clear risk | Block confidently |
| Conflicting | 0.45 | 0.40 | 0.15 | Ambiguous | Warn + request clarity |
| Insufficient | 0.35 | 0.20 | 0.45 | Unknown | Escalate to user |

---

## Threshold Decision Rules

### Probabilistic FOL Integration

```
Rule PM-R-001:
IF P(FileComplianceRisk) > threshold('high_risk') 
THEN BLOCK_EDIT() ∧ LOG_DECISION('blocked_high_risk')

Rule PM-R-002:
IF P(FileComplianceRisk) > threshold('medium_risk') ∧ 
   P(FileComplianceRisk) <= threshold('high_risk')
THEN WARN_USER() ∧ LOG_DECISION('warned_medium_risk') ∧ ALLOW_WITH_WARNING()

Rule PM-R-003:
IF P(FileComplianceRisk) <= threshold('medium_risk')
THEN LOG_ONLY() ∧ ALLOW()

Rule PM-R-004 (Uncertainty-Based):
IF Uncertainty > 0.40
THEN ESCALATE_TO_USER() ∧ LOG_DECISION('insufficient_evidence')
```

---

## Learning Loop

### Feedback Signals

| Signal | Source | Weight Update Action |
|--------|--------|---------------------|
| **User adds header after warning** | Behavioral observation | ✅ Reinforce pattern |
| **User says "this is fine"** | Explicit feedback | ⬇️ Decrease risk for context |
| **User ignores warnings 5x** | Behavioral pattern | ⬇️ Decrease weight for file type/location |
| **User escalates after my approval** | Error signal | ⬆️ Increase risk sensitivity |

### Update Frequency

**Real-time:** Immediate threshold micro-adjustments (<5%) on explicit feedback  
**Nightly:** Full recalibration of weights and temperature from last 24h decisions  
**Weekly:** Correlation matrix update and weight optimization

### Convergence Criteria

Model is considered "converged" when:
- ECE < 0.05 for 3 consecutive weeks
- Accuracy > 0.90 for 100+ decisions
- No major weight changes (< 0.05 delta) for 2 weeks

---

## Performance Requirements

| Metric | Target | Monitoring |
|--------|--------|------------|
| **Inference Time** | <10ms p95 | Telemetry logging |
| **Memory Usage** | <5MB | Process monitoring |
| **Accuracy** | >90% | Weekly calibration report |
| **ECE** | <5% | Calculated nightly |
| **False Positive Rate** | <10% | Weekly review |

---

## Example Scenarios

### Scenario 1: Foundation File Edit

```
Evidence:
  file_location: foundation/logic/new-rule.json → 0.95
  file_type: governance → 0.90
  edit_frequency: 2/week → 0.50
  user_corrections: 0 → 0.60
  cascading_refs: 8 → 0.75

Calculation:
  P_raw = (0.95×0.30) + (0.90×0.25) + (0.50×0.20) + (0.60×0.15) + (0.75×0.10)
       = 0.285 + 0.225 + 0.100 + 0.090 + 0.075
       = 0.775

  P_calibrated = sigmoid((0.775 - 0.5) / 1.0) = 0.818

  Subjective Logic:
    Trust = 0.70 (strong evidence for risk)
    Disbelief = 0.15 (some low scores)
    Uncertainty = 0.15 (one evidence missing)

Decision:
  0.818 > 0.65 (medium_risk threshold)
  → WARN_USER + LOG + ALLOW_WITH_CAUTION

Confidence: 0.85 (high confidence, low uncertainty)
```

### Scenario 2: User Workspace File

```
Evidence:
  file_location: Work Files/notes.md → 0.20
  file_type: user_content → 0.15
  edit_frequency: 15/week → 0.75
  user_corrections: 6 → 0.20
  cascading_refs: 0 → 0.30

Calculation:
  P_raw = (0.20×0.30) + (0.15×0.25) + (0.75×0.20) + (0.20×0.15) + (0.30×0.10)
       = 0.060 + 0.0375 + 0.150 + 0.030 + 0.030
       = 0.3075

  P_calibrated = sigmoid((0.3075 - 0.5) / 1.0) = 0.352

  Subjective Logic:
    Trust = 0.25
    Disbelief = 0.65 (strong evidence against risk)
    Uncertainty = 0.10

Decision:
  0.352 < 0.40 (low_risk threshold)
  → LOG_ONLY + ALLOW

Confidence: 0.90 (very confident it's safe)
```

---

## Integration with Meta-Learning Log

### Log Entry Format

When decisions are logged to meta-learning-log.md:

```markdown
## 2025-11-08 14:32:15 - File Compliance Decision

**Decision ID:** DEC-1731078735
**Model:** PM-001 (FileComplianceRisk)
**File:** foundation/logic/new-config.json
**Probability:** 0.818 (calibrated from 0.775)
**Confidence:** 0.85
**Subjective Logic:** T=0.70, D=0.15, U=0.15
**Decision:** WARN + ALLOW
**Outcome:** [To be filled when user responds]

**Evidence Breakdown:**
- file_location: 0.95 (foundation/logic)
- file_type: 0.90 (governance)
- edit_frequency: 0.50 (2/week)
- user_corrections: 0.60 (no history)
- cascading_refs: 0.75 (8 references)

**Learning Opportunity:** Track if user validates warning or says "too strict"
```

---

## Calibration Monitoring

### Weekly Report Format

```
## File Compliance Risk Model - Weekly Calibration Report

**Period:** 2025-11-01 to 2025-11-08
**Decisions Made:** 47
**Outcomes Received:** 41 (6 pending)

### Calibration Metrics
- ECE: 4.2% ✅ (target <5%)
- Accuracy: 92.7% ✅ (target >90%)
- Precision (high_risk): 88.9%
- Recall (high_risk): 94.1%

### Threshold Performance
| Threshold | Precision | Recall | Adjusted |
|-----------|-----------|--------|----------|
| high_risk (0.85) | 88.9% | 94.1% | No change |
| medium_risk (0.65) | 76.3% | 81.2% | ⬆️ +0.02 to 0.67 |
| low_risk (0.40) | 61.5% | 72.8% | No change |

### Weight Updates
| Evidence | Old Weight | New Weight | Change |
|----------|------------|------------|--------|
| file_location | 0.300 | 0.305 | +0.005 |
| user_corrections | 0.150 | 0.145 | -0.005 |

### Temperature
- Current: 1.02
- Change: +0.02 (reduced overconfidence)
- ECE improvement: 5.1% → 4.2%

**Status:** ✅ Well-calibrated, continue monitoring
```

---

## Future Enhancements

### Phase 2 Additions (After Initial Validation)

1. **Context-Specific Temperatures**
   - Different T for foundation/ vs Work Files/
   - Per-project calibration

2. **Temporal Patterns**
   - Learn day-of-week patterns
   - Project phase awareness

3. **User Intent Detection**
   - Distinguish experimental vs production edits
   - Adapt based on commit messages

4. **Multi-File Context**
   - Consider related file changes
   - Batch edit risk assessment

---

## Testing & Validation

### Unit Tests Required

- Evidence calculation for each source
- Weight normalization
- Correlation adjustment
- Temperature scaling
- Threshold classification
- Subjective logic decomposition

### Integration Tests Required

- End-to-end risk assessment
- Learning loop updates
- Calibration metric calculation
- Performance benchmarks (<10ms)

### Validation Dataset

Collect 100 historical decisions with outcomes for initial validation before production deployment.

---

## References

- PAC-Bayesian Ensembles: [arXiv 2406.05469](https://arxiv.org/html/2406.05469v1)
- Temperature Scaling: [Heartbeat Calibration Guide](https://heartbeat.comet.ml/calibration-techniques-in-deep-neural-networks-55ad76fea58b)
- Subjective Logic: [arXiv 2411.00265](https://arxiv.org/abs/2411.00265)
- Uncertainty Primer: [Vizuara Substack](https://vizuara.substack.com/p/a-primer-on-uncertainty-and-calibration)

