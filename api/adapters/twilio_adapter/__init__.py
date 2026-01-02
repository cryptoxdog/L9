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
#     "file": "__init__.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Twilio Adapter Module
─────────────────────
Receives Twilio SMS/voice webhooks, validates signatures, and routes to AIOS for processing. Supports outbound messaging via Twilio API.

Auto-generated from Module-Spec v2.6.0
Spec Hash: SPEC-102d1d3dc34c
"""

import os
import structlog

from .config import TwilioAdapterConfig
from .schemas import TwilioAdapterRequest, TwilioAdapterResponse

__all__ = [
    "TwilioAdapterConfig",
    "TwilioAdapterRequest",
    "TwilioAdapterResponse",
]

__version__ = "1.0.0"
__spec_hash__ = "SPEC-102d1d3dc34c"

# ══════════════════════════════════════════════════════════════════════════════
# STARTUP GUARD: Fail fast if required env vars missing when enabled
# ══════════════════════════════════════════════════════════════════════════════

_logger = structlog.get_logger(__name__)


def _validate_startup() -> None:
    """Validate required configuration at module load time."""
    # Only enforce if explicitly enabled (using env.example naming)
    if os.getenv("TWILIO_ENABLED", "").lower() != "true":
        _logger.debug("Twilio Adapter not enabled (TWILIO_ENABLED != true)")
        return

    config = TwilioAdapterConfig.from_env()
    errors = config.validate()

    if errors:
        # Warn but don't crash - allows module to load without credentials
        _logger.warning(
            "Twilio Adapter enabled but missing credentials: %s. "
            "Webhook calls will fail until configured.",
            "; ".join(errors),
        )
        return

    _logger.info(
        "Twilio Adapter startup validated: module_id=%s, spec_hash=%s",
        config.module_id,
        __spec_hash__,
    )


# Run validation on import
_validate_startup()
