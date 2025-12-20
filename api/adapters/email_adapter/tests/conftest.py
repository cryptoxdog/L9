# ══════════════════════════════════════════════════════════════════════════════
# Generated from Module-Spec v2.6
# module_id: email.adapter
# enforced_acceptance: ["valid_email_processed", "idempotent_replay_cached", "email_parsed_correctly", "aios_response_forwarded", "packet_written_on_success", ... (8 total)]
# ══════════════════════════════════════════════════════════════════════════════
# DORA META BLOCK — DO NOT EDIT MANUALLY (CI-owned)
# ══════════════════════════════════════════════════════════════════════════════
# __meta__ = {
#     "template_version": "2.6.0",
#     "spec_hash": "SPEC-62d9295fc71f",
#     "created_at": "2025-12-18T06:24:54.974886+00:00",
#     "created_by": "module_pipeline",
#     "last_updated_at": "2025-12-18T06:24:54.974886+00:00",
#     "last_updated_by": "module_pipeline",
#     "module_id": "email.adapter",
#     "file": "tests/conftest.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Pytest Configuration and Shared Fixtures
───────────────────────────────────────────
Shared fixtures for Email Adapter tests

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
    return "email.adapter"


@pytest.fixture
def spec_hash():
    """Spec hash for verification."""
    return "SPEC-62d9295fc71f"
