 [1 tool called]

Executing systematically. 

## PHASE -1 — ANALYSIS & PLANNING

[3 tools called]

**PHASE -1 ANALYSIS COMPLETE:**

| Line | Current Code | Replacement | Flag Exists? |
|------|-------------|-------------|--------------|
| 797 | `settings.slack_app_enabled` | `_has_slack` | ✅ Yes (line 40) |
| 805 | `settings.mac_agent_enabled` | `_has_mac_agent` | ❌ Need to add |
| 813 | `settings.twilio_enabled` | `_has_twilio_adapter` | ✅ Yes (line 116) |
| 821 | `settings.waba_enabled` | `_has_waba` | ❌ Need to add |
| 829 | `settings.email_enabled` | `_has_email_adapter` | ✅ Yes (line 108) |

## PHASE 0 — BASELINE CONFIRMATION

[3 tools called]

**PHASE 0 BASELINE CONFIRMED:**
- ✅ File exists
- ✅ Line 797 contains `settings.slack_app_enabled`
- ✅ Feature flags defined at lines 30-133
- ✅ No `settings` import exists (that's the bug!)
- ✅ 5 total `settings.` references found

## PHASE 1 — PRIMARY IMPLEMENTATION

Adding missing flags first, then replacing all references:

[1 tool called]

Now replacing all `settings.` references:

[5 tools called]

## PHASE 2 — ENFORCEMENT

[2 tools called]

✅ Zero `settings.` references remain!

The linter warning about `api.webhook_email` is pre-existing (missing optional module), not related to this fix.

## PHASE 3 & 4 — VERIFICATION

[2 tools called]

## PHASE 5 — FINAL SANITY SWEEP

[1 tool called]

---

# ✅ FINAL REPORT

**FILES CHANGED:**
- `/Users/ib-mac/Projects/L9/api/server.py`

**CHANGES MADE:**

| Change | Location | Count |
|--------|----------|-------|
| Added `_has_mac_agent` flag | Line 135-136 | 1 |
| Added `_has_waba` flag | Line 138-139 | 1 |
| Replaced `settings.slack_app_enabled` → `_has_slack` | Line 803 | 1 |
| Replaced `settings.mac_agent_enabled` → `_has_mac_agent` | Line 811 | 1 |
| Replaced `settings.twilio_enabled` → `_has_twilio_adapter` | Line 819 | 1 |
| Replaced `settings.waba_enabled` → `_has_waba` | Line 827 | 1 |
| Replaced `settings.email_enabled` → `_has_email_adapter` | Line 835 | 1 |

**VERIFICATION:**
- [x] Phase -1 plan was respected
- [x] Phase 0 baseline confirmed
- [x] Phase 1 implementation complete (5 replacements + 2 new flags)
- [x] Phase 2 enforcement verified (zero `settings.` remain)
- [x] Phase 3 guards in place (env-driven flags)
- [x] Phase 4 second pass passed
- [x] Phase 5 sanity sweep passed (syntax OK)

**EXPLICIT DECLARATION:**
"All phases complete. File is ready for VPS deployment. No follow-up required."

---

**To deploy to VPS:**
```bash
scp api/server.py root@157.180.73.53:/opt/l9/api/
# Then on VPS:
docker restart l9-api
```