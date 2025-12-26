## **🧠 GOD-MODE CURSOR PROMPT — L9 Edition**

============================================================================
L9-SPECIFIC CURSOR PROMPT (DETERMINISTIC, LOCKED)
Purpose:
- Fix server.py NameError without breaking architecture
- Use existing feature flag pattern (_has_*)
- Preserve all formatting and structure
- Enforce zero drift from VPS expectations

============================================================================

## ROLE

You are a constrained code fixer operating inside the L9 repository.
You fix the exact problem identified.
You do not redesign patterns.
You do not add new abstractions.
You do not guess what "might be nice."
You implement only what is explicitly required.

---

## MISSION OBJECTIVE

Fix line 797 in /opt/l9/api/server.py:
- PROBLEM: `NameError: name 'settings' is not defined`
- CAUSE: Code uses `settings.slack_app_enabled` and `settings.mac_agent_enabled` 
  but `settings` object is never created
- SOLUTION: Replace ALL `settings.X` references with existing `_has_X` feature flags
- RESULT: App starts without NameError; no new patterns introduced

---

## OPERATING MODE (NON-NEGOTIABLE)

Execution is strictly phased.
Phases must be executed in order.
No phase may be skipped.
No phase may be partially completed.

---

# ============================================================================
PHASE -1 — ANALYSIS & PLANNING
============================================================================

ACTIONS:
1. Open /opt/l9/api/server.py
2. Search for ALL occurrences of `settings.` (should be 2-4 instances)
3. Identify what each `settings.X` reference is checking
4. Map each to the corresponding `_has_X` feature flag already defined above
5. Create a TODO list of exact replacements needed

REQUIRED CHECKLIST:
- [ ] Found all `settings.` references in file
- [ ] Each maps to a valid `_has_*` flag
- [ ] Replacement doesn't break logic
- [ ] No new abstractions needed

SAMPLE FINDINGS:
- Line 797: `if settings.slack_app_enabled:` → Replace with `if _has_slack:`
- Line XXX: `if settings.mac_agent_enabled:` → Need to add `_has_mac_agent` flag first

---

# ============================================================================
PHASE 0 — BASELINE CONFIRMATION
============================================================================

CHECKLIST (ALL MUST PASS):
- [ ] File exists at /opt/l9/api/server.py
- [ ] Current state matches uploaded file (36660 bytes)
- [ ] Line 797 contains `settings.slack_app_enabled` reference
- [ ] Feature flags (_has_slack, etc.) are defined around line 30-150
- [ ] No `settings` class or object is currently defined anywhere
- [ ] Mac agent reference exists (line XXX: `settings.mac_agent_enabled`)

FAIL RULE:
If any checklist item fails, STOP and report actual state.

---

# ============================================================================
PHASE 1 — PRIMARY IMPLEMENTATION
============================================================================

ACTIONS (IN THIS EXACT ORDER):

1. Replace ALL `settings.slack_app_enabled` with `_has_slack`
   - Use find-replace across entire file
   - Preserve surrounding code exactly
   - No contextual changes

2. Replace ALL `settings.mac_agent_enabled` with `_has_mac_agent`
   - Same precision as above

3. Add missing `_has_mac_agent` flag definition
   - Location: Around line 165, after `LOCAL_DEV` definition
   - Exact code:
     ```
     # Optional: Mac Agent API
     _has_mac_agent = os.getenv("MAC_AGENT_ENABLED", "false").lower() == "true"
     ```
   - This follows existing pattern (see _has_slack, _has_research, etc.)

4. Verify NO `settings.` references remain
   - Search should return 0 results
   - Search should be case-sensitive

CHECKLIST:
- [ ] All `settings.slack_app_enabled` → `_has_slack`
- [ ] All `settings.mac_agent_enabled` → `_has_mac_agent`
- [ ] `_has_mac_agent` flag defined at line ~165
- [ ] Zero `settings.` references remain
- [ ] All surrounding code unchanged
- [ ] File structure preserved (imports, classes, functions intact)

FAIL RULE:
Do not proceed until ALL checklist items pass.

---

# ============================================================================
PHASE 2 — ENFORCEMENT (Verify via inspection, NOT execution)
============================================================================

ACTIONS:
1. Review every line you changed (show diff)
2. Confirm each replacement makes logical sense
3. Confirm feature flag is defined before first use
4. Verify indentation and formatting preserved

CHECKLIST:
- [ ] Each replacement is semantically correct
- [ ] Feature flag defined before first use
- [ ] No orphaned `settings` references
- [ ] Code formatting matches file style

FAIL RULE:
If any replacement is questionable, ask for clarification.

---

# ============================================================================
PHASE 3 — SYSTEM GUARDS
============================================================================

ACTIONS:
1. Add a comment documenting the replacement:

Note: Use has* feature flags instead of settings object
Feature flags are initialized from environment variables above
text
- Place at line 797 area (where old settings reference was)

2. Ensure MAC_AGENT_ENABLED can be set via .env
- No code change needed (env var pattern already used elsewhere)
- Just confirm the pattern works

CHECKLIST:
- [ ] Comment explains the pattern
- [ ] Comment is placed near the replaced code
- [ ] _has_mac_agent uses same env var pattern as others

FAIL RULE:
Comments must be clear and non-obvious.

---

# ============================================================================
PHASE 4 — SECOND PASS VALIDATION
============================================================================

ACTIONS:
1. Re-read the entire feature flags section (lines 30-170)
2. Verify `_has_mac_agent` fits the pattern consistently
3. Scan lines around 790-810 for any remaining issues
4. Check that ALL conditional logic still reads correctly

CHECKLIST:
- [ ] Feature flags section is consistent
- [ ] _has_mac_agent defined in right location
- [ ] No orphaned or broken conditionals
- [ ] Code is readable and maintainable

FAIL RULE:
If pattern is inconsistent, fix before proceeding.

---

# ============================================================================
PHASE 5 — FINAL SANITY SWEEP
============================================================================

ACTIONS:
1. Re-read entire file for any remaining `settings` references
2. Verify no new bugs introduced
3. Confirm architecture not changed

CHECKLIST:
- [ ] Zero `settings` references remain
- [ ] All replacements are correct
- [ ] File is ready for VPS deployment

FAIL RULE:
Any remaining issue = incomplete.

---

# ============================================================================
DEFINITION OF DONE
============================================================================

The task is ONLY complete if ALL of these are true:

✓ No `settings.` references remain in file
✓ All `_has_*` flags are properly defined
✓ Indentation and formatting preserved
✓ Feature flag pattern is consistent
✓ Code runs without NameError
✓ No other changes made to the file

---

# ============================================================================
FINAL REPORT (REQUIRED OUTPUT)
============================================================================

After completing all phases, output:

**FILES CHANGED:**
- /opt/l9/api/server.py

**CHANGES MADE:**
- Replaced `settings.slack_app_enabled` with `_has_slack` (count: X occurrences)
- Replaced `settings.mac_agent_enabled` with `_has_mac_agent` (count: X occurrences)
- Added `_has_mac_agent` flag definition at line YYY
- Added explanatory comment at line ZZZ

**VERIFICATION:**
- [ ] Phase -1 plan was respected
- [ ] Phase 0 baseline confirmed
- [ ] Phase 1 implementation complete
- [ ] Phase 2 enforcement verified
- [ ] Phase 3 guards in place
- [ ] Phase 4 second pass passed
- [ ] Phase 5 sanity sweep passed

**EXPLICIT DECLARATION:**
"All phases complete. File is ready for VPS deployment. No follow-up required."
