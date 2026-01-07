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
#     "file": "config.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Calendar Adapter Configuration
──────────────────────────────
Environment-driven configuration for Calendar Adapter.

Auto-generated from Module-Spec v2.6.0
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CalendarAdapterConfig:
    """Configuration for Calendar Adapter."""

    # Required environment variables
    google_calendar_api_key: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_CALENDAR_API_KEY", "")
    )
    google_calendar_webhook_secret: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_CALENDAR_WEBHOOK_SECRET", "")
    )

    # Optional environment variables
    calendar_adapter_enabled: Optional[str] = field(
        default_factory=lambda: os.environ.get("CALENDAR_ADAPTER_ENABLED")
    )
    calendar_adapter_log_level: Optional[str] = field(
        default_factory=lambda: os.environ.get("CALENDAR_ADAPTER_LOG_LEVEL")
    )
    calendar_sync_interval_minutes: Optional[str] = field(
        default_factory=lambda: os.environ.get("CALENDAR_SYNC_INTERVAL_MINUTES")
    )

    # Module settings
    module_id: str = "calendar.adapter"
    module_name: str = "Calendar Adapter"
    enabled: bool = True

    # Timeouts
    default_timeout_seconds: int = 30
    aios_timeout_seconds: int = 60

    # Idempotency
    dedupe_cache_ttl_seconds: int = 86400

    def validate(self) -> list[str]:
        """Validate required configuration is present."""
        errors = []
        if not self.google_calendar_api_key:
            errors.append("Missing required env: GOOGLE_CALENDAR_API_KEY")
        if not self.google_calendar_webhook_secret:
            errors.append("Missing required env: GOOGLE_CALENDAR_WEBHOOK_SECRET")
        return errors

    @classmethod
    def from_env(cls) -> "CalendarAdapterConfig":
        """Create config from environment variables."""
        return cls()


# Global config instance (lazy loaded)
_config: Optional[CalendarAdapterConfig] = None


def get_config() -> CalendarAdapterConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = CalendarAdapterConfig.from_env()
    return _config
