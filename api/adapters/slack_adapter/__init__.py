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
#     "file": "__init__.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Slack Webhook Adapter Module
────────────────────────────
Validates Slack events, normalizes to L9 packets, and routes to AIOS reasoning.

Auto-generated from Module-Spec v2.6.0
Spec Hash: SPEC-slack-webhook
"""

import os
import structlog

from .config import SlackWebhookConfig
from .schemas import SlackWebhookRequest, SlackWebhookResponse

__all__ = [
    "SlackWebhookConfig",
    "SlackWebhookRequest",
    "SlackWebhookResponse",
]

__version__ = "1.0.0"
__spec_hash__ = "SPEC-slack-webhook"

# ══════════════════════════════════════════════════════════════════════════════
# STARTUP GUARD: Fail fast if required env vars missing when enabled
# ══════════════════════════════════════════════════════════════════════════════

_logger = structlog.get_logger(__name__)

def _validate_startup() -> None:
    """Validate required configuration at module load time."""
    # Only enforce if explicitly enabled
    if os.getenv("SLACK_APP_ENABLED", "").lower() != "true":
        _logger.debug("Slack Webhook Adapter not enabled (SLACK_APP_ENABLED != true)")
        return
    
    config = SlackWebhookConfig.from_env()
    errors = config.validate()
    
    if errors:
        # Warn but don't crash - allows module to load without credentials
        _logger.warning(
            "Slack Webhook Adapter enabled but missing credentials: %s. "
            "Webhook calls will fail until configured.",
            "; ".join(errors)
        )
        return
    
    _logger.info(
        "Slack Webhook Adapter startup validated: module_id=%s, spec_hash=%s",
        config.module_id,
        __spec_hash__,
    )

# Run validation on import
_validate_startup()

