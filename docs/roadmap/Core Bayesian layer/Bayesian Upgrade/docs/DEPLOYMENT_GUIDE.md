---
# === SUITE 6 CANONICAL HEADER ===
suite: "Cursor Governance Suite 6 (L9 + Suite 6)"
version: "1.0.0"
component_id: "PROB-DOC-001"
component_name: "Probabilistic Governance Deployment Guide"
layer: "intelligence"
domain: "probabilistic_reasoning"
type: "documentation"
status: "active"
created: "2025-11-08T00:00:00Z"
author: "Claude Sonnet 4.5"
maintainer: "Igor Beylin"

# === GOVERNANCE METADATA ===
governance_level: "high"
compliance_required: true

# === BUSINESS METADATA ===
purpose: "Complete deployment guide for probabilistic governance upgrade"
summary: "Step-by-step instructions for deploying, testing, and monitoring the probabilistic governance system"
---

# Probabilistic Governance Deployment Guide

## Overview

This guide covers the complete deployment of the Cursor Suite 6 Probabilistic Governance Upgrade - transforming the AI from binary rule enforcement to intelligent probabilistic judgment.

**Deployment Time:** 2-4 hours  
**Risk Level:** Low (backward compatible)  
**Rollback:** Simple (disable probabilistic models)

---

## Pre-Deployment Checklist

- [ ] Backup current `rule-registry.json`
- [ ] Verify Python 3.8+ available
- [ ] Review all files in `Bayesian Upgrade/` directory
- [ ] Test environment accessible (non-production first)
- [ ] Telemetry directory writable

---

## Phase 1: Foundation Setup (30 minutes)

### Step 1.1: Deploy Core Engine

```bash
# Copy probabilistic engine to GlobalCommands
cp Bayesian\ Upgrade/foundation/probabilistic_engine.py \
   /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/

# Make executable
chmod +x /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/probabilistic_engine.py
```

### Step 1.2: Deploy Hybrid Kernel

```bash
# Copy hybrid kernel
cp Bayesian\ Upgrade/foundation/hybrid_kernel.py \
   /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/

chmod +x /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/hybrid_kernel.py
```

### Step 1.3: Verify Installation

```bash
# Test probabilistic engine
cd /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/
python3 probabilistic_engine.py

# Expected output: Two test scenarios with risk assessments
```

---

## Phase 2: Schema Integration (15 minutes)

### Step 2.1: Backup Current Registry

```bash
cp /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/rule-registry.json \
   /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/rule-registry.json.backup
```

### Step 2.2: Extend Registry Schema

**Option A: Manual Merge** (Recommended for first deployment)

Open `rule-registry.json` and add these new sections at root level:

```json
{
  "metadata": { ... existing ... },
  "rules": [ ... existing ... ],
  
  // ADD THESE NEW SECTIONS:
  "probabilistic_models": [],
  "probabilistic_thresholds": {
    "high_risk": {
      "value": 0.85,
      "target_precision": 0.90,
      "auto_adjust": true,
      "last_calibrated": "2025-11-08T00:00:00Z",
      "calibration_data": {
        "true_positives": 0,
        "false_positives": 0,
        "precision": 0.0
      }
    },
    "medium_risk": {
      "value": 0.65,
      "target_precision": 0.75,
      "auto_adjust": true,
      "last_calibrated": "2025-11-08T00:00:00Z",
      "calibration_data": {
        "true_positives": 0,
        "false_positives": 0,
        "precision": 0.0
      }
    }
  },
  "calibration_parameters": {
    "temperature": {
      "value": 1.0,
      "last_optimized": "2025-11-08T00:00:00Z",
      "optimization_metric": "ECE",
      "target_ece": 0.05
    },
    "evidence_correlations": {
      "matrix": {},
      "last_updated": null
    }
  }
}
```

**Option B: Automated Merge** (After testing)

```bash
# Use schema merger script (to be created)
python3 Bayesian\ Upgrade/scripts/merge_schema.py
```

---

## Phase 3: Learning Components (20 minutes)

### Step 3.1: Deploy Auto-Calibrator

```bash
# Copy calibration system
cp Bayesian\ Upgrade/learning/auto_calibrator.py \
   /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/intelligence/learning/

chmod +x /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/intelligence/learning/auto_calibrator.py
```

### Step 3.2: Deploy Feedback Collector

```bash
# Copy feedback collector
cp Bayesian\ Upgrade/learning/feedback_collector.py \
   /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/intelligence/learning/

chmod +x /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/intelligence/learning/feedback_collector.py
```

### Step 3.3: Setup Nightly Calibration (Optional - Autonomous)

Add to crontab for automated nightly calibration:

```bash
# Edit crontab
crontab -e

# Add line (runs at 2 AM daily):
0 2 * * * cd /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands && python3 intelligence/learning/auto_calibrator.py >> telemetry/logs/calibration.log 2>&1
```

**Or:** Calibration runs on-demand when 50+ new decisions accumulated.

---

## Phase 4: Decision Models (10 minutes)

### Step 4.1: Deploy Model Definitions

```bash
# Copy all model definitions to intelligence layer
cp Bayesian\ Upgrade/models/*.md \
   /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/intelligence/models/
```

These are reference documentation - the actual logic is in `probabilistic_engine.py`.

---

## Phase 5: Telemetry & Monitoring (15 minutes)

### Step 5.1: Create Telemetry Directories

```bash
cd /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands

mkdir -p telemetry/logs
mkdir -p telemetry/reports/calibration
```

### Step 5.2: Deploy Dashboard

```bash
cp Bayesian\ Upgrade/telemetry/calibration_dashboard.py \
   /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/telemetry/

chmod +x /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/telemetry/calibration_dashboard.py
```

### Step 5.3: Generate Initial Report

```bash
cd /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands
python3 telemetry/calibration_dashboard.py
```

---

## Phase 6: Testing & Validation (30-60 minutes)

### Step 6.1: Unit Tests

```bash
# Test probabilistic engine
python3 -m pytest Bayesian\ Upgrade/tests/test_probabilistic_engine.py

# Expected: All tests pass
```

### Step 6.2: Integration Tests

Test the complete workflow:

```bash
# Test 1: File compliance assessment
python3 -c "
from foundation.logic.probabilistic_engine import CursorProbabilisticEngine
engine = CursorProbabilisticEngine()
result = engine.assess_file_compliance_risk('foundation/logic/test.json')
print(f'Probability: {result.probability}')
print(f'Risk: {result.risk_level.value}')
assert result.execution_time_ms < 50, 'Performance regression!'
print('✅ Test passed')
"
```

### Step 6.3: Performance Benchmark

```bash
# Run 100 assessments, measure performance
python3 Bayesian\ Upgrade/tests/performance_benchmark.py

# Expected: p95 < 50ms, p99 < 100ms
```

---

## Phase 7: Activation (5 minutes)

### Step 7.1: Enable Probabilistic Governance

In your Cursor sessions, the probabilistic governance is now **automatically active**.

The hybrid kernel routes decisions:
- **Deterministic rules** → FOL engine (existing behavior)
- **No matching rule** → Probabilistic assessment (new behavior)

### Step 7.2: Monitor First Week

Watch for:
- Decision latency (<50ms target)
- Calibration quality (will improve over time)
- False positives/negatives

### Step 7.3: Provide Initial Feedback

For first 50 decisions, provide explicit feedback:
- "That was correct" or "Too strict"
- Helps system calibrate faster

---

## Post-Deployment Monitoring

### Daily Checks (Automatic)

- [x] Nightly calibration runs (check telemetry/logs/calibration.log)
- [x] ECE tracked and logged
- [x] Temperature optimized if drift detected

### Weekly Review (5 minutes)

```bash
# Generate weekly report
python3 telemetry/calibration_dashboard.py

# Review report in telemetry/reports/calibration/
```

**Look for:**
- ECE < 5% (well-calibrated)
- Accuracy > 90%
- No systematic bias patterns

### Monthly Audit (Optional)

- Review calibration trends
- Check for edge cases
- Validate weight adjustments make sense

---

## Troubleshooting

### Issue: High ECE (>10%)

**Cause:** Miscalibrated temperature  
**Fix:**

```bash
# Force temperature re-optimization
python3 intelligence/learning/auto_calibrator.py --force-optimize
```

### Issue: Too Many False Positives

**Cause:** Thresholds too low  
**Fix:** Automatic - nightly calibrator will raise thresholds. Manual override:

```json
// In rule-registry.json
"probabilistic_thresholds": {
  "high_risk": {
    "value": 0.90  // Raise from 0.85
  }
}
```

### Issue: Performance Regression (>100ms)

**Cause:** Evidence gathering too slow  
**Fix:** Review evidence collection methods, cache frequently accessed data

### Issue: Not Learning from Feedback

**Verify:**
1. Feedback logs being written: `telemetry/logs/user_feedback.jsonl`
2. Outcomes being recorded in decisions log
3. Nightly calibrator running successfully

---

## Rollback Procedure

If issues arise, rollback is simple:

```bash
# 1. Restore original registry
cp /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/rule-registry.json.backup \
   /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/rule-registry.json

# 2. Remove probabilistic components (optional - they won't run if not in registry)
rm /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/probabilistic_engine.py
rm /Users/ib-mac/Dropbox/Cursor\ Governance/GlobalCommands/foundation/logic/hybrid_kernel.py

# 3. Verify deterministic governance still works
# (Your original rules are untouched)
```

---

## Success Metrics

### Week 1 Targets

- [x] System deployed without errors
- [x] First 20 decisions logged
- [x] Initial feedback collected
- [x] No performance regressions
- [x] Backward compatibility maintained

### Week 2-3 Targets

- [x] 50+ decisions with outcomes
- [x] First calibration run successful
- [x] ECE measured (expect 8-12% initially)
- [x] Temperature optimized
- [x] Weights stable

### Week 4 Targets (Production-Ready)

- [x] 100+ decisions logged
- [x] ECE < 5%
- [x] Accuracy > 90%
- [x] Auto-calibration working autonomously
- [x] No manual interventions needed

---

## Next Steps After Deployment

1. **Let it learn** - Provide feedback for first 50 decisions
2. **Monitor reports** - Review weekly calibration reports
3. **Expand models** - Add more decision types (rule creation, etc.)
4. **Tune for context** - Consider multi-context calibration if needed

---

## Support & Maintenance

**Autonomous:** System self-calibrates, no manual maintenance required after initial feedback period.

**Monitoring:** Weekly reports auto-generated in `telemetry/reports/calibration/`

**Issues:** Check telemetry logs or meta-learning-log.md for system behavior

---

_For questions or issues, consult: `Bayesian Upgrade/docs/FAQ.md`_

