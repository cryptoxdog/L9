# ══════════════════════════════════════════════════════════════════════════════
# Generated from Module-Spec v2.6
# module_id: slack.webhook
# enforced_acceptance: ["valid_request_processed", "idempotent_replay_cached", "stale_timestamp_rejected", "aios_response_forwarded", "packet_written_on_success", ... (6 total)]
# ══════════════════════════════════════════════════════════════════════════════
# DORA META BLOCK — DO NOT EDIT MANUALLY (CI-owned)
# ══════════════════════════════════════════════════════════════════════════════
# __meta__ = {
#     "template_version": "2.6.0",
#     "spec_hash": "SPEC-slack-webhook",
#     "created_at": "2025-12-20T00:00:00.000000+00:00",
#     "created_by": "module_pipeline",
#     "last_updated_at": "2025-12-20T00:00:00.000000+00:00",
#     "last_updated_by": "module_pipeline",
#     "module_id": "slack.webhook",
#     "file": "tests/conftest.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Pytest Configuration and Shared Fixtures
─────────────────────────────────────────
Shared fixtures for Slack Webhook Adapter tests

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
    return "slack.webhook"


@pytest.fixture
def spec_hash():
    """Spec hash for verification."""
    return "SPEC-slack-webhook"
