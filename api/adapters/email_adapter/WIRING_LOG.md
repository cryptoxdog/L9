# Wiring Log: email.adapter

**Wired by:** cursor  
**Date:** 2025-12-18  
**Spec Hash:** SPEC-62d9295fc71f  
**Status:** COMPLETE

## Files Inventory

| # | File | From (Source) | To (Destination) | Action | Details |
|---|------|---------------|------------------|--------|---------|
| 1 | `__init__.py` | `Module Production/.../module.email_adapter/__init__.py` | `api/adapters/email_adapter/__init__.py` | MODIFIED | Added startup guard for env var validation |
| 2 | `config.py` | `Module Production/.../module.email_adapter/config.py` | `api/adapters/email_adapter/config.py` | COPIED | Already correct - no changes needed |
| 3 | `schemas.py` | `Module Production/.../module.email_adapter/schemas.py` | `api/adapters/email_adapter/schemas.py` | COPIED | Already correct - no changes needed |
| 4 | `README.md` | `Module Production/.../module.email_adapter/README.md` | `api/adapters/email_adapter/README.md` | COPIED | Documentation, no wiring needed |
| 5 | `Module-Spec-v2.6-email_adapter.yaml` | `Module Production/.../module.email_adapter/Module-Spec-v2.6-email_adapter.yaml` | `api/adapters/email_adapter/Module-Spec-v2.6-email_adapter.yaml` | COPIED | Spec preserved as-is |
| 6 | `adapters/email_adapter_adapter.py` | `Module Production/.../module.email_adapter/adapters/email_adapter_adapter.py` | `api/adapters/email_adapter/adapters/email_adapter_adapter.py` | COPIED | Prompt forbids modifying adapter logic |
| 7 | `routes/email_adapter.py` | `Module Production/.../module.email_adapter/routes/email_adapter.py` | `api/adapters/email_adapter/routes/email_adapter.py` | MODIFIED | Fixed route prefix `/email/adapter` → `/email`, endpoint `/email/webhook` → `/webhook`, `aios_runtime_client` → `aios_runtime` |
| 8 | `clients/email_adapter_client.py` | `Module Production/.../module.email_adapter/clients/email_adapter_client.py` | `api/adapters/email_adapter/clients/email_adapter_client.py` | COPIED | Already correct - no changes needed |
| 9 | `services/email_adapter_service.py` | `Module Production/.../module.email_adapter/services/email_adapter_service.py` | `api/adapters/email_adapter/services/email_adapter_service.py` | COPIED | Already correct - no changes needed |
| 10 | `tests/conftest.py` | `Module Production/.../module.email_adapter/tests/conftest.py` | `api/adapters/email_adapter/tests/conftest.py` | COPIED | Already correct - no changes needed |
| 11 | `tests/test_email_adapter.py` | `Module Production/.../module.email_adapter/tests/test_email_adapter.py` | `api/adapters/email_adapter/tests/test_email_adapter.py` | MODIFIED | Fixed import path `adapters.` → `api.adapters.email_adapter.adapters.` |
| 12 | `tests/test_email_adapter_integration.py` | `Module Production/.../module.email_adapter/tests/test_email_adapter_integration.py` | `api/adapters/email_adapter/tests/test_email_adapter_integration.py` | MODIFIED | Fixed import path and endpoint URLs |

## External Files Modified

| File | Changes |
|------|---------|
| `api/server.py` | Added conditional import for `email_adapter_router`, `_has_email_adapter` flag, `include_router()` call, feature in root response |
| `env.example` | Added `EMAIL_ADAPTER_ENABLED`, `EMAIL_ADAPTER_SIGNING_SECRET`, `GMAIL_API_KEY`, `EMAIL_ADAPTER_LOG_LEVEL` |

## Routes Registered

| Method | Path | Auth |
|--------|------|------|
| POST | `/email/webhook` | Bearer token |
| GET | `/email/health` | None |

## Environment Variables

**Updated 2025-12-20:** Config updated to use existing `EMAIL_ENABLED` toggle from env.example.

| Variable | Required | In env.example | Notes |
|----------|----------|----------------|-------|
| `EMAIL_ADAPTER_SIGNING_SECRET` | Yes | YES (added) | USER ACTION NEEDED |
| `GMAIL_API_KEY` | Yes | YES (added) | USER ACTION NEEDED |
| `EMAIL_ENABLED` | No | YES (existing) | FIXED: Config now uses existing toggle, not `EMAIL_ADAPTER_ENABLED` |
| `EMAIL_ADAPTER_LOG_LEVEL` | No | No | Optional override |

## Validation Results

- Unit Tests: 7/8 passed
- Integration Tests: 4/4 passed
- Import Test: PASS
- Negative Test (missing env): PASS

## Phase Checklist

- [x] Phase -1: Planning
- [x] Phase 0: Baseline
- [x] Phase 1: Implementation
- [x] Phase 2: Enforcement
- [x] Phase 3: Guards
- [x] Phase 4: Validation
- [x] Phase 5: Final Sweep

## Gaps, Errors & Follow-ups

| Issue | Severity | Status | Action Required |
|-------|----------|--------|-----------------|
| Missing `EMAIL_ADAPTER_SIGNING_SECRET` | BLOCKING | OPEN | User must create/obtain signing secret |
| Missing `GMAIL_API_KEY` | BLOCKING | OPEN | User must obtain from Google Cloud Console |
| Route prefix incorrect in generated code | LOW | FIXED | Changed `/email/adapter/email/webhook` → `/email/webhook` |
| `aios_runtime_client` wrong reference | LOW | FIXED | Changed to `aios_runtime` to match server.py |
| Test imports used wrong paths | LOW | FIXED | Updated to use `api.adapters.email_adapter.` prefix |
| `test_thread_uuid_deterministic` fails | LOW | OPEN (PRE-EXISTING) | Generated test bug - thread key uses email fields not event_id, so different event_ids produce same UUID when email fields empty. Cannot fix per prompt rules. |
| `EMAIL_ENABLED` vs `EMAIL_ADAPTER_ENABLED` | LOW | FIXED | Config updated to use existing `EMAIL_ENABLED` from env.example |

**Blocking Issues:** 2  
**Open Non-blocking:** 2  
**Fixed During Wiring:** 4

## User Actions Required

- [ ] Obtain/create `EMAIL_ADAPTER_SIGNING_SECRET` for webhook signature validation
- [ ] Obtain `GMAIL_API_KEY` from Google Cloud Console
- [ ] Set `EMAIL_ENABLED=true` in `.env.local` when credentials are ready

## Notes

- The generated test `test_thread_uuid_deterministic` has a logic bug: it expects different event_ids to produce different thread UUIDs, but the thread key is derived from `['email_from', 'email_subject', 'email_thread_id']` per the spec. When these fields are empty, all requests produce the same UUID. This is a spec/generator issue, not a wiring issue.
- Config updated to use existing `EMAIL_ENABLED` toggle from env.example (no new toggle needed).

