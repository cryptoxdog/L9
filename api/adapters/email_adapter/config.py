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
#     "file": "config.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Email Adapter Configuration
───────────────────────────
Environment-driven configuration for Email Adapter.

Auto-generated from Module-Spec v2.6.0
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EmailAdapterConfig:
    """Configuration for Email Adapter."""

    # Required environment variables
    email_adapter_signing_secret: str = field(
        default_factory=lambda: os.environ.get("EMAIL_ADAPTER_SIGNING_SECRET", "")
    )
    gmail_api_key: str = field(
        default_factory=lambda: os.environ.get("GMAIL_API_KEY", "")
    )

    # Optional environment variables (EMAIL_ENABLED matches env.example)
    email_enabled: Optional[str] = field(
        default_factory=lambda: os.environ.get("EMAIL_ENABLED")
    )
    email_adapter_log_level: Optional[str] = field(
        default_factory=lambda: os.environ.get("EMAIL_ADAPTER_LOG_LEVEL")
    )

    # Module settings
    module_id: str = "email.adapter"
    module_name: str = "Email Adapter"
    enabled: bool = True

    # Timeouts
    default_timeout_seconds: int = 30
    aios_timeout_seconds: int = 60

    # Idempotency
    dedupe_cache_ttl_seconds: int = 86400

    def validate(self) -> list[str]:
        """Validate required configuration is present."""
        errors = []
        if not self.email_adapter_signing_secret:
            errors.append("Missing required env: EMAIL_ADAPTER_SIGNING_SECRET")
        if not self.gmail_api_key:
            errors.append("Missing required env: GMAIL_API_KEY")
        return errors

    @classmethod
    def from_env(cls) -> "EmailAdapterConfig":
        """Create config from environment variables."""
        return cls()


# Global config instance (lazy loaded)
_config: Optional[EmailAdapterConfig] = None


def get_config() -> EmailAdapterConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = EmailAdapterConfig.from_env()
    return _config
