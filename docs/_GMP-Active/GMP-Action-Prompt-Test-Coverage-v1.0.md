============================================================================
GOD-MODE CURSOR PROMPT — L9 TEST COVERAGE EXPANSION V1.0 (DETERMINISTIC, LOCKED)
============================================================================

PURPOSE:
• Expand test coverage from 3/10 to 7/10 across L9 modules
• Add unit tests for 9 critical modules currently at 0% coverage
• Follow existing test patterns from memory/, ir_engine/, runtime/
• Ensure all new tests use contract-grade mocks
• Achieve minimum 1 test file per critical module

============================================================================

ROLE
You are a constrained execution agent operating inside the L9 Secure AI OS repository at `/Users/ib-mac/Projects/L9/`.  
You create test files that follow the existing test patterns.  
You do not redesign the test framework.  
You do not invent test requirements beyond what modules expose.  
You use the existing mock infrastructure from `tests/core/agents/test_executor.py` and `tests/mocks/`.  
You do not freelance.  
You output only working test files with proper imports and assertions.

============================================================================

MODIFICATION LOCK — ABSOLUTE

❌ YOU MAY NOT:
• Modify production code to make tests pass
• Create tests that require external services (DB, Redis, APIs)
• Skip the existing mock patterns
• Create integration tests disguised as unit tests
• Add dependencies to requirements.txt
• Modify conftest.py without explicit TODO

✅ YOU MAY ONLY:
• Create new test files under `/Users/ib-mac/Projects/L9/tests/`
• Use existing mocks from `tests/mocks/` and `tests/core/agents/test_executor.py`
• Import modules and test their public interfaces
• Use pytest fixtures and async patterns from existing tests
• Add new mock classes following existing patterns

============================================================================

L9-SPECIFIC OPERATING CONSTRAINTS (NON-NEGOTIABLE)

• All test files must be under `/Users/ib-mac/Projects/L9/tests/`
• Test file naming: `test_<module_name>.py`
• Test directory structure mirrors source: `tests/api/`, `tests/orchestrators/`, etc.
• Use `pytest.mark.asyncio` for async tests
• Use `MockSubstrateService` pattern from `tests/core/agents/test_executor.py`
• Use `TestClient` from FastAPI for API route tests
• Do not connect to real databases - mock all DB calls
• Do not make HTTP calls - mock httpx/requests

============================================================================

STRUCTURED OUTPUT REQUIREMENTS

Report File:
```text
Path: /Users/ib-mac/Projects/L9/reports/test-coverage-expansion-v1.0.md
```

Report Structure:
1. Execution Summary (tests created, coverage delta)
2. Files Created (with line counts)
3. Test Count by Module
4. Remaining Gaps
5. TODO INDEX HASH verification

============================================================================

PHASE 0 — RECONNAISSANCE & PATTERN EXTRACTION

PURPOSE:
• Analyze existing test patterns in well-covered modules
• Extract mock patterns, fixture patterns, assertion patterns
• Identify reusable test infrastructure

ACTIONS:
• Read `/Users/ib-mac/Projects/L9/tests/core/agents/test_executor.py` for mock patterns
• Read `/Users/ib-mac/Projects/L9/tests/memory/test_memory_ingestion.py` for async patterns
• Read `/Users/ib-mac/Projects/L9/tests/conftest.py` for shared fixtures
• Catalog reusable mocks: MockAIOSRuntime, MockToolRegistry, MockSubstrateService, MockAgentRegistry

✅ PHASE 0 DEFINITION OF DONE:
- [ ] Existing test patterns cataloged
- [ ] Mock classes identified and documented
- [ ] Fixture patterns understood
- [ ] Async test patterns extracted

❌ FAIL RULE:
If existing tests cannot be read, STOP and report.

============================================================================

PHASE 1 — CRITICAL GAP TESTS (P0: api/, orchestrators/)

PURPOSE:
• Create foundational tests for highest-risk modules
• Establish test patterns for API and orchestrator testing

ACTIONS:
• Create test directories: `tests/api/`, `tests/orchestrators/`
• Create API route tests using TestClient
• Create orchestrator unit tests using mocks

✅ PHASE 1 DEFINITION OF DONE:
- [ ] `tests/api/__init__.py` created
- [ ] `tests/api/test_server_health.py` created (health endpoints)
- [ ] `tests/api/test_auth.py` created (auth module)
- [ ] `tests/orchestrators/__init__.py` created
- [ ] `tests/orchestrators/test_action_tool_orchestrator.py` created
- [ ] All tests pass with `pytest tests/api/ tests/orchestrators/ -v`

============================================================================

PHASE 2 — AGENT & EMAIL TESTS (P1: agents/, email_agent/)

PURPOSE:
• Add tests for agent implementations
• Add tests for email agent (with mocked Gmail API)

ACTIONS:
• Create `tests/agents/` directory structure
• Create base agent tests
• Create email agent tests with mocked credentials

✅ PHASE 2 DEFINITION OF DONE:
- [ ] `tests/agents/__init__.py` created
- [ ] `tests/agents/test_base_agent.py` created
- [ ] `tests/agents/test_architect_agents.py` created
- [ ] `tests/email_agent/__init__.py` created
- [ ] `tests/email_agent/test_email_router.py` created
- [ ] `tests/email_agent/test_email_triage.py` created
- [ ] All tests pass

============================================================================

PHASE 3 — OS & MAC AGENT TESTS (P2: os/, mac_agent/)

PURPOSE:
• Add tests for OS layer
• Add tests for Mac agent (with mocked WebSocket)

ACTIONS:
• Create `tests/os/` directory
• Create `tests/mac_agent/` directory
• Test controller, bootstrap, executor with mocks

✅ PHASE 3 DEFINITION OF DONE:
- [ ] `tests/os/__init__.py` created
- [ ] `tests/os/test_controller.py` created
- [ ] `tests/os/test_bootstrap.py` created
- [ ] `tests/mac_agent/__init__.py` created
- [ ] `tests/mac_agent/test_executor.py` created
- [ ] All tests pass

============================================================================

PHASE 4 — REMAINING MODULES (P3: collaborative_cells/, simulation/, clients/)

PURPOSE:
• Complete coverage expansion for remaining modules
• Ensure all critical modules have at least 1 test file

ACTIONS:
• Create tests for collaborative_cells
• Create tests for simulation engine
• Create tests for clients

✅ PHASE 4 DEFINITION OF DONE:
- [ ] `tests/collaborative_cells/test_base_cell.py` created
- [ ] `tests/simulation/test_simulation_engine.py` created
- [ ] `tests/clients/test_memory_client.py` created
- [ ] All tests pass

============================================================================

PHASE 5 — CORE MODULE EXPANSION (Partial gaps in core/)

PURPOSE:
• Expand core module coverage beyond executor and governance
• Add tests for aios, tools, security, boundary

ACTIONS:
• Add tests for `core/aios/runtime.py`
• Add tests for `core/tools/tool_graph.py`
• Add tests for `core/security/permission_graph.py`

✅ PHASE 5 DEFINITION OF DONE:
- [ ] `tests/core/aios/test_runtime.py` created
- [ ] `tests/core/tools/test_tool_graph.py` created
- [ ] `tests/core/security/test_permission_graph.py` created
- [ ] All tests pass

============================================================================

PHASE 6 — VERIFICATION & REPORT

PURPOSE:
• Run full test suite
• Calculate coverage delta
• Generate final report

ACTIONS:
• Run `pytest tests/ -v --tb=short`
• Count new test files created
• Calculate new coverage percentage
• Write report to `/Users/ib-mac/Projects/L9/reports/test-coverage-expansion-v1.0.md`

✅ PHASE 6 DEFINITION OF DONE:
- [ ] Full test suite passes (excluding known infrastructure tests)
- [ ] Report generated with all sections
- [ ] Coverage improved from 3/10 to minimum 6/10
- [ ] All TODO items marked complete

============================================================================

FINAL DEFINITION OF DONE (TOTAL, NON-NEGOTIABLE)

✓ All test directories created with __init__.py
✓ Minimum 15 new test files created
✓ All new tests use existing mock patterns
✓ All new tests pass independently
✓ Full test suite passes (excluding infrastructure tests)
✓ Coverage improved to 6/10 or higher
✓ Report generated at `/Users/ib-mac/Projects/L9/reports/test-coverage-expansion-v1.0.md`
✓ No production code modified
✓ No new dependencies added

============================================================================

FINAL DECLARATION

> GMP execution complete. Test coverage expanded. All phases verified.
> Report stored at `/Users/ib-mac/Projects/L9/reports/test-coverage-expansion-v1.0.md`.
> No further modifications needed.

============================================================================

SPECIFIC REQUIREMENTS — TEST COVERAGE TODO PLAN (LOCKED)

## TODO INDEX HASH: TC-v1.0-2024-DEC25

---

### PHASE 1: CRITICAL GAPS (api/, orchestrators/)

**[TC-v1.0-001]**
- File: `/Users/ib-mac/Projects/L9/tests/api/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py for test package
- Imports: NONE

**[TC-v1.0-002]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_server_health.py`
- Action: Create
- Target: New test file
- Expected: Tests for `/health`, `/`, `/docs` endpoints using TestClient
- Imports: `pytest`, `fastapi.testclient.TestClient`
- Pattern: Use TestClient with mocked db.init_db()
- Tests Required:
  - `test_health_endpoint_returns_200`
  - `test_root_endpoint_returns_info`
  - `test_docs_endpoint_accessible`

**[TC-v1.0-003]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_auth.py`
- Action: Create
- Target: New test file
- Expected: Tests for auth module token validation
- Imports: `pytest`, `api.auth`
- Tests Required:
  - `test_valid_api_key_passes`
  - `test_invalid_api_key_fails`
  - `test_missing_auth_header_fails`

**[TC-v1.0-004]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py for test package
- Imports: NONE

**[TC-v1.0-005]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_action_tool_orchestrator.py`
- Action: Create
- Target: New test file
- Expected: Tests for action_tool orchestrator
- Imports: `pytest`, `orchestrators.action_tool.orchestrator`
- Tests Required:
  - `test_orchestrator_initialization`
  - `test_validate_action_request`
  - `test_execute_action_with_mock`

---

### PHASE 2: AGENTS & EMAIL (agents/, email_agent/)

**[TC-v1.0-006]**
- File: `/Users/ib-mac/Projects/L9/tests/agents/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py
- Imports: NONE

**[TC-v1.0-007]**
- File: `/Users/ib-mac/Projects/L9/tests/agents/test_base_agent.py`
- Action: Create
- Target: New test file
- Expected: Tests for base agent class
- Imports: `pytest`, `agents.base_agent`
- Tests Required:
  - `test_base_agent_instantiation`
  - `test_base_agent_has_required_methods`

**[TC-v1.0-008]**
- File: `/Users/ib-mac/Projects/L9/tests/email_agent/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py
- Imports: NONE

**[TC-v1.0-009]**
- File: `/Users/ib-mac/Projects/L9/tests/email_agent/test_email_router.py`
- Action: Create
- Target: New test file
- Expected: Tests for email routing logic
- Imports: `pytest`, `email_agent.router`
- Tests Required:
  - `test_route_email_to_correct_handler`
  - `test_unknown_sender_handling`

**[TC-v1.0-010]**
- File: `/Users/ib-mac/Projects/L9/tests/email_agent/test_email_triage.py`
- Action: Create
- Target: New test file
- Expected: Tests for email triage classification
- Imports: `pytest`, `email_agent.triage`
- Tests Required:
  - `test_triage_classification`
  - `test_priority_assignment`

---

### PHASE 3: OS & MAC AGENT (os/, mac_agent/)

**[TC-v1.0-011]**
- File: `/Users/ib-mac/Projects/L9/tests/os/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py
- Imports: NONE

**[TC-v1.0-012]**
- File: `/Users/ib-mac/Projects/L9/tests/os/test_controller.py`
- Action: Create
- Target: New test file
- Expected: Tests for OS controller
- Imports: `pytest`, `os.controller`
- Tests Required:
  - `test_controller_initialization`
  - `test_controller_start_stop`

**[TC-v1.0-013]**
- File: `/Users/ib-mac/Projects/L9/tests/mac_agent/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py
- Imports: NONE

**[TC-v1.0-014]**
- File: `/Users/ib-mac/Projects/L9/tests/mac_agent/test_executor.py`
- Action: Create
- Target: New test file
- Expected: Tests for mac agent executor with mocked subprocess
- Imports: `pytest`, `mac_agent.executor`, `unittest.mock`
- Tests Required:
  - `test_executor_runs_command`
  - `test_executor_handles_timeout`
  - `test_executor_captures_output`

---

### PHASE 4: REMAINING MODULES

**[TC-v1.0-015]**
- File: `/Users/ib-mac/Projects/L9/tests/collaborative_cells/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py
- Imports: NONE

**[TC-v1.0-016]**
- File: `/Users/ib-mac/Projects/L9/tests/collaborative_cells/test_base_cell.py`
- Action: Create
- Target: New test file
- Expected: Tests for base cell class
- Imports: `pytest`, `collaborative_cells.base_cell`
- Tests Required:
  - `test_base_cell_initialization`
  - `test_cell_state_management`

**[TC-v1.0-017]**
- File: `/Users/ib-mac/Projects/L9/tests/simulation/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py
- Imports: NONE

**[TC-v1.0-018]**
- File: `/Users/ib-mac/Projects/L9/tests/simulation/test_simulation_engine.py`
- Action: Create
- Target: New test file
- Expected: Tests for simulation engine
- Imports: `pytest`, `simulation.simulation_engine`
- Tests Required:
  - `test_engine_initialization`
  - `test_run_simulation_basic`

**[TC-v1.0-019]**
- File: `/Users/ib-mac/Projects/L9/tests/clients/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py
- Imports: NONE

**[TC-v1.0-020]**
- File: `/Users/ib-mac/Projects/L9/tests/clients/test_memory_client.py`
- Action: Create
- Target: New test file
- Expected: Tests for memory client with mocked HTTP
- Imports: `pytest`, `clients.memory_client`, `unittest.mock`
- Tests Required:
  - `test_client_initialization`
  - `test_write_packet_mock`
  - `test_search_packets_mock`

---

### PHASE 5: CORE EXPANSION

**[TC-v1.0-021]**
- File: `/Users/ib-mac/Projects/L9/tests/core/aios/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py
- Imports: NONE

**[TC-v1.0-022]**
- File: `/Users/ib-mac/Projects/L9/tests/core/aios/test_runtime.py`
- Action: Create
- Target: New test file
- Expected: Tests for AIOS runtime
- Imports: `pytest`, `core.aios.runtime`
- Tests Required:
  - `test_runtime_initialization`
  - `test_execute_reasoning_mock`

**[TC-v1.0-023]**
- File: `/Users/ib-mac/Projects/L9/tests/core/tools/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py
- Imports: NONE

**[TC-v1.0-024]**
- File: `/Users/ib-mac/Projects/L9/tests/core/tools/test_tool_graph.py`
- Action: Create
- Target: New test file
- Expected: Tests for tool graph (with mocked Neo4j)
- Imports: `pytest`, `core.tools.tool_graph`
- Tests Required:
  - `test_tool_definition_creation`
  - `test_register_tool_mock`

**[TC-v1.0-025]**
- File: `/Users/ib-mac/Projects/L9/tests/core/security/__init__.py`
- Action: Create
- Target: New file
- Expected: Empty __init__.py
- Imports: NONE

**[TC-v1.0-026]**
- File: `/Users/ib-mac/Projects/L9/tests/core/security/test_permission_graph.py`
- Action: Create
- Target: New test file
- Expected: Tests for permission graph
- Imports: `pytest`, `core.security.permission_graph`
- Tests Required:
  - `test_permission_check`
  - `test_grant_permission`

---

## EXECUTION ORDER

1. Phase 0: Read existing patterns (no file changes)
2. Phase 1: Create 5 files ([TC-v1.0-001] through [TC-v1.0-005])
3. Phase 2: Create 5 files ([TC-v1.0-006] through [TC-v1.0-010])
4. Phase 3: Create 4 files ([TC-v1.0-011] through [TC-v1.0-014])
5. Phase 4: Create 6 files ([TC-v1.0-015] through [TC-v1.0-020])
6. Phase 5: Create 6 files ([TC-v1.0-021] through [TC-v1.0-026])
7. Phase 6: Run tests, generate report

**TOTAL: 26 new files (13 __init__.py + 13 test files)**

============================================================================

END OF GMP ACTION PROMPT

