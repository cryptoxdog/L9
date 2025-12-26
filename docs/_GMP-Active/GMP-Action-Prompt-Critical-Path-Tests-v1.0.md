============================================================================
GOD-MODE CURSOR PROMPT — L9 CRITICAL PATH TEST COVERAGE V1.0 (DETERMINISTIC, LOCKED)
============================================================================

PURPOSE:
• Expand Critical Path Coverage from 4/10 to 8/10
• Add unit tests for API endpoints (production-facing critical path)
• Add unit tests for all 7 orchestrators (business logic critical path)
• Use TestClient for API tests, mocks for orchestrators
• Zero external dependencies - all mocked

============================================================================

ROLE
You are a constrained execution agent operating inside the L9 Secure AI OS repository at `/Users/ib-mac/Projects/L9/`.  
You create test files for CRITICAL PATH components only.  
Critical Path = API endpoints + Orchestrators.  
You use TestClient from FastAPI with mocked database initialization.  
You use existing mock patterns from `tests/core/agents/test_executor.py`.  
You do not touch production code.  
You do not freelance.

============================================================================

MODIFICATION LOCK — ABSOLUTE

❌ YOU MAY NOT:
• Modify any production code
• Create tests that require running services
• Skip mocking database/Redis/Neo4j connections
• Create integration tests (unit tests only)
• Add new dependencies
• Modify docker-compose.yml or .env files

✅ YOU MAY ONLY:
• Create new test files under `/Users/ib-mac/Projects/L9/tests/`
• Use `unittest.mock.patch` to mock database connections
• Use `fastapi.testclient.TestClient` for API tests
• Use existing mock classes from test infrastructure
• Create `__init__.py` files for new test directories

============================================================================

L9-SPECIFIC OPERATING CONSTRAINTS (NON-NEGOTIABLE)

• All test files under `/Users/ib-mac/Projects/L9/tests/`
• API tests MUST patch `api.db.init_db` before importing server
• Orchestrator tests MUST mock all external service calls
• Use `pytest.mark.asyncio` for async tests
• Follow naming: `test_<module>.py`
• Each test file must be independently runnable

============================================================================

STRUCTURED OUTPUT REQUIREMENTS

Report File:
```text
Path: /Users/ib-mac/Projects/L9/reports/critical-path-tests-v1.0.md
```

Report Structure:
1. Execution Summary
2. Files Created (path, line count, test count)
3. Critical Path Coverage Delta (before/after)
4. Test Run Results
5. TODO INDEX HASH verification

============================================================================

PHASE 0 — PATTERN EXTRACTION

PURPOSE:
• Extract testing patterns from existing well-tested modules
• Identify how to mock database connections for API tests
• Catalog orchestrator interfaces for mocking

ACTIONS:
• Read `/Users/ib-mac/Projects/L9/tests/core/agents/test_executor.py` lines 1-250
• Read `/Users/ib-mac/Projects/L9/api/server.py` lines 1-50 (understand init pattern)
• Read `/Users/ib-mac/Projects/L9/api/db.py` (understand what to mock)
• Read one orchestrator: `/Users/ib-mac/Projects/L9/orchestrators/action_tool/orchestrator.py`

✅ PHASE 0 DEFINITION OF DONE:
- [ ] TestClient pattern understood
- [ ] db.init_db mocking pattern identified
- [ ] Orchestrator interface patterns cataloged
- [ ] Mock patterns from test_executor.py extracted

============================================================================

PHASE 1 — API CRITICAL PATH TESTS

PURPOSE:
• Create tests for `/health`, `/`, `/docs`, `/openapi.json`
• Create tests for `/os/*` routes
• Create tests for `/agent/*` routes
• Create tests for `/memory/*` routes
• All using TestClient with mocked DB

ACTIONS:
• Create `/Users/ib-mac/Projects/L9/tests/api/__init__.py`
• Create `/Users/ib-mac/Projects/L9/tests/api/test_health_routes.py`
• Create `/Users/ib-mac/Projects/L9/tests/api/test_os_routes.py`
• Create `/Users/ib-mac/Projects/L9/tests/api/test_agent_routes.py`
• Create `/Users/ib-mac/Projects/L9/tests/api/test_memory_routes.py`

✅ PHASE 1 DEFINITION OF DONE:
- [ ] `tests/api/__init__.py` exists
- [ ] `tests/api/test_health_routes.py` has 4+ tests
- [ ] `tests/api/test_os_routes.py` has 3+ tests
- [ ] `tests/api/test_agent_routes.py` has 3+ tests
- [ ] `tests/api/test_memory_routes.py` has 3+ tests
- [ ] All API tests pass: `pytest tests/api/ -v`

============================================================================

PHASE 2 — ORCHESTRATOR CRITICAL PATH TESTS

PURPOSE:
• Create tests for all 7 orchestrator modules
• Test initialization, validation, and core methods
• Mock all external dependencies

ACTIONS:
• Create tests for each orchestrator:
  - action_tool
  - memory
  - meta
  - world_model
  - reasoning
  - research_swarm
  - evolution

✅ PHASE 2 DEFINITION OF DONE:
- [ ] `tests/orchestrators/test_action_tool.py` created
- [ ] `tests/orchestrators/test_memory_orchestrator.py` created
- [ ] `tests/orchestrators/test_meta_orchestrator.py` created
- [ ] `tests/orchestrators/test_world_model_orchestrator.py` created
- [ ] `tests/orchestrators/test_reasoning_orchestrator.py` created
- [ ] `tests/orchestrators/test_research_swarm.py` created
- [ ] `tests/orchestrators/test_evolution_orchestrator.py` created
- [ ] All orchestrator tests pass: `pytest tests/orchestrators/ -v`

============================================================================

PHASE 3 — AUTH CRITICAL PATH TESTS

PURPOSE:
• Test authentication middleware
• Test API key validation
• Test authorization flows

ACTIONS:
• Create `/Users/ib-mac/Projects/L9/tests/api/test_auth.py`

✅ PHASE 3 DEFINITION OF DONE:
- [ ] `tests/api/test_auth.py` created with 5+ tests
- [ ] Token validation tested
- [ ] Missing auth header tested
- [ ] Invalid token tested
- [ ] All auth tests pass

============================================================================

PHASE 4 — WEBHOOK CRITICAL PATH TESTS

PURPOSE:
• Test Slack webhook endpoint
• Test Mac agent webhook endpoint
• All with mocked external calls

ACTIONS:
• Create `/Users/ib-mac/Projects/L9/tests/api/test_webhook_slack.py`
• Create `/Users/ib-mac/Projects/L9/tests/api/test_webhook_mac_agent.py`

✅ PHASE 4 DEFINITION OF DONE:
- [ ] `tests/api/test_webhook_slack.py` created
- [ ] `tests/api/test_webhook_mac_agent.py` created
- [ ] Webhook signature verification tested
- [ ] All webhook tests pass

============================================================================

PHASE 5 — INTEGRATION VERIFICATION

PURPOSE:
• Run all new tests together
• Verify no conflicts with existing tests
• Calculate coverage delta

ACTIONS:
• Run `pytest tests/api/ tests/orchestrators/ -v --tb=short`
• Run full suite: `pytest tests/ -v --tb=short -x` (stop on first failure)
• Count new tests added
• Calculate critical path coverage improvement

✅ PHASE 5 DEFINITION OF DONE:
- [ ] All new tests pass independently
- [ ] All new tests pass with full suite
- [ ] No regressions in existing tests
- [ ] Coverage delta calculated

============================================================================

PHASE 6 — REPORT GENERATION

PURPOSE:
• Generate execution report
• Document all created files
• Verify TODO completion

ACTIONS:
• Write report to `/Users/ib-mac/Projects/L9/reports/critical-path-tests-v1.0.md`
• List all files created with line counts
• Document test counts per module
• Calculate final critical path coverage score

✅ PHASE 6 DEFINITION OF DONE:
- [ ] Report generated at specified path
- [ ] All files documented
- [ ] Coverage delta: 4/10 → 8/10 (target)
- [ ] All TODOs marked complete

============================================================================

FINAL DEFINITION OF DONE (TOTAL, NON-NEGOTIABLE)

✓ All API endpoint tests created (health, os, agent, memory, auth, webhooks)
✓ All 7 orchestrator tests created
✓ All tests use mocks (no external dependencies)
✓ All tests pass independently
✓ Full test suite passes
✓ Critical Path Coverage improved to 8/10
✓ Report generated
✓ No production code modified

============================================================================

FINAL DECLARATION

> GMP execution complete. Critical path tests created. All phases verified.
> Report stored at `/Users/ib-mac/Projects/L9/reports/critical-path-tests-v1.0.md`.
> Critical Path Coverage: 4/10 → 8/10.
> No further modifications needed.

============================================================================

SPECIFIC REQUIREMENTS — CRITICAL PATH TODO PLAN (LOCKED)

## TODO INDEX HASH: CP-v1.0-2024-DEC25

---

### PHASE 1: API ENDPOINT TESTS

**[CP-v1.0-001]**
- File: `/Users/ib-mac/Projects/L9/tests/api/__init__.py`
- Action: Create
- Target: New package init
- Expected: Empty __init__.py
- Imports: NONE

**[CP-v1.0-002]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_health_routes.py`
- Action: Create
- Target: New test file
- Expected: Tests for core health endpoints with mocked DB
- Imports: `pytest`, `unittest.mock.patch`, `fastapi.testclient.TestClient`
- Implementation:
```python
"""
API Health Routes Tests
Tests critical health endpoints with mocked database.
"""
import pytest
from unittest.mock import patch, MagicMock

# Mock db.init_db BEFORE importing server
with patch('api.db.init_db'):
    from api.server import app

from fastapi.testclient import TestClient

@pytest.fixture
def client():
    """Test client with mocked DB."""
    return TestClient(app)

class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_returns_200(self, client):
        """GET /health returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_returns_status_ok(self, client):
        """GET /health returns status ok."""
        response = client.get("/health")
        assert response.json().get("status") in ["ok", "healthy"]
    
    def test_root_returns_200(self, client):
        """GET / returns 200."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_docs_accessible(self, client):
        """GET /docs returns 200."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_json_accessible(self, client):
        """GET /openapi.json returns valid JSON."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()
```
- Tests: 5

**[CP-v1.0-003]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_os_routes.py`
- Action: Create
- Target: New test file
- Expected: Tests for /os/* endpoints
- Imports: `pytest`, `unittest.mock.patch`, `fastapi.testclient.TestClient`
- Implementation:
```python
"""
OS Routes Tests
Tests /os/* endpoints with mocked dependencies.
"""
import pytest
from unittest.mock import patch, MagicMock

with patch('api.db.init_db'):
    from api.server import app

from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

class TestOSRoutes:
    """Test OS endpoints."""
    
    def test_os_health_returns_200(self, client):
        """GET /os/health returns 200."""
        response = client.get("/os/health")
        assert response.status_code == 200
    
    def test_os_status_returns_200(self, client):
        """GET /os/status returns 200."""
        response = client.get("/os/status")
        assert response.status_code == 200
    
    def test_os_status_has_version(self, client):
        """GET /os/status includes version."""
        response = client.get("/os/status")
        data = response.json()
        assert "version" in data or "status" in data
```
- Tests: 3

**[CP-v1.0-004]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_agent_routes.py`
- Action: Create
- Target: New test file
- Expected: Tests for /agent/* endpoints
- Imports: `pytest`, `unittest.mock.patch`, `fastapi.testclient.TestClient`
- Tests Required:
  - `test_agent_health_returns_200`
  - `test_agent_status_returns_200`
  - `test_agent_execute_requires_body`
- Tests: 3

**[CP-v1.0-005]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_memory_routes.py`
- Action: Create
- Target: New test file
- Expected: Tests for /memory/* endpoints
- Imports: `pytest`, `unittest.mock.patch`, `fastapi.testclient.TestClient`
- Tests Required:
  - `test_memory_stats_returns_200`
  - `test_memory_health_returns_200`
  - `test_memory_test_endpoint`
- Tests: 3

**[CP-v1.0-006]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_auth.py`
- Action: Create
- Target: New test file
- Expected: Tests for authentication
- Imports: `pytest`, `api.auth`
- Tests Required:
  - `test_valid_api_key_accepted`
  - `test_invalid_api_key_rejected`
  - `test_missing_auth_returns_401`
  - `test_malformed_bearer_rejected`
  - `test_empty_token_rejected`
- Tests: 5

---

### PHASE 2: ORCHESTRATOR TESTS

**[CP-v1.0-007]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_action_tool.py`
- Action: Create
- Target: New test file
- Expected: Tests for action_tool orchestrator
- Imports: `pytest`, `orchestrators.action_tool.orchestrator`, `unittest.mock`
- Implementation:
```python
"""
Action Tool Orchestrator Tests
"""
import pytest
from unittest.mock import MagicMock, AsyncMock

class TestActionToolOrchestrator:
    """Test action tool orchestrator."""
    
    def test_import_orchestrator(self):
        """Orchestrator module imports without error."""
        from orchestrators.action_tool import orchestrator
        assert orchestrator is not None
    
    def test_interface_exists(self):
        """Interface module exists."""
        from orchestrators.action_tool import interface
        assert interface is not None
    
    def test_validator_exists(self):
        """Validator module exists."""
        from orchestrators.action_tool import validator
        assert validator is not None
```
- Tests: 3

**[CP-v1.0-008]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_memory_orchestrator.py`
- Action: Create
- Target: New test file
- Expected: Tests for memory orchestrator
- Imports: `pytest`, `orchestrators.memory.orchestrator`
- Tests Required:
  - `test_import_orchestrator`
  - `test_interface_exists`
  - `test_housekeeping_exists`
- Tests: 3

**[CP-v1.0-009]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_meta_orchestrator.py`
- Action: Create
- Target: New test file
- Expected: Tests for meta orchestrator
- Imports: `pytest`, `orchestrators.meta.orchestrator`
- Tests Required:
  - `test_import_orchestrator`
  - `test_adapter_exists`
  - `test_interface_exists`
- Tests: 3

**[CP-v1.0-010]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_world_model_orchestrator.py`
- Action: Create
- Target: New test file
- Expected: Tests for world_model orchestrator
- Imports: `pytest`, `orchestrators.world_model.orchestrator`
- Tests Required:
  - `test_import_orchestrator`
  - `test_scheduler_exists`
  - `test_interface_exists`
- Tests: 3

**[CP-v1.0-011]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_reasoning_orchestrator.py`
- Action: Create
- Target: New test file
- Expected: Tests for reasoning orchestrator
- Imports: `pytest`, `orchestrators.reasoning.orchestrator`
- Tests Required:
  - `test_import_orchestrator`
  - `test_interface_exists`
- Tests: 2

**[CP-v1.0-012]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_research_swarm.py`
- Action: Create
- Target: New test file
- Expected: Tests for research_swarm orchestrator
- Imports: `pytest`, `orchestrators.research_swarm.orchestrator`
- Tests Required:
  - `test_import_orchestrator`
  - `test_interface_exists`
- Tests: 2

**[CP-v1.0-013]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_evolution_orchestrator.py`
- Action: Create
- Target: New test file
- Expected: Tests for evolution orchestrator
- Imports: `pytest`, `orchestrators.evolution.orchestrator`
- Tests Required:
  - `test_import_orchestrator`
  - `test_interface_exists`
- Tests: 2

---

### PHASE 4: WEBHOOK TESTS

**[CP-v1.0-014]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_webhook_slack.py`
- Action: Create
- Target: New test file
- Expected: Tests for Slack webhook with mocked signature verification
- Imports: `pytest`, `unittest.mock`, `api.webhook_slack`
- Tests Required:
  - `test_slack_challenge_response`
  - `test_invalid_signature_rejected`
  - `test_valid_event_processed`
- Tests: 3

**[CP-v1.0-015]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_webhook_mac_agent.py`
- Action: Create
- Target: New test file
- Expected: Tests for Mac agent webhook
- Imports: `pytest`, `unittest.mock`
- Tests Required:
  - `test_webhook_accepts_valid_payload`
  - `test_webhook_rejects_invalid_payload`
- Tests: 2

---

## EXECUTION ORDER

1. Phase 0: Read patterns (no files created)
2. Phase 1: Create 6 files ([CP-v1.0-001] through [CP-v1.0-006])
3. Phase 2: Create 7 files ([CP-v1.0-007] through [CP-v1.0-013])
4. Phase 4: Create 2 files ([CP-v1.0-014] through [CP-v1.0-015])
5. Phase 5: Run all tests, verify
6. Phase 6: Generate report

---

## SUMMARY

| Category | Files | Tests |
|----------|-------|-------|
| API Health/Core | 4 | 14 |
| API Auth | 1 | 5 |
| API Webhooks | 2 | 5 |
| Orchestrators | 7 | 18 |
| **TOTAL** | **15** | **42** |

**Expected Outcome:**
- Critical Path Coverage: 4/10 → 8/10
- New test files: 15
- New tests: ~42

============================================================================

END OF GMP ACTION PROMPT

