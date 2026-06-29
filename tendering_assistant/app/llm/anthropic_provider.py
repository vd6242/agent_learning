from typing import Any

import anthropic

from app.core.config import Settings
from app.llm.base import LLMProvider
from app.llm.errors import LLMConfigurationError


class AnthropicProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        if not settings.anthropic_api_key:
            raise LLMConfigurationError(
                "ANTHROPIC_API_KEY is not set; configure it to use the Claude provider."
            )
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model

    async def extract_structured(
        self,
        *,
        system_prompt: str,
        user_content: str,
        json_schema: dict[str, Any],
        schema_name: str,
    ) -> dict[str, Any]:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "json_schema": {"name": schema_name, "schema": json_schema},
                }
            },
        )
        return _parse_json_text(response)

    async def generate_text(self, *, system_prompt: str, user_content: str) -> str:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        return "".join(block.text for block in response.content if block.type == "text")


def _parse_json_text(response: Any) -> dict[str, Any]:
    import json

    text = "".join(block.text for block in response.content if block.type == "text")
    return json.loads(text)
