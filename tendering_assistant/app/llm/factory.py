from functools import lru_cache

from app.core.config import Settings, get_settings
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.base import LLMProvider

_PROVIDERS = {
    "anthropic": AnthropicProvider,
}


@lru_cache
def get_llm_provider() -> LLMProvider:
    settings: Settings = get_settings()
    provider_cls = _PROVIDERS.get(settings.llm_provider)
    if provider_cls is None:
        raise ValueError(f"Unknown LLM_PROVIDER '{settings.llm_provider}'")
    return provider_cls(settings)
