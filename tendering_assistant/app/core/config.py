from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "anthropic"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-opus-4-8"

    # Tender source connectors are disabled until their base URL is set.
    # Each portal needs its own auth/credentials handled inside its connector.
    gem_api_base_url: str | None = None
    cppp_eprocure_api_base_url: str | None = None
    state_procurement_api_base_url: str | None = None
    psu_portal_api_base_url: str | None = None
    railways_api_base_url: str | None = None
    defence_api_base_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
