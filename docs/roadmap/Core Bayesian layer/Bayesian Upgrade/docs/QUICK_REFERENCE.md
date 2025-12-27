---
# === SUITE 6 CANONICAL HEADER ===
suite: "Cursor Governance Suite 6 (L9 + Suite 6)"
version: "1.0.0"
component_id: "PROB-DOC-003"
component_name: "Probabilistic Governance Quick Reference"
type: "documentation"
status: "active"
---

# Probabilistic Governance - Quick Reference

## API Cheat Sheet

### Assess File Risk

```python
from foundation.logic.probabilistic_engine import CursorProbabilisticEngine

engine = CursorProbabilisticEngine()

assessment = engine.assess_file_compliance_risk(
    file_path="foundation/logic/test.json",
    file_type="config",                    # Optional
    edit_frequency=3.5,                    # Edits/week
    user_correction_count=0,               # Times corrected
    references_count=5                     # Files referencing this
)

print(f"Risk: {assessment.probability}")
print(f"Confidence: {assessment.confidence}")
print(f"Action: {assessment.recommended_action}")
```

### Make Governance Decision

```python
from foundation.logic.hybrid_kernel import HybridInferenceKernel

kernel = HybridInferenceKernel()

decision = kernel.evaluate_governance_action(
    action_type='file_edit',  # or 'command_execution', 'escalation'
    context={
        'file_path': 'foundation/test.py',
        'file_type': 'config',
        'edit_frequency': 2.0
    }
)

if decision.result:
    print("ALLOW")
else:
    print(f"BLOCK: {decision.reasoning}")
```

### Record Feedback

```python
from intelligence.learning.feedback_collector import FeedbackCollector

collector = FeedbackCollector()

# Explicit feedback
collector.record_explicit_feedback(
    decision_id="DEC-123456",
    feedback="too_strict",  # or 'correct', 'too_lenient'
    context={'file': 'Work Files/notes.md'}
)

# Implicit feedback (from behavior)
collector.record_implicit_feedback(
    decision_id="DEC-123456",
    user_action="edited_file",  # or 'said_fine', 'overrode'
    decision_context={'decision_action': 'WARN_AND_LOG'}
)
```

### Run Calibration

```python
from intelligence.learning.auto_calibrator import AutoCalibrator

calibrator = AutoCalibrator()
report = calibrator.run_calibration()

print(f"ECE: {report.ece_before} → {report.ece_after}")
print(f"Temperature: {report.temperature_before} → {report.temperature_after}")
```

### Generate Dashboard

```python
from telemetry.calibration_dashboard import CalibrationDashboard

dashboard = CalibrationDashboard()
report = dashboard.generate_weekly_report()

print(report)  # Markdown report
```

---

## Decision Thresholds

| Threshold | Value | Meaning |
|-----------|-------|---------|
| **high_risk** | 0.85 | Block or require review |
| **medium_risk** | 0.65 | Warn user |
| **low_risk** | 0.40 | Log only |
| Below 0.40 | - | Allow silently |

**Auto-adjusting:** These values optimize automatically from outcomes.

---

## Evidence Sources (File Compliance)

| Source | Weight | What It Measures |
|--------|--------|------------------|
| `file_location` | 30% | Criticality of directory |
| `file_type` | 25% | Type of file (governance/config/etc) |
| `edit_frequency` | 20% | How often file is edited |
| `user_corrections` | 15% | How often you corrected me |
| `cascading_impact` | 10% | How many files reference this |

---

## Feedback Types

| Feedback | Meaning | System Response |
|----------|---------|-----------------|
| `correct` | I was right | Reinforce pattern |
| `too_strict` | False alarm | Lower threshold/temp |
| `too_lenient` | Missed risk | Raise threshold/temp |
| `unclear` | Ambiguous | No immediate action |

---

## Subjective Logic

Every decision includes:

| Component | Meaning | Example |
|-----------|---------|---------|
| **Trust (T)** | Evidence FOR risk | 0.70 |
| **Disbelief (D)** | Evidence AGAINST risk | 0.15 |
| **Uncertainty (U)** | Missing/ambiguous | 0.15 |

**Must sum to 1.0**

**Interpretation:**
- High T + Low U = Confident in risk
- High U = Insufficient evidence → escalate
- T ≈ D = Conflicting evidence → warn

---

## Performance Targets

| Metric | Target | Typical |
|--------|--------|---------|
| Inference time | <50ms | ~8ms |
| ECE | <5% | ~4% (after calibration) |
| Accuracy | >90% | ~93% |
| Memory | <10MB | ~4MB |

---

## Monitoring

### Check Calibration Quality

```bash
# Weekly report
python3 telemetry/calibration_dashboard.py

# Look for:
# - ECE < 5%
# - Accuracy > 90%
# - No systematic bias
```

### Check System Health

```bash
# View recent decisions
tail -20 telemetry/logs/probabilistic_decisions.jsonl | jq .

# Check for errors
grep ERROR telemetry/logs/*.log
```

---

## Common Patterns

### Pattern 1: Check Risk Before Edit

```python
# Before editing governance file
assessment = engine.assess_file_compliance_risk(file_path)

if assessment.risk_level.value in ['high', 'critical']:
    print(f"⚠️  High risk: {assessment.reasoning}")
    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != 'y':
        return
```

### Pattern 2: Command Pre-Flight Check

```python
# Before executing heavy command
decision = kernel.evaluate_governance_action(
    action_type='command_execution',
    context={'command': '/forge', 'target_files': files}
)

if not decision.result:
    print(f"❌ Command blocked: {decision.reasoning['explanation']}")
    return
```

### Pattern 3: Smart Escalation

```python
# In error handler
decision = kernel.evaluate_governance_action(
    action_type='escalation',
    context={
        'error_severity': 0.80,
        'hour': datetime.now().hour,
        'similar_escalation_count': 3
    }
)

if decision.reasoning['action'] == 'IMMEDIATE_ESCALATION':
    send_notification()
elif decision.reasoning['action'] == 'LOG_FOR_MORNING_REVIEW':
    log_for_review()
else:
    handle_autonomously()
```

---

## Troubleshooting Quick Fixes

### Too Many Warnings

```python
# Lower medium_risk threshold
engine.thresholds['medium_risk']['value'] = 0.70  # From 0.65

# Or wait for auto-calibration to adjust
```

### Missing Risky Files

```python
# Lower high_risk threshold
engine.thresholds['high_risk']['value'] = 0.80  # From 0.85
```

### Slow Performance

```bash
# Check evidence gathering
# Cache file metadata, git history

# Profile:
python3 -m cProfile foundation/logic/probabilistic_engine.py
```

---

## File Locations (After Deployment)

```
GlobalCommands/
├── foundation/logic/
│   ├── probabilistic_engine.py
│   ├── hybrid_kernel.py
│   └── rule-registry.json (extended)
│
├── intelligence/learning/
│   ├── auto_calibrator.py
│   └── feedback_collector.py
│
├── intelligence/models/
│   ├── file_compliance_risk.md
│   ├── escalation_need.md
│   └── command_execution_risk.md
│
└── telemetry/
    ├── logs/
    │   ├── probabilistic_decisions.jsonl
    │   └── user_feedback.jsonl
    ├── reports/calibration/
    └── calibration_dashboard.py
```

---

## Help & Support

| Issue | Resource |
|-------|----------|
| **Deployment** | `docs/DEPLOYMENT_GUIDE.md` |
| **Integration** | `docs/INTEGRATION_GUIDE.md` |
| **FAQ** | `docs/FAQ.md` |
| **Performance** | `tests/performance_benchmark.py` |
| **Bugs** | Check telemetry logs first |

---

## Version History

**v1.0.0** (2025-11-08) - Initial release
- Core probabilistic engine
- Temperature calibration
- Subjective logic
- Three decision models
- Auto-calibration system
- Complete documentation

---

_For complete documentation, see README.md and docs/ directory._

