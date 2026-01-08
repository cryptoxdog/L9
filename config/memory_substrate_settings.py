"""
L9 Memory Substrate - Configuration Settings
Version: 1.0.0

Pydantic settings for environment variables and configuration.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class MemorySubstrateSettings(BaseSettings):
    """
    Configuration for the Memory Substrate module.

    Environment variables:
    - DATABASE_URL: Postgres DSN with pgvector extension enabled (required)
    - EMBEDDING_MODEL: Embedding model name (optional, default: text-embedding-3-large)
    - OPENAI_API_KEY: Required for embedding generation
    """

    # Database
    database_url: str = Field(
        ...,
        alias="DATABASE_URL",
        description="Postgres DSN with pgvector extension enabled",
    )

    # Embedding configuration
    embedding_model: str = Field(
        default="text-embedding-3-large",
        alias="EMBEDDING_MODEL",
        description="Embedding model name",
    )
    embedding_dimensions: int = Field(
        default=1536, description="Embedding vector dimensions (must match model)"
    )

    # OpenAI API (for embeddings)
    openai_api_key: Optional[str] = Field(
        default=None,
        alias="OPENAI_API_KEY",
        description="OpenAI API key for embedding generation",
    )

    # API configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8080, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1/memory", alias="API_PREFIX")

    # Substrate namespace
    namespace: str = Field(
        default="plasticos",
        alias="SUBSTRATE_NAMESPACE",
        description="Namespace for memory isolation",
    )

    # Performance tuning
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")

    # Sync configuration
    sync_interval_minutes: int = Field(
        default=10,
        alias="SYNC_INTERVAL_MINUTES",
        description="Interval for background sync to external systems",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Singleton instance
_settings: Optional[MemorySubstrateSettings] = None


def get_settings() -> MemorySubstrateSettings:
    """Get or create settings singleton."""
    global _settings
    if _settings is None:
        _settings = MemorySubstrateSettings()
    return _settings


def reset_settings() -> None:
    """Reset settings (useful for testing)."""
    global _settings
    _settings = None

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "CON-OPER-001",
    "component_name": "Memory Substrate Settings",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "config",
    "type": "utility",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Provides memory substrate settings components including MemorySubstrateSettings, Config",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
