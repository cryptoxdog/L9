# ══════════════════════════════════════════════════════════════════════════════
# Generated from Module-Spec v2.6
# module_id: twilio.adapter
# enforced_acceptance: ["valid_sms_processed", "idempotent_replay_cached", "signature_validated", "aios_response_forwarded", "packet_written_on_success", ... (8 total)]
# ══════════════════════════════════════════════════════════════════════════════
# DORA META BLOCK — DO NOT EDIT MANUALLY (CI-owned)
# ══════════════════════════════════════════════════════════════════════════════
# __meta__ = {
#     "template_version": "2.6.0",
#     "spec_hash": "SPEC-102d1d3dc34c",
#     "created_at": "2025-12-18T06:25:01.645626+00:00",
#     "created_by": "module_pipeline",
#     "last_updated_at": "2025-12-18T06:25:01.645626+00:00",
#     "last_updated_by": "module_pipeline",
#     "module_id": "twilio.adapter",
#     "file": "tests/conftest.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Pytest Configuration and Shared Fixtures
───────────────────────────────────────────
Shared fixtures for Twilio Adapter tests

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
    return "twilio.adapter"


@pytest.fixture
def spec_hash():
    """Spec hash for verification."""
    return "SPEC-102d1d3dc34c"
