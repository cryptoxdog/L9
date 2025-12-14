"""
L9 Unified Integration Toggle Settings
Version: 1.0.0

Centralized configuration for all external integrations.
All integrations can be toggled on/off via environment variables.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class IntegrationSettings(BaseSettings):
    """
    Configuration for L9 external integrations.
    
    Environment variables:
    - SLACK_APP_ENABLED: Enable Slack integration (default: false)
    - MAC_AGENT_ENABLED: Enable Mac Agent integration (default: false)
    - EMAIL_ENABLED: Enable Email integration (default: false)
    - INBOX_PARSER_ENABLED: Enable Inbox Parser integration (default: false)
    - TWILIO_ENABLED: Enable Twilio integration (default: false)
    - WABA_ENABLED: Enable WABA integration (default: false)
    """
    
    # Integration toggles
    slack_app_enabled: bool = Field(
        default=False,
        alias="SLACK_APP_ENABLED",
        description="Enable Slack Events API integration"
    )
    
    mac_agent_enabled: bool = Field(
        default=False,
        alias="MAC_AGENT_ENABLED",
        description="Enable Mac Agent task execution"
    )
    
    email_enabled: bool = Field(
        default=False,
        alias="EMAIL_ENABLED",
        description="Enable Email integration"
    )
    
    inbox_parser_enabled: bool = Field(
        default=False,
        alias="INBOX_PARSER_ENABLED",
        description="Enable Inbox Parser integration"
    )
    
    twilio_enabled: bool = Field(
        default=False,
        alias="TWILIO_ENABLED",
        description="Enable Twilio SMS/WhatsApp integration"
    )
    
    waba_enabled: bool = Field(
        default=False,
        alias="WABA_ENABLED",
        description="Enable WABA (WhatsApp Business Account) integration"
    )
    
    # Storage configuration
    l9_data_root: str = Field(
        default=os.path.expanduser("~/.l9"),
        alias="L9_DATA_ROOT",
        description="Root directory for L9 data storage"
    )
    
    slack_files_dir: str = Field(
        default="",  # Will be computed from l9_data_root
        alias="SLACK_FILES_DIR",
        description="Directory for Slack file storage (auto-computed if not set)"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Singleton instance
_settings: IntegrationSettings | None = None


def get_integration_settings() -> IntegrationSettings:
    """Get or create integration settings singleton."""
    global _settings
    if _settings is None:
        _settings = IntegrationSettings()
    return _settings


def reset_integration_settings() -> None:
    """Reset settings (useful for testing)."""
    global _settings
    _settings = None


# Convenience accessor
settings = get_integration_settings()


def get_slack_files_dir() -> str:
    """
    Get the Slack files directory path.
    
    Uses SLACK_FILES_DIR if set, otherwise computes from L9_DATA_ROOT.
    Directory structure: ~/.l9/slack_files/
    
    Returns:
        Absolute path to Slack files directory
    """
    integration_settings = get_integration_settings()
    
    # If explicitly set, use it
    if integration_settings.slack_files_dir:
        return os.path.abspath(os.path.expanduser(integration_settings.slack_files_dir))
    
    # Otherwise compute from L9_DATA_ROOT
    data_root = os.path.abspath(os.path.expanduser(integration_settings.l9_data_root))
    slack_files_dir = os.path.join(data_root, "slack_files")
    
    # Ensure directory exists
    Path(slack_files_dir).mkdir(parents=True, exist_ok=True)
    
    return slack_files_dir
