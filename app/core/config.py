from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-5-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    database_url: str = "postgresql+asyncpg://opsmind:opsmind@localhost:5432/opsmind"
    redis_url: str = "redis://localhost:6379/0"
    otel_exporter_endpoint: str | None = None
    rag_top_k: int = 8
    conversation_ttl_seconds: int = 3600

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
