import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server
    MCP_HOST: str = "127.0.0.1"
    MCP_PORT: int = 9001
    MCP_ENV: str = "production"
    LOG_LEVEL: str = "INFO"

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_EMBED_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBED_DIM: int = 1536

    # PostgreSQL (same Postgres instance L9 uses, but l9memory DB)
    MEMORY_DSN: str

    # Memory lifecycle
    MEMORY_SHORTTERM_HOURS: int = 1
    MEMORY_MEDIUMTERM_HOURS: int = 24
    MEMORY_CLEANUP_INTERVAL_MINUTES: int = 60
    MEMORY_SHORT_RETENTION_DAYS: int = 7
    MEMORY_MEDIUM_RETENTION_DAYS: int = 30

    # Vector search
    VECTOR_SEARCH_THRESHOLD: float = 0.7
    VECTOR_SEARCH_TOP_K: int = 10

    # MCP auth
    MCP_API_KEY: str

    # User identification for memory namespacing
    USER_ID: str = "default"
    CURSOR_USERNAME: str = "cursor"

    # Optional: Postgres password (used in MEMORY_DSN interpolation)
    POSTGRES_PASSWORD: str = ""

    # Optional Redis embedding cache (not used yet; for future)
    REDIS_ENABLED: bool = False
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379

    class Config:
        env_file = ".env.cursor"
        extra = "ignore"


settings = Settings()

