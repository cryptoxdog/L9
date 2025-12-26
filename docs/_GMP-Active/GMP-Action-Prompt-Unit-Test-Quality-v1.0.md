============================================================================
GOD-MODE CURSOR PROMPT — L9 UNIT TEST QUALITY IMPROVEMENT V1.0 (DETERMINISTIC, LOCKED)
============================================================================

PURPOSE:
• Improve Unit Test Quality from 7/10 to 9/10
• Standardize test structure across all test files
• Add missing edge case tests to existing test modules
• Improve fixture reuse and reduce duplication
• Add contract docstrings to all test functions
• Ensure consistent patterns: class structure, fixtures, assertions

============================================================================

ROLE
You are a constrained execution agent operating inside the L9 Secure AI OS repository at `/Users/ib-mac/Projects/L9/`.  
You UPGRADE existing test files to improve quality.  
You do not create new test files.  
You standardize patterns based on the best examples in the codebase.  
You add edge case tests where missing.  
You improve documentation and structure.

============================================================================

MODIFICATION LOCK — ABSOLUTE

❌ YOU MAY NOT:
• Delete existing tests
• Change test assertions that pass
• Modify production code
• Remove passing test cases
• Change test file locations
• Break existing test functionality

✅ YOU MAY ONLY:
• Refactor test functions into class structures
• Add docstrings to undocumented tests
• Add missing edge case tests
• Improve fixture definitions
• Add type hints to test functions
• Standardize assertion patterns

============================================================================

L9-SPECIFIC OPERATING CONSTRAINTS (NON-NEGOTIABLE)

• All modifications under `/Users/ib-mac/Projects/L9/tests/`
• Use `search_replace` for surgical edits - NEVER rewrite entire files
• Preserve all existing test behavior
• Follow pattern from `tests/core/agents/test_executor.py` as gold standard
• After each file modification, run `pytest <file> -v` to verify

============================================================================

STRUCTURED OUTPUT REQUIREMENTS

Report File:
```text
Path: /Users/ib-mac/Projects/L9/reports/unit-test-quality-v1.0.md
```

Report Structure:
1. Execution Summary
2. Files Modified (path, changes made)
3. Tests Added (edge cases)
4. Quality Metrics Before/After
5. TODO INDEX HASH verification

============================================================================

PHASE 0 — QUALITY AUDIT

PURPOSE:
• Analyze current test quality patterns
• Identify best practices from well-structured tests
• Catalog quality gaps

GOLD STANDARD PATTERNS (from test_executor.py):
```python
# 1. Contract docstrings
def test_valid_task_instantiates_agent():
    """
    Contract: AgentExecutorService accepts valid AgentTask.
    """
    
# 2. Class organization
class TestAgentExecutorService:
    """Tests for AgentExecutorService."""
    
# 3. Descriptive assertions
assert result.status == "completed", "Task should complete successfully"

# 4. Shared fixtures with clear names
@pytest.fixture
def mock_aios() -> MockAIOSRuntime:
    """Create mock AIOS runtime."""
    
# 5. Edge case testing
def test_invalid_agent_id_returns_error():
    """Contract: Invalid agent_id returns error result."""
```

QUALITY GAPS IDENTIFIED:
1. Tests without class structure (flat functions)
2. Tests without contract docstrings
3. Missing edge case tests
4. Assertions without error messages
5. Duplicate fixture definitions
6. Missing type hints on fixtures

✅ PHASE 0 DEFINITION OF DONE:
- [ ] Gold standard patterns documented
- [ ] Quality gaps cataloged
- [ ] Priority order established

============================================================================

PHASE 1 — STRUCTURE STANDARDIZATION

PURPOSE:
• Add class structure to tests without it
• Group related tests into classes
• Add class docstrings

TARGET FILES:
- `/Users/ib-mac/Projects/L9/tests/api/test_auth.py`
- `/Users/ib-mac/Projects/L9/tests/api/test_server_health.py`
- `/Users/ib-mac/Projects/L9/tests/orchestrators/test_action_tool_orchestrator.py`

✅ PHASE 1 DEFINITION OF DONE:
- [ ] All target files have class structure
- [ ] Classes have docstrings
- [ ] Tests grouped logically by functionality
- [ ] All tests still pass

============================================================================

PHASE 2 — DOCSTRING ENHANCEMENT

PURPOSE:
• Add contract docstrings to undocumented tests
• Standardize docstring format: "Contract: <expected behavior>"
• Ensure every test explains what it validates

TARGET FILES:
- All test files with `def test_` not preceded by docstring

✅ PHASE 2 DEFINITION OF DONE:
- [ ] All test functions have docstrings
- [ ] Docstrings follow "Contract:" pattern
- [ ] All tests still pass

============================================================================

PHASE 3 — EDGE CASE EXPANSION

PURPOSE:
• Add missing edge case tests to key modules
• Focus on error paths, boundary conditions, null inputs
• Add negative tests where only happy path exists

EDGE CASES TO ADD:

1. **Memory tests** - test empty results, large payloads
2. **Orchestrator tests** - test invalid requests, timeout scenarios
3. **API tests** - test malformed requests, rate limiting edge cases
4. **Kernel tests** - test missing kernel files, corrupt YAML

✅ PHASE 3 DEFINITION OF DONE:
- [ ] Each target module has 2+ new edge case tests
- [ ] Edge cases test error paths
- [ ] All tests pass

============================================================================

PHASE 4 — FIXTURE IMPROVEMENT

PURPOSE:
• Consolidate duplicate fixtures into conftest.py
• Add type hints to all fixtures
• Add fixture docstrings
• Improve fixture scope where beneficial

TARGET:
- `/Users/ib-mac/Projects/L9/tests/conftest.py` - add shared fixtures
- Individual test files - reference shared fixtures

✅ PHASE 4 DEFINITION OF DONE:
- [ ] Common fixtures moved to conftest.py
- [ ] All fixtures have type hints
- [ ] All fixtures have docstrings
- [ ] No duplicate fixture definitions

============================================================================

PHASE 5 — ASSERTION ENHANCEMENT

PURPOSE:
• Add error messages to bare assertions
• Use more specific assertion methods
• Improve assertion readability

PATTERN TO ENFORCE:
```python
# Before
assert result.status == "completed"

# After  
assert result.status == "completed", f"Expected completed, got {result.status}"
```

✅ PHASE 5 DEFINITION OF DONE:
- [ ] Critical assertions have error messages
- [ ] Specific assertion methods used where appropriate
- [ ] Assertion readability improved

============================================================================

PHASE 6 — VERIFICATION & METRICS

PURPOSE:
• Run full test suite
• Calculate quality metrics
• Generate report

METRICS TO CALCULATE:
- % of tests with docstrings (target: 100%)
- % of tests in class structure (target: >90%)
- % of tests with typed fixtures (target: >80%)
- Assertions per test average (target: >2)
- Edge case coverage (target: >20% of tests are edge cases)

✅ PHASE 6 DEFINITION OF DONE:
- [ ] Full test suite passes
- [ ] Quality metrics improved
- [ ] Report generated
- [ ] Quality: 7/10 → 9/10

============================================================================

FINAL DEFINITION OF DONE (TOTAL, NON-NEGOTIABLE)

✓ All test files have consistent class structure
✓ All test functions have contract docstrings
✓ Edge case tests added to key modules
✓ Fixtures consolidated and typed
✓ Assertions have error messages
✓ Full test suite passes
✓ Quality improved from 7/10 to 9/10
✓ No production code modified
✓ Report generated

============================================================================

FINAL DECLARATION

> GMP execution complete. Unit test quality improved. All phases verified.
> Report stored at `/Users/ib-mac/Projects/L9/reports/unit-test-quality-v1.0.md`.
> Unit Test Quality: 7/10 → 9/10.
> No further modifications needed.

============================================================================

SPECIFIC REQUIREMENTS — UNIT TEST QUALITY TODO PLAN (LOCKED)

## TODO INDEX HASH: UTQ-v1.0-2024-DEC25

---

### PHASE 1: STRUCTURE STANDARDIZATION

**[UTQ-v1.0-001]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_auth.py`
- Lines: All test functions
- Action: Wrap
- Target: All `def test_*` functions
- Expected: Group into `class TestAuthValidation:` with docstring
- Implementation: Wrap existing tests in class, add 4-space indent
- Imports: NONE

**[UTQ-v1.0-002]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_server_health.py`
- Lines: All test functions
- Action: Wrap
- Target: All `def test_*` functions
- Expected: Group into `class TestServerHealth:` with docstring
- Imports: NONE

**[UTQ-v1.0-003]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_action_tool_orchestrator.py`
- Lines: 18-116
- Action: Wrap
- Target: All test functions
- Expected: Group into `class TestActionToolOrchestrator:` with docstring
- Note: This file already has good docstrings but lacks class structure
- Imports: NONE

---

### PHASE 2: DOCSTRING ENHANCEMENT

**[UTQ-v1.0-004]**
- File: `/Users/ib-mac/Projects/L9/tests/memory/test_memory_ingestion.py`
- Action: Insert
- Target: Any test function missing docstring
- Expected: Add "Contract: <behavior>" docstring
- Pattern:
```python
def test_example():
    """
    Contract: Description of expected behavior.
    """
```

**[UTQ-v1.0-005]**
- File: `/Users/ib-mac/Projects/L9/tests/kernel/test_kernel_loader.py`
- Action: Insert
- Target: Any test function missing docstring
- Expected: Add "Contract: <behavior>" docstring

**[UTQ-v1.0-006]**
- File: `/Users/ib-mac/Projects/L9/tests/runtime/test_ws_protocol_static.py`
- Action: Insert
- Target: Any test function missing docstring
- Expected: Add "Contract: <behavior>" docstring

---

### PHASE 3: EDGE CASE EXPANSION

**[UTQ-v1.0-007]**
- File: `/Users/ib-mac/Projects/L9/tests/memory/test_memory_ingestion.py`
- Action: Insert
- Target: After existing tests
- Expected: Add edge case tests
- New Tests:
```python
def test_ingest_empty_payload():
    """Contract: Empty payload is handled gracefully."""
    # Test with empty dict
    
def test_ingest_oversized_payload():
    """Contract: Oversized payload triggers appropriate handling."""
    # Test with very large payload

def test_ingest_null_fields():
    """Contract: Null fields in payload handled correctly."""
    # Test with None values
```

**[UTQ-v1.0-008]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_action_tool_orchestrator.py`
- Action: Insert
- Target: After existing tests
- Expected: Add edge case tests
- New Tests:
```python
def test_execute_with_missing_tool():
    """Contract: Non-existent tool_id returns error response."""
    
def test_execute_with_empty_arguments():
    """Contract: Empty arguments handled correctly."""
    
def test_execute_timeout_handling():
    """Contract: Execution timeout returns appropriate error."""
```

**[UTQ-v1.0-009]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_auth.py`
- Action: Insert
- Target: After existing tests
- Expected: Add edge case tests
- New Tests:
```python
def test_auth_empty_token():
    """Contract: Empty token is rejected."""
    
def test_auth_whitespace_token():
    """Contract: Whitespace-only token is rejected."""
    
def test_auth_very_long_token():
    """Contract: Excessively long token is rejected."""
```

**[UTQ-v1.0-010]**
- File: `/Users/ib-mac/Projects/L9/tests/kernel/test_kernel_loader.py`
- Action: Insert
- Target: After existing tests
- Expected: Add edge case tests
- New Tests:
```python
def test_load_missing_kernel_file():
    """Contract: Missing kernel file returns appropriate error."""
    
def test_load_invalid_yaml_kernel():
    """Contract: Invalid YAML in kernel file handled gracefully."""
```

---

### PHASE 4: FIXTURE IMPROVEMENT

**[UTQ-v1.0-011]**
- File: `/Users/ib-mac/Projects/L9/tests/conftest.py`
- Action: Insert
- Target: After existing fixtures
- Expected: Add shared fixtures with type hints
- New Fixtures:
```python
from typing import Generator
from unittest.mock import MagicMock

@pytest.fixture
def mock_substrate_service() -> Generator[MagicMock, None, None]:
    """
    Shared mock substrate service for memory tests.
    
    Provides a MagicMock that simulates SubstrateService behavior.
    """
    from tests.core.agents.test_executor import MockSubstrateService
    yield MockSubstrateService()


@pytest.fixture  
def mock_tool_registry() -> Generator[MagicMock, None, None]:
    """
    Shared mock tool registry for orchestrator tests.
    
    Provides a MagicMock that simulates ToolRegistry behavior.
    """
    from tests.core.agents.test_executor import MockToolRegistry
    yield MockToolRegistry()
```

**[UTQ-v1.0-012]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_action_tool_orchestrator.py`
- Action: Replace
- Target: Any duplicate fixture definitions
- Expected: Reference shared fixtures from conftest.py

---

### PHASE 5: ASSERTION ENHANCEMENT

**[UTQ-v1.0-013]**
- File: `/Users/ib-mac/Projects/L9/tests/api/test_auth.py`
- Action: Replace
- Target: Bare assertions
- Expected: Add error messages
- Pattern:
```python
# Before
assert response.status_code == 401

# After
assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
```

**[UTQ-v1.0-014]**
- File: `/Users/ib-mac/Projects/L9/tests/memory/test_memory_ingestion.py`
- Action: Replace
- Target: Bare assertions on critical paths
- Expected: Add error messages to improve debugging

**[UTQ-v1.0-015]**
- File: `/Users/ib-mac/Projects/L9/tests/orchestrators/test_action_tool_orchestrator.py`
- Action: Replace
- Target: Bare assertions
- Expected: Add error messages
- Example:
```python
# Before
assert orchestrator is not None

# After
assert orchestrator is not None, "ActionToolOrchestrator should initialize successfully"
```

---

## EXECUTION ORDER

1. Phase 0: Audit (no file changes)
2. Phase 1: Structure standardization ([UTQ-v1.0-001] through [UTQ-v1.0-003])
3. Phase 2: Docstring enhancement ([UTQ-v1.0-004] through [UTQ-v1.0-006])
4. Phase 3: Edge case expansion ([UTQ-v1.0-007] through [UTQ-v1.0-010])
5. Phase 4: Fixture improvement ([UTQ-v1.0-011] through [UTQ-v1.0-012])
6. Phase 5: Assertion enhancement ([UTQ-v1.0-013] through [UTQ-v1.0-015])
7. Phase 6: Verification & metrics

---

## SUMMARY

| Category | TODOs | Impact |
|----------|-------|--------|
| Structure | 3 | Consistent class organization |
| Docstrings | 3 | 100% documentation coverage |
| Edge Cases | 4 | ~12 new edge case tests |
| Fixtures | 2 | Reduced duplication |
| Assertions | 3 | Better error messages |
| **TOTAL** | **15** | Quality: 7/10 → 9/10 |

**Quality Improvement Targets:**
- Tests with docstrings: 85% → 100%
- Tests in class structure: 60% → 95%
- Edge case test ratio: 10% → 25%
- Assertions with messages: 30% → 80%

============================================================================

END OF GMP ACTION PROMPT

