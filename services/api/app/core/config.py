from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MANSI_", extra="ignore")

    environment: str = Field(default="development", pattern="^(development|test|staging|production)$")
    service_name: str = "mansi-api"
    api_prefix: str = "/v1"
    allowed_origins: list[AnyHttpUrl] = []
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    redis_url: str | None = None
    auth_jwt_secret: str | None = None
    stream_token_ttl_seconds: int = Field(default=3600, ge=60, le=86_400)


@lru_cache
def get_settings() -> Settings:
    return Settings()
