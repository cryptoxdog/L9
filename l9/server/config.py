from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    orchestrator_api_key: str
    agent_auth_token: str
    hmac_secret: str

    allowed_origins: list[AnyHttpUrl] = []

    class Config:
        env_prefix = "L9_"
        env_file = ".env"


settings = Settings()

