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
#     "file": "config.py",
# }
# ══════════════════════════════════════════════════════════════════════════════

"""
Slack Webhook Adapter Configuration
────────────────────────────────────
Environment-driven configuration for Slack Webhook Adapter.

Auto-generated from Module-Spec v2.6.0
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SlackWebhookConfig:
    """Configuration for Slack Webhook Adapter."""
    
    # Required environment variables (using existing env.example naming)
    slack_signing_secret: str = field(default_factory=lambda: os.environ.get("SLACK_SIGNING_SECRET", ""))
    slack_bot_token: str = field(default_factory=lambda: os.environ.get("SLACK_BOT_TOKEN", ""))
    
    # Optional environment variables
    slack_app_enabled: Optional[str] = field(default_factory=lambda: os.environ.get("SLACK_APP_ENABLED"))
    slack_webhook_log_level: Optional[str] = field(default_factory=lambda: os.environ.get("SLACK_WEBHOOK_LOG_LEVEL"))
    
    # Module settings
    module_id: str = "slack.webhook"
    module_name: str = "Slack Webhook Adapter"
    enabled: bool = True
    
    # Timeouts
    default_timeout_seconds: int = 30
    aios_timeout_seconds: int = 60
    slack_post_timeout_seconds: int = 10
    
    # Idempotency
    dedupe_cache_ttl_seconds: int = 86400
    
    # Timestamp validation (Slack recommends 5 minutes)
    timestamp_tolerance_seconds: int = 300
    
    def validate(self) -> list[str]:
        """Validate required configuration is present."""
        errors = []
        if not self.slack_signing_secret:
            errors.append("Missing required env: SLACK_SIGNING_SECRET")
        if not self.slack_bot_token:
            errors.append("Missing required env: SLACK_BOT_TOKEN")
        return errors
    
    @classmethod
    def from_env(cls) -> "SlackWebhookConfig":
        """Create config from environment variables."""
        return cls()


# Global config instance (lazy loaded)
_config: Optional[SlackWebhookConfig] = None


def get_config() -> SlackWebhookConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = SlackWebhookConfig.from_env()
    return _config

