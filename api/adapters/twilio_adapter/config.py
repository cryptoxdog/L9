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
#     "file": "config.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Twilio Adapter Configuration
────────────────────────────
Environment-driven configuration for Twilio Adapter.

Auto-generated from Module-Spec v2.6.0
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TwilioAdapterConfig:
    """Configuration for Twilio Adapter."""

    # Required environment variables (matching env.example)
    twilio_account_sid: str = field(
        default_factory=lambda: os.environ.get("TWILIO_ACCOUNT_SID", "")
    )
    twilio_auth_token: str = field(
        default_factory=lambda: os.environ.get("TWILIO_AUTH_TOKEN", "")
    )
    twilio_sms_number: str = field(
        default_factory=lambda: os.environ.get("TWILIO_SMS_NUMBER", "")
    )

    # Optional environment variables (matching env.example)
    twilio_enabled: Optional[str] = field(
        default_factory=lambda: os.environ.get("TWILIO_ENABLED")
    )
    twilio_whatsapp_number: Optional[str] = field(
        default_factory=lambda: os.environ.get("TWILIO_WHATSAPP_NUMBER")
    )
    twilio_adapter_log_level: Optional[str] = field(
        default_factory=lambda: os.environ.get("TWILIO_ADAPTER_LOG_LEVEL")
    )

    # Module settings
    module_id: str = "twilio.adapter"
    module_name: str = "Twilio Adapter"
    enabled: bool = True

    # Timeouts
    default_timeout_seconds: int = 30
    aios_timeout_seconds: int = 60

    # Idempotency
    dedupe_cache_ttl_seconds: int = 86400

    def validate(self) -> list[str]:
        """Validate required configuration is present."""
        errors = []
        if not self.twilio_account_sid:
            errors.append("Missing required env: TWILIO_ACCOUNT_SID")
        if not self.twilio_auth_token:
            errors.append("Missing required env: TWILIO_AUTH_TOKEN")
        if not self.twilio_sms_number:
            errors.append("Missing required env: TWILIO_SMS_NUMBER")
        return errors

    @classmethod
    def from_env(cls) -> "TwilioAdapterConfig":
        """Create config from environment variables."""
        return cls()


# Global config instance (lazy loaded)
_config: Optional[TwilioAdapterConfig] = None


def get_config() -> TwilioAdapterConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = TwilioAdapterConfig.from_env()
    return _config

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "API-OPER-019",
    "component_name": "Config",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:13Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "api_gateway",
    "type": "schema",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Implements TwilioAdapterConfig for config functionality",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
