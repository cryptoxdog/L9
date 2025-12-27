---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

## **GMP-10: GMP-L.recursive-self-testing-and-validation**

You are C. You are not designing new test frameworks. You are enabling a test agent to automatically write unit + integration tests for L's proposals, execute them in a sandbox, and report results before Igor approves.

### OBJECTIVE (LOCKED)

Ensure that:
1. When L proposes a high-risk change (GMP, code), a **test agent** automatically generates unit + integration tests.
2. Tests execute in an isolated environment (separate DB, Redis, etc.).
3. Test results are logged and passed to Igor for approval decision.
4. L learns from test failures and refines proposals.

### SCOPE (LOCKED)

You MAY modify:
- New file: `core/agents/test_agent.py` – test generation and execution logic.
- New file: `core/testing/test_generator.py` – generate tests from code proposals.
- New file: `core/testing/test_executor.py` – run tests in sandbox.
- `core/agents/executor.py` – spawn test agent for high-risk proposals.
- `core/agents/registry.py` – register test agent.
- `docker-compose.yml` – add test containers (isolated DB, Redis for testing).

You MAY NOT:
- Modify core testing framework (pytest).
- Change approval gates.

### TODO LIST (BY ID)

**T1 – Test agent registration**
- File: `core/agents/registry.py`
- Add `AgentConfig` for test agent (minimal, focused on test generation and execution).

**T2 – Test generation from proposals**
- File: `core/testing/test_generator.py` (new)
- Implement:
  - `generate_unit_tests(code_proposal) -> List[str]` (returns Python test functions).
  - `generate_integration_tests(code_proposal, dependencies) -> List[str]`.
- Uses code analysis or LLM prompting to generate tests.
- Covers: happy path, edge cases, error handling.

**T3 – Test executor in sandbox**
- File: `core/testing/test_executor.py` (new)
- Implement:
  - `async def run_tests_in_sandbox(test_code, env_config) -> TestResults`
  - Spawns isolated environment (Docker container or tmpdir).
  - Runs pytest with coverage tracking.
  - Captures stdout, stderr, coverage percentage.
  - Returns `TestResults` (dict of test_name → result).

**T4 – Test agent spawning**
- File: `core/agents/executor.py`, in `dispatch_tool_call()` for high-risk tools
- When gmprun or gitcommit called, spawn test agent as sibling task.
- Test agent:
  - Receives code proposal from L.
  - Calls `generate_unit_tests()` and `generate_integration_tests()`.
  - Calls `run_tests_in_sandbox()`.
  - Writes results to memory segment `test_results`.

**T5 – Test results in memory**
- File: `core/memory/runtime.py`, segment definition
- Add `test_results` segment for test run outputs.
- Structure: `test_run_id`, `parent_task_id`, `tests_generated`, `tests_passed`, `tests_failed`, `coverage_percent`, `timestamp`.

**T6 – L's adaptation from test failures**
- File: `core/agents/adaptive_prompting.py`, extend
- If test agent reports failures, retrieve from memory.
- Generate adaptive prompt for L: "Prior proposal had X test failures related to Y. Ensure new proposal addresses these."
- L refines proposal.

**T7 – Test results in approval decision**
- File: `core/governance/approvals.py`, in `approvetask()`
- Check for linked test results in memory.
- Include test summary in approval request to Igor: "Proposal has N tests, M passed, K failed. Coverage: X%."

**T8 – Docker Compose test containers**
- File: `docker-compose.yml`
- Add service:
  - `test-db` (PostgreSQL with separate schema for tests).
  - `test-redis` (Redis with separate namespace).
  - `test-runner` (optional: dedicated container for test execution).

**T9 – Integration test**
- File: `tests/integration/test_recursive_self_testing.py` (new)
- Propose a high-risk change.
- Verify test agent spawns.
- Verify tests are generated and executed.
- Verify test results appear in memory and approval request.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm pytest and test isolation mechanisms are available.
2. Verify test containers can be provisioned quickly (Docker or tmpfs).

### PHASES 1–6

Validation:
- **Positive:** Generate tests, run them, verify coverage, refine proposal based on failures.
- **Negative:** Test execution failure doesn't block approval path; results logged for Igor.
- **Regression:** Existing testing framework unchanged; new testing is additive.

***
