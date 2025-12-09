from pydantic import BaseSettings


class AgentSettings(BaseSettings):
    agent_id: str = "mac-001"
    orchestrator_ws_url: str
    agent_auth_token: str

    class Config:
        env_prefix = "L9_AGENT_"
        env_file = ".env"


settings = AgentSettings()

