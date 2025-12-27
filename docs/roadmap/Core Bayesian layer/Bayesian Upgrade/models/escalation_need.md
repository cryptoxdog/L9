---
# === SUITE 6 CANONICAL HEADER ===
suite: "Cursor Governance Suite 6 (L9 + Suite 6)"
version: "1.0.0"
component_id: "PROB-MOD-002"
component_name: "Escalation Need Assessment Model"
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
purpose: "Determine when to escalate issues to user vs. handle autonomously"
summary: "Probabilistic model assessing escalation urgency based on error severity, timing, user patterns, and system state"
success_metrics: ["false_escalation_rate < 0.15", "missed_critical_rate < 0.05"]
---

# Escalation Need Assessment Model

## Decision Context

When encountering errors, issues, or uncertain situations, should I:

- **Immediate Escalation** (WhatsApp/urgent notification)
- **Morning Review** (log for next business day)
- **Handle Autonomously** (resolve without bothering user)

---

## Evidence Sources

### 1. Error Severity (Weight: 0.35)

| Severity Level | Score | Examples |
|----------------|-------|----------|
| Critical | 0.95 | System crash, data loss, security breach |
| High | 0.80 | Service unavailable, build failure, API down |
| Medium | 0.60 | Warning, deprecated usage, minor config issue |
| Low | 0.35 | Info message, successful with warnings |
| Info | 0.15 | Status update, progress notification |

### 2. Time Context (Weight: 0.25)

| Time Range | Score | Rationale |
|------------|-------|-----------|
| 9 AM - 6 PM (weekday) | 0.80 | Working hours, likely available |
| 6 PM - 10 PM (weekday) | 0.50 | Evening, less urgent |
| 10 PM - 7 AM | 0.20 | Night, only urgent matters |
| Weekend (9 AM - 6 PM) | 0.40 | May be available but prefer not to disturb |
| Weekend (other) | 0.15 | Avoid unless critical |

### 3. Historical Response Pattern (Weight: 0.20)

| Pattern | Score | Interpretation |
|---------|-------|----------------|
| User always responds | 0.80 | Values escalations |
| User responds 60-80% | 0.60 | Selective attention |
| User responds <40% | 0.30 | Often ignores, prefer autonomy |
| Similar issue ignored 3+ times | 0.20 | Learn not to escalate this type |

### 4. System State (Weight: 0.15)

| State | Score | Rationale |
|-------|-------|-----------|
| Production system affected | 0.90 | Business impact |
| Development/staging only | 0.50 | Lower urgency |
| Testing/local only | 0.25 | No external impact |
| No active systems affected | 0.10 | Informational only |

### 5. Auto-Resolution Confidence (Weight: 0.05)

| Confidence | Score | Interpretation |
|------------|-------|----------------|
| Can definitely fix | 0.10 | Don't escalate |
| Probably can fix | 0.30 | Try first, escalate if fails |
| Uncertain | 0.60 | Consider escalating |
| Cannot fix | 0.90 | Must escalate |

---

## Escalation Formula

```
P(EscalationNeed) = 
    0.35 × error_severity +
    0.25 × time_appropriateness +
    0.20 × user_response_pattern +
    0.15 × system_state_criticality +
    0.05 × (1 - auto_resolution_confidence)
```

---

## Decision Thresholds

| Threshold | Value | Action |
|-----------|-------|--------|
| **urgent_escalation** | >0.85 | Immediate WhatsApp/notification |
| **next_day_review** | 0.55-0.85 | Log for morning review |
| **autonomous_handling** | <0.55 | Handle without escalation |

---

## Special Rules

### Override Conditions (Always Escalate)

- Security violations detected
- Data loss or corruption risk
- User explicitly requested notification
- Governance rule conflicts detected

### Never Escalate (Always Handle)

- Routine status updates
- Successful operations
- Minor formatting issues
- Informational logs

---

## Example Scenarios

### Scenario 1: Build Failure at 11 PM

```
Evidence:
  error_severity: high → 0.80
  time_context: 11 PM weekday → 0.20
  user_response: 65% response rate → 0.60
  system_state: staging only → 0.50
  auto_resolution: probably can fix → 0.30

Calculation:
  P = (0.80×0.35) + (0.20×0.25) + (0.60×0.20) + (0.50×0.15) + (0.70×0.05)
    = 0.280 + 0.050 + 0.120 + 0.075 + 0.035
    = 0.560

Decision: 0.560 > 0.55 → LOG_FOR_MORNING_REVIEW
Confidence: 0.82

Reasoning: Error is significant but not critical, late hour suggests morning review appropriate, staging impact allows delay.
```

### Scenario 2: Security Alert at 2 PM

```
Evidence:
  error_severity: critical → 0.95
  time_context: 2 PM weekday → 0.80
  user_response: always responds to security → 0.90
  system_state: production affected → 0.90
  auto_resolution: cannot fix → 0.90

Calculation:
  P = (0.95×0.35) + (0.80×0.25) + (0.90×0.20) + (0.90×0.15) + (0.90×0.05)
    = 0.3325 + 0.200 + 0.180 + 0.135 + 0.045
    = 0.8925

Decision: 0.8925 > 0.85 → IMMEDIATE_ESCALATION
Confidence: 0.95

Reasoning: Critical security issue during business hours with production impact requires immediate attention.
```

---

## Learning Signals

| Signal | Learning Action |
|--------|-----------------|
| User responds quickly | ✅ Escalation was appropriate |
| User says "could have waited" | ⬇️ Reduce urgency for this type |
| User says "should have told me sooner" | ⬆️ Increase urgency for this type |
| User ignores notification | ⬇️ Reduce weight for this context |
| User fixes immediately | ✅ Confirms escalation value |

---

## Integration Notes

This model should be called by:
- Error handlers
- Exception processors
- Monitoring systems
- Workflow completion checks

Default behavior: When uncertain (P ≈ 0.50-0.60), prefer logging for review over immediate escalation.

