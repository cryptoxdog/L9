# ══════════════════════════════════════════════════════════════════════════════
# Generated from Module-Spec v2.6
# module_id: calendar.adapter
# enforced_acceptance: ["valid_event_processed", "idempotent_replay_cached", "event_created_successfully", "event_updated_successfully", "aios_response_forwarded", ... (8 total)]
# ══════════════════════════════════════════════════════════════════════════════
# DORA META BLOCK — DO NOT EDIT MANUALLY (CI-owned)
# ══════════════════════════════════════════════════════════════════════════════
# __meta__ = {
#     "template_version": "2.6.0",
#     "spec_hash": "SPEC-447dc3be62b3",
#     "created_at": "2025-12-18T06:25:16.899340+00:00",
#     "created_by": "module_pipeline",
#     "last_updated_at": "2025-12-18T06:25:16.899340+00:00",
#     "last_updated_by": "module_pipeline",
#     "module_id": "calendar.adapter",
#     "file": "tests/conftest.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Pytest Configuration and Shared Fixtures
───────────────────────────────────────────
Shared fixtures for Calendar Adapter tests

Auto-generated from Module-Spec v2.6.0
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def anyio_backend():
    """Configure anyio backend for async tests."""
    return "asyncio"


@pytest.fixture
def module_id():
    """Module ID for tests."""
    return "calendar.adapter"


@pytest.fixture
def spec_hash():
    """Spec hash for verification."""
    return "SPEC-447dc3be62b3"
