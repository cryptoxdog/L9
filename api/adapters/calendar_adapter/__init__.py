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
#     "file": "__init__.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Calendar Adapter Module
───────────────────────
Syncs with Google/Outlook calendars, creates/updates events, and notifies AIOS of scheduling changes.

Auto-generated from Module-Spec v2.6.0
Spec Hash: SPEC-447dc3be62b3
"""

import os
import structlog

from .config import CalendarAdapterConfig
from .schemas import CalendarAdapterRequest, CalendarAdapterResponse

__all__ = [
    "CalendarAdapterConfig",
    "CalendarAdapterRequest",
    "CalendarAdapterResponse",
]

__version__ = "1.0.0"
__spec_hash__ = "SPEC-447dc3be62b3"

# ══════════════════════════════════════════════════════════════════════════════
# STARTUP GUARD: Fail fast if required env vars missing when enabled
# ══════════════════════════════════════════════════════════════════════════════

_logger = structlog.get_logger(__name__)


def _validate_startup() -> None:
    """Validate required configuration at module load time."""
    # Only enforce if explicitly enabled
    if os.getenv("CALENDAR_ADAPTER_ENABLED", "").lower() != "true":
        _logger.debug("Calendar Adapter not enabled (CALENDAR_ADAPTER_ENABLED != true)")
        return

    config = CalendarAdapterConfig.from_env()
    errors = config.validate()

    if errors:
        # Warn but don't crash - allows module to load without credentials
        _logger.warning(
            "Calendar Adapter enabled but missing credentials: %s. "
            "Webhook calls will fail until configured.",
            "; ".join(errors),
        )
        return

    _logger.info(
        "Calendar Adapter startup validated: module_id=%s, spec_hash=%s",
        config.module_id,
        __spec_hash__,
    )


# Run validation on import
_validate_startup()
