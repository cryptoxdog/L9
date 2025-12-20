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
#     "file": "__init__.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Email Adapter Module
────────────────────
Receives inbound emails via webhook, parses content, and routes to AIOS for processing. Supports Gmail API integration.

Auto-generated from Module-Spec v2.6.0
Spec Hash: SPEC-62d9295fc71f
"""

import os
import logging

from .config import EmailAdapterConfig
from .schemas import EmailAdapterRequest, EmailAdapterResponse

__all__ = [
    "EmailAdapterConfig",
    "EmailAdapterRequest",
    "EmailAdapterResponse",
]

__version__ = "1.0.0"
__spec_hash__ = "SPEC-62d9295fc71f"

# ══════════════════════════════════════════════════════════════════════════════
# STARTUP GUARD: Fail fast if required env vars missing when enabled
# ══════════════════════════════════════════════════════════════════════════════

_logger = logging.getLogger(__name__)

def _validate_startup() -> None:
    """Validate required configuration at module load time."""
    # Only enforce if explicitly enabled (using env.example naming)
    if os.getenv("EMAIL_ENABLED", "").lower() != "true":
        _logger.debug("Email Adapter not enabled (EMAIL_ENABLED != true)")
        return
    
    config = EmailAdapterConfig.from_env()
    errors = config.validate()
    
    if errors:
        # Warn but don't crash - allows module to load without credentials
        _logger.warning(
            "Email Adapter enabled but missing credentials: %s. "
            "Webhook calls will fail until configured.",
            "; ".join(errors)
        )
        return
    
    _logger.info(
        "Email Adapter startup validated: module_id=%s, spec_hash=%s",
        config.module_id,
        __spec_hash__,
    )

# Run validation on import
_validate_startup()
