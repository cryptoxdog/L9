"""
Configuration for L9 MCP Memory Server.
Environment-based settings with HNSW and memory compounding support.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server Configuration
    # Bind to 0.0.0.0 for Caddy reverse proxy (Cloudflare → Caddy:443 → MCP:9001)
    # Public URL: https://l9.quantumaipartners.com (Caddy routes /mcp/* to this server)
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 9001
    MCP_ENV: str = "production"
    LOG_LEVEL: str = "INFO"

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_EMBED_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBED_DIM: int = 1536

    # Database Configuration
    MEMORY_DSN: str

    # Memory Lifecycle
    MEMORY_SHORT_TERM_HOURS: int = 24
    MEMORY_MEDIUM_TERM_HOURS: int = 168
    MEMORY_CLEANUP_INTERVAL_MINUTES: int = 720
    MEMORY_SHORT_RETENTION_DAYS: int = 14
    MEMORY_MEDIUM_RETENTION_DAYS: int = 30

    # Vector Search Configuration
    VECTOR_SEARCH_THRESHOLD: float = 0.7
    VECTOR_SEARCH_TOP_K: int = 10

    # Vector Index Configuration (HNSW)
    VECTOR_INDEX_TYPE: str = "hnsw"
    HNSW_M: int = 16
    HNSW_EF_CONSTRUCTION: int = 64
    HNSW_EF_SEARCH: int = 40

    # Memory Compounding Configuration
    COMPOUNDING_ENABLED: bool = True
    COMPOUNDING_SIMILARITY_THRESHOLD: float = 0.92
    COMPOUNDING_MIN_COUNT: int = 3

    # Importance Decay Configuration
    DECAY_ENABLED: bool = True
    DECAY_RATE_PER_DAY: float = 0.01
    ACCESS_BOOST_PER_HIT: float = 0.05

    # Authentication - Dual API Keys for L and C
    # See: mcp_memory/memory-setup-instructions.md for governance spec
    # - MCP_API_KEY_L: L-CTO kernel (full read/write/delete)
    # - MCP_API_KEY_C: Cursor IDE (read all, write/delete own only)
    MCP_API_KEY_L: str  # L-CTO API key
    MCP_API_KEY_C: str  # Cursor IDE API key

    # Shared User Identity (L and C operate in same semantic space)
    # Separation is enforced via metadata.creator and caller identity
    # See: memory-setup-instructions.md → userid_strategy
    L_CTO_USER_ID: str = "l9-shared"  # Shared userid for L + Cursor collaboration

    # Redis (optional)
    REDIS_ENABLED: bool = False
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
