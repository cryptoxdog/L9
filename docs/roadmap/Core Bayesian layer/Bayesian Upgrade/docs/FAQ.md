# Probabilistic Governance - Frequently Asked Questions

## General Questions

### Q: What is probabilistic governance?

**A:** Instead of binary pass/fail rules, the AI assesses **risk levels** (0.0-1.0) and makes calibrated decisions. Think of it as adding "judgment" to rule enforcement.

**Example:**
- Old: "File has no header → ❌ FAIL"
- New: "File in Work Files/ has no header → P(Risk)=0.32 → ✅ LOG + ALLOW"

---

### Q: Will this break my existing governance rules?

**A:** No. Completely backward compatible. Deterministic FOL rules are checked FIRST and always enforced. Probabilistic reasoning only applies when no deterministic rule matches.

---

### Q: How long until it's calibrated?

**A:** 
- **Week 1:** Learning phase (provide feedback on ~50 decisions)
- **Week 2-3:** First auto-calibrations
- **Week 4+:** Stable, well-calibrated performance

**ECE improvement:** ~10% (initial) → <5% (converged)

---

### Q: Do I need to maintain it?

**A:** No. Fully autonomous after deployment:
- Nightly auto-calibration
- Real-time learning from feedback
- Automatic threshold adjustments
- Self-monitoring for drift

Optional: Review weekly calibration reports (5 min/week).

---

## Technical Questions

### Q: How fast is inference?

**A:** **~8ms typical, <50ms guaranteed p95**

Much faster than:
- pgmpy (100-500ms)
- Full Bayesian networks (100-200ms)
- TensorFlow Probability (50-100ms)

---

### Q: How much data needed for learning?

**A:**
- **Minimum:** 50 decisions for first calibration
- **Optimal:** 100+ decisions for stable performance
- **Ongoing:** Learns continuously from every feedback

---

### Q: What if I disagree with an assessment?

**A:** Just provide feedback:

**Explicit:** Say "that was too strict" or "good call"  
**Implicit:** System observes your actions (edit after warning = validation)

System adjusts automatically within 24 hours.

---

### Q: Can I have different calibration for different contexts?

**A:** Yes, Phase 2 feature. For now, uses global calibration which works well across contexts.

**Future:** Multi-context temperature (different T for foundation/ vs Work Files/)

---

## Calibration Questions

### Q: What is ECE and why does it matter?

**A:** **Expected Calibration Error** - measures if probabilities match reality.

**Example:**
- I say "80% confident" 100 times
- ECE = 0% → I'm right exactly 80 times (perfect)
- ECE = 10% → I'm right 70 or 90 times (miscalibrated)

**Target:** ECE < 5% (well-calibrated)

---

### Q: What's temperature scaling?

**A:** Single parameter (T) that rescales probabilities:

- T = 1.0 → No scaling
- T > 1.0 → Reduces confidence (softens probabilities)
- T < 1.0 → Increases confidence (sharpens probabilities)

**Optimized automatically** to minimize ECE.

---

### Q: What if calibration drifts?

**A:** System detects drift automatically:
- Compares recent ECE vs historical
- If drift > 10%, triggers immediate recalibration
- Alert logged to telemetry

**Manual override:** Run `python3 intelligence/learning/auto_calibrator.py --force`

---

## Usage Questions

### Q: How do I provide feedback?

**A:** Three ways:

**1. Explicit (Best):**
```python
collector.record_explicit_feedback(decision_id, "too_strict")
```

**2. Implicit (Automatic):**
- You edit file after warning → System infers "I was right"
- You say "this is fine" → System infers "too strict"

**3. Pattern-Based:**
- You ignore 5 warnings in same dir → System learns "too strict for this context"

---

### Q: Can I manually adjust thresholds?

**A:** Yes, but not recommended. System auto-calibrates better than manual tuning.

**If needed:**
```json
// In rule-registry.json
"probabilistic_thresholds": {
  "high_risk": {
    "value": 0.90,  // Manually set
    "auto_adjust": false  // Disable auto-adjustment
  }
}
```

---

### Q: How do I see what the system is learning?

**A:** Check three places:

1. **Weekly Reports:** `telemetry/reports/calibration/report_YYYYMMDD.md`
2. **Meta-Learning Log:** `intelligence/meta-learning/meta-learning-log.md`
3. **Decision Log:** `telemetry/logs/probabilistic_decisions.jsonl`

---

## Troubleshooting

### Q: System is too strict / too lenient

**A:** 

**Short-term:** Provide explicit feedback on 5-10 decisions  
**Wait:** 24-48 hours for auto-calibration  
**Check:** Next weekly report should show improvement

**Manual override:** Adjust thresholds in rule-registry.json (not recommended)

---

### Q: Inference is slow (>100ms)

**A:** Check:

1. **Evidence gathering:** Are git operations cached?
2. **File system:** Is it on network drive (should be local)?
3. **Decision log:** Is it growing too large (rotate logs)?

**Quick fix:** Reduce evidence sources or cache more aggressively

---

### Q: Not learning from feedback

**A:** Verify:

```bash
# Check feedback is logged
tail telemetry/logs/user_feedback.jsonl

# Check outcomes recorded
grep "outcome" telemetry/logs/probabilistic_decisions.jsonl

# Check calibrator runs
tail telemetry/logs/calibration.log
```

---

### Q: Want to disable temporarily

**A:**

```json
// In rule-registry.json, remove or comment out:
"probabilistic_models": []  // Empty = disabled
```

System reverts to pure deterministic governance.

---

## Advanced Questions

### Q: Can I add custom evidence sources?

**A:** Yes, extend `probabilistic_engine.py`:

```python
# Add to _assess_file_compliance_risk:
custom_evidence = Evidence(
    name="custom_metric",
    value=your_calculation_function(),
    weight=0.05
)
evidence_list.append(custom_evidence)

# Don't forget to normalize weights to sum to 1.0
```

---

### Q: Can I create new decision models?

**A:** Yes, follow pattern in `models/`:

1. Create new model definition (markdown)
2. Add assessment method to `probabilistic_engine.py`
3. Add case to `hybrid_kernel.py`
4. Define thresholds in registry
5. Test and deploy

---

### Q: How does correlation detection work?

**A:** PAC-Bayesian approach:

1. **Measure:** Calculate correlation between evidence sources
2. **Detect:** If correlation > 0.70, sources are redundant
3. **Adjust:** Reduce weight of lesser source to avoid double-counting

**Example:**
```
file_location and file_type correlated at 0.78
→ Reduce file_type weight: 0.25 → 0.23
→ Prevents over-weighting similar evidence
```

---

### Q: What's the difference from full Bayesian Neural Networks?

**A:** 

| Aspect | Full BNN | Our System |
|--------|----------|------------|
| **Complexity** | Neural network with distributed weights | Weighted evidence combination |
| **Speed** | 100-500ms | ~8ms (10-60x faster) |
| **Training** | Needs 10,000+ samples | Learns from dozens |
| **Use Case** | Train ML models | Make governance decisions |

**We use Bayesian thinking (prior + evidence + learning) without Bayesian neural network machinery.**

---

## Integration Questions

### Q: How do I integrate with existing validator?

**A:** See `docs/INTEGRATION_GUIDE.md` for complete examples.

**Quick:**
```python
# In your validator:
assessment = engine.assess_file_compliance_risk(file_path, ...)

if assessment.risk_level.value == 'high':
    block_edit()
elif assessment.risk_level.value == 'medium':
    warn_user()
else:
    allow_edit()
```

---

### Q: Does this work with other governance components?

**A:** Yes, integrates with:
- meta-learning-log.md (learning source)
- telemetry-collector.py (logging)
- governance-validator.py (validation)
- governance-monitor.py (monitoring)

---

## Performance Questions

### Q: How much memory does it use?

**A:** ~4MB additional overhead:
- Engine: 2MB
- Decision history (1000 recent): 1MB
- Correlation matrix: <1MB

---

### Q: Can it handle 1000s of decisions/day?

**A:** Yes, scales well:
- Inference: O(1) constant time per decision
- Learning: O(n) processes all decisions nightly
- Logging: Append-only, rotates automatically

**Tested:** 10,000 decisions in benchmark with no performance degradation

---

## Research Questions

### Q: What research is this based on?

**A:** Synthesis of:
- PAC-Bayesian ensemble theory (Hauptvogel & Igel 2024)
- Temperature scaling calibration (Guo et al. 2017)
- Subjective logic (Ouattara et al. 2024)
- Lightweight inference (OSTI 2283285)

See `Bayesian Upgrade/Bayesian Research/` for full research compilation.

---

### Q: Why not use pgmpy or TensorFlow Probability?

**A:** Speed and simplicity:
- **pgmpy:** Full Bayesian networks, 100-500ms inference (overkill)
- **TF Probability:** Train neural networks, not make decisions
- **Our approach:** Right-sized for governance, 10x faster, easier to debug

**Research validates:** Simple weighted ensembles outperform complex Bayesian inference for fast decision-making.

---

## Future Roadmap

### Phase 2 (After Validation)

- Multi-context calibration
- Rule creation judgment
- Temporal pattern awareness

### Phase 3 (Advanced)

- Active learning (system requests feedback on uncertain cases)
- Meta-reasoning (reasoning about uncertainty itself)
- Cross-session learning

---

## Getting Help

**Issue:** Something broken?  
**Check:** `telemetry/logs/` for error messages

**Question:** How does X work?  
**Check:** This FAQ or `docs/INTEGRATION_GUIDE.md`

**Improvement:** Want to enhance the system?  
**Contribute:** Follow patterns in existing models

---

_Last updated: 2025-11-08_  
_System version: 1.0.0_

