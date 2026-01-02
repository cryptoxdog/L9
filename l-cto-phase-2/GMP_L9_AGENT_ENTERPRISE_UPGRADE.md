============================================================================
GOD-MODE CURSOR PROMPT — L9 AGENT ENTERPRISE UPGRADE v1.0
============================================================================

PURPOSE:
• Upgrade l-cto-phase-2/l9_agent/ stubs to enterprise-grade production code
• Apply 20-point Enterprise-Grade Checklist to all module files
• Verify each requirement exists, add if missing
• Preserve existing logic while adding L9 integration patterns
• Produce deterministic, auditable TODO plan with full traceability

============================================================================

ROLE
You are a constrained execution agent operating inside the L9 Secure AI OS repository at `/Users/ib-mac/Projects/L9/`.
You execute instructions exactly as written.
You do not redesign the module logic.
You do not invent new features.
You do not guess missing information.
You report only to this prompt.

============================================================================

MODIFICATION LOCK — ABSOLUTE

❌ YOU MAY NOT:
• Create new module files unless explicitly listed in Phase 0 TODO plan
• Change core module LOGIC (desire/will/trust algorithms stay the same)
• Add features beyond the 20-point checklist
• Refactor beyond what's needed for L9 integration
• Touch files outside l-cto-phase-2/l9_agent/

✅ YOU MAY ONLY:
• Add missing enterprise requirements from the 20-point checklist
• Wrap existing logic with async, error handling, logging
• Add Pydantic models, type hints, docstrings
• Wire to L9 systems (PacketEnvelope, MemorySubstrate, governance)
• Move files to production location (/l9_agent/) after upgrade

============================================================================

L9-SPECIFIC OPERATING CONSTRAINTS (NON-NEGOTIABLE)

• All file paths must be absolute under `/Users/ib-mac/Projects/L9/`
• All async code must use `async def` and `await`
• All memory writes must use PacketEnvelopeIn from memory.substrate_models
• All logging must use structlog with context (agent_id, module, operation)
• All configuration must come from environment or YAML (no hardcoded paths)
• Feature flags must use L9_ENABLE_* pattern

============================================================================

ENTERPRISE-GRADE CHECKLIST (20 ITEMS)

For EACH file in l-cto-phase-2/l9_agent/, verify and add if missing:

| # | Requirement | How to Check | How to Add |
|---|-------------|--------------|------------|
| 1 | Async methods | All public methods are `async def` | Wrap with async/await |
| 2 | PacketEnvelope emission | Decisions emit packets | Add substrate.ingest_packet() |
| 3 | MemorySubstrate persistence | State persists to memory | Add load/save methods |
| 4 | L9 governance integration | Has on_task hooks | Add lifecycle methods |
| 5 | Production error handling | try/except with recovery | Add error handlers |
| 6 | Pydantic models | All data uses BaseModel | Create models.py |
| 7 | Dependency injection | Constructor takes dependencies | Refactor __init__ |
| 8 | Structured logging | Uses structlog with context | Add logger calls |
| 9 | Metrics/Prometheus | Has counters/histograms | Add metrics module |
| 10 | Input validation | All inputs validated | Add validators |
| 11 | Idempotency keys | Memory writes have dedup_key | Add to packets |
| 12 | Environment config | Uses os.getenv() | Replace hardcoded |
| 13 | Pytest structure | Uses @pytest.mark.asyncio | Rewrite tests |
| 14 | Complete type hints | All args/returns typed | Add annotations |
| 15 | Full docstrings | Args/Returns/Raises present | Add docstrings |
| 16 | Circuit breakers | External calls protected | Add decorator |
| 17 | Feature flags | Toggleable via L9_ENABLE_* | Add conditionals |
| 18 | Graceful degradation | Failures don't crash agent | Add fallbacks |
| 19 | Version support | Has VERSION constant | Add to module |
| 20 | Executor integration | Has lifecycle hooks | Add hook methods |

============================================================================

TARGET FILES (12 files to upgrade)

```
l-cto-phase-2/l9_agent/
├── __init__.py              # Update exports
├── value_alignment.py       # Core module
├── value_tests.py           # Tests
├── desire_engine.py         # Core module
├── will_engine.py           # Core module
├── persistence_engine.py    # Core module
├── goal_commitment.py       # Core module
├── desire_tests.py          # Tests
├── trust_model.py           # Core module
├── trust_engine.py          # Core module
├── trust_hooks.py           # Integration
├── trust_visualization.py   # Utility
└── trust_tests.py           # Tests
```

NEW FILES TO CREATE:
- `l9_agent/models.py` - Pydantic models for all data
- `l9_agent/metrics.py` - Prometheus metrics
- `l9_agent/config.py` - Configuration loader

============================================================================

STRUCTURED OUTPUT REQUIREMENTS

Output MUST be written to:
```
Path: /Users/ib-mac/Projects/L9/reports/GMP_Report_L9_Agent_Enterprise_Upgrade.md
```

Required sections:
1. `# EXECUTION REPORT — L9 Agent Enterprise Upgrade`
2. `## TODO PLAN (LOCKED)`
3. `## TODO INDEX HASH`
4. `## PHASE CHECKLIST STATUS (0–6)`
5. `## FILES MODIFIED + LINE RANGES`
6. `## TODO → CHANGE MAP`
7. `## ENTERPRISE CHECKLIST VERIFICATION` (20-item matrix per file)
8. `## ENFORCEMENT + VALIDATION RESULTS`
9. `## PHASE 5 RECURSIVE VERIFICATION`
10. `## FINAL DEFINITION OF DONE (TOTAL)`
11. `## FINAL DECLARATION`

============================================================================

PHASE 0 — AUDIT EXISTING CODE + TODO PLAN LOCK

PURPOSE:
• Read each target file
• For each file, check all 20 enterprise requirements
• Create TODO items ONLY for missing requirements
• Lock plan before any edits

ACTIONS:
1. Read each of the 12 target files
2. For each file, create a 20-item audit matrix:
   ```
   File: value_alignment.py
   [ ] 1. Async methods - MISSING
   [x] 2. PacketEnvelope - N/A (no state changes)
   [ ] 3. MemorySubstrate - MISSING
   ...
   ```
3. Generate TODO items for all MISSING items
4. Write TODO plan to report

REQUIRED TODO FORMAT:
```markdown
- [0.1] File: `/Users/ib-mac/Projects/L9/l-cto-phase-2/l9_agent/value_alignment.py`
        Requirement: #1 Async methods
        Action: Wrap | Lines: 41-57
        Target: `score_action()` method
        Change: Convert to `async def score_action()`
        Imports: NONE
```

✅ PHASE 0 DEFINITION OF DONE:
- [ ] All 12 files audited against 20-point checklist
- [ ] Audit matrix documented per file
- [ ] TODO items generated for all MISSING requirements
- [ ] TODO PLAN locked in report
- [ ] TODO INDEX HASH generated

============================================================================

PHASE 1 — BASELINE CONFIRMATION

PURPOSE:
• Verify all target files exist
• Confirm line numbers match
• Confirm current function signatures

ACTIONS:
• Open each file from TODO plan
• Confirm target functions/classes exist
• Record baseline state

✅ PHASE 1 DEFINITION OF DONE:
- [ ] Every TODO target confirmed to exist
- [ ] Line numbers verified accurate
- [ ] Baseline signatures recorded

============================================================================

PHASE 2 — IMPLEMENTATION

PURPOSE:
• Apply each TODO item
• Add missing enterprise requirements
• Preserve existing logic

IMPLEMENTATION PATTERNS:

### Pattern 1: Async Wrapper
```python
# BEFORE:
def score_action(self, action_tags: list[str]) -> float:
    ...

# AFTER:
async def score_action(self, action_tags: List[str]) -> float:
    ...
```

### Pattern 2: Dependency Injection
```python
# BEFORE:
def __init__(self, config_path="config/core_values.yaml"):

# AFTER:
def __init__(
    self,
    substrate: Optional[MemorySubstrateService] = None,
    config_path: Optional[str] = None,
    logger: Optional[structlog.BoundLogger] = None,
):
    self.substrate = substrate
    self.config_path = config_path or os.getenv("L9_VALUES_CONFIG", "config/core_values.yaml")
    self.logger = logger or structlog.get_logger(__name__)
```

### Pattern 3: PacketEnvelope Emission
```python
async def on_alignment_scored(self, score: float, action_tags: List[str]) -> None:
    if self.substrate:
        await self.substrate.ingest_packet(
            PacketEnvelopeIn(
                source_id="l9_agent.value_alignment",
                agent_id="L",
                kind="DECISION",
                payload={
                    "event": "alignment_scored",
                    "score": score,
                    "action_tags": action_tags,
                },
                metadata=PacketMetadata(
                    timestamp=datetime.utcnow().isoformat(),
                    confidence=score,
                ),
            )
        )
```

### Pattern 4: Pydantic Models
```python
# NEW FILE: models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AlignmentScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    action_tags: List[str]
    explanation: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TrustScore(BaseModel):
    partner_id: str
    score: float = Field(ge=0.0, le=1.0)
    history: List[tuple] = Field(default_factory=list)
```

### Pattern 5: Structured Logging
```python
self.logger.info(
    "alignment_scored",
    score=score,
    action_tags=action_tags,
    total_weight=total_weight,
    matched_weight=matched_weight,
)
```

### Pattern 6: Error Handling
```python
async def score_action(self, action_tags: List[str]) -> AlignmentScore:
    try:
        # existing logic
        score = self._calculate_score(action_tags)
        await self.on_alignment_scored(score, action_tags)
        return AlignmentScore(score=score, action_tags=action_tags)
    except FileNotFoundError as e:
        self.logger.error("config_not_found", error=str(e))
        raise ConfigurationError(f"Core values config missing: {e}") from e
    except Exception as e:
        self.logger.error("alignment_score_failed", error=str(e))
        # Graceful degradation: return neutral score
        return AlignmentScore(score=0.5, action_tags=action_tags)
```

### Pattern 7: Feature Flags
```python
if os.getenv("L9_ENABLE_VALUE_ALIGNMENT_PACKETS", "true").lower() == "true":
    await self.on_alignment_scored(score, action_tags)
```

### Pattern 8: Executor Integration
```python
class ValueAlignmentModule:
    """L9 Executor-integrated value alignment module."""
    
    VERSION = "1.0.0"
    
    async def on_task_start(self, task: AgentTask) -> None:
        """Called when agent task starts."""
        self.logger.info("task_started", task_id=str(task.id))
    
    async def on_task_complete(self, result: ExecutionResult) -> None:
        """Called when agent task completes."""
        # Score the task outcome
        tags = self._extract_tags_from_result(result)
        await self.score_action(tags)
    
    async def on_task_error(self, error: Exception) -> None:
        """Called when agent task fails."""
        self.logger.error("task_failed", error=str(error))
```

✅ PHASE 2 DEFINITION OF DONE:
- [ ] All TODO items implemented
- [ ] Only TODO-listed files modified
- [ ] All 20 requirements addressed per file
- [ ] Existing logic preserved
- [ ] Line ranges recorded in report

============================================================================

PHASE 3 — ENFORCEMENT (TESTS)

PURPOSE:
• Update test files to pytest structure
• Add async test fixtures
• Ensure all modules testable

ACTIONS:
• Convert value_tests.py → test_value_alignment.py
• Convert desire_tests.py → test_motivation.py
• Convert trust_tests.py → test_trust.py
• Add pytest.mark.asyncio decorators
• Add mock fixtures for substrate/logger

✅ PHASE 3 DEFINITION OF DONE:
- [ ] All tests use pytest structure
- [ ] All async methods tested with @pytest.mark.asyncio
- [ ] Mock fixtures created for L9 dependencies
- [ ] Tests pass with `PYTHONPATH=. pytest l9_agent/`

============================================================================

PHASE 4 — VALIDATION

PURPOSE:
• Run all tests
• Verify imports work
• Confirm no regressions

ACTIONS:
• Run: `PYTHONPATH=. python -m pytest l9_agent/ -v`
• Run: `python -c "from l9_agent import ValueAlignmentEngine"`
• Verify all 12 files import cleanly

✅ PHASE 4 DEFINITION OF DONE:
- [ ] All tests pass
- [ ] All imports work
- [ ] No lint errors
- [ ] No type errors (if mypy available)

============================================================================

PHASE 5 — RECURSIVE VERIFICATION

PURPOSE:
• Verify all 20 requirements met for all 12 files
• Generate final compliance matrix

ACTIONS:
• Create 12x20 matrix showing compliance
• Verify no requirements missed
• Confirm TODO→Change mapping complete

✅ PHASE 5 DEFINITION OF DONE:
- [ ] 12x20 compliance matrix complete
- [ ] All cells marked [x] or [N/A]
- [ ] No [MISSING] cells remain
- [ ] TODO→Change map verified

============================================================================

PHASE 6 — FINALIZATION

PURPOSE:
• Move upgraded files to production location
• Update l9_agent/__init__.py exports
• Finalize report

ACTIONS:
• Move l-cto-phase-2/l9_agent/ → /l9_agent/
• Update all imports
• Write final report sections

✅ PHASE 6 DEFINITION OF DONE:
- [ ] Files moved to production location
- [ ] Imports updated
- [ ] Report complete at /Users/ib-mac/Projects/L9/reports/GMP_Report_L9_Agent_Enterprise_Upgrade.md
- [ ] Final declaration written

============================================================================

FINAL DEFINITION OF DONE (TOTAL)

✓ All 12 files upgraded with all 20 enterprise requirements
✓ Pydantic models created in models.py
✓ Metrics module created in metrics.py
✓ Config loader created in config.py
✓ All tests pass
✓ All imports work
✓ 12x20 compliance matrix complete
✓ Files moved to /l9_agent/
✓ Report written to required path

============================================================================

FINAL DECLARATION (REQUIRED IN REPORT)

> All phases (0–6) complete. 12 files upgraded. 20 requirements applied.
> L9 Agent modules now enterprise-grade production quality.
> Output verified. Report stored at `/Users/ib-mac/Projects/L9/reports/GMP_Report_L9_Agent_Enterprise_Upgrade.md`
> No further changes permitted.

============================================================================

EXECUTION NOTES

• This GMP is for FUTURE execution when Phase 5 becomes priority
• Current priority is CodeGenAgent (Phase 0)
• Save this prompt for later use
• Do NOT execute until workflow_state.md shows Phase 5 active

============================================================================

