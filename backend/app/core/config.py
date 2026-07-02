from __future__ import annotations

from functools import lru_cache
from pydantic import Field
try:
    from pydantic_settings import BaseSettings
except Exception:  # pragma: no cover - keeps deterministic core tests light
    from pydantic import BaseModel as BaseSettings


class Settings(BaseSettings):
    app_name: str = "WorkflowOps AI"
    environment: str = "local"
    database_url: str = "sqlite:///./workflowops.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = Field(default="change-me-in-production")
    jwt_expire_minutes: int = 1440
    llm_provider: str = "mock"
    openai_api_key: str | None = None
    auto_create_tables: bool = True
    local_sync_worker: bool = True
    max_upload_mb: int = 10
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    ollama_base_url: str = "http://localhost:11434"
    demo_mode: bool = True
    max_workflow_cost_usd: float = 2.0
    workflow_timeout_seconds: int = 180

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
