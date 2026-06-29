from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Provider-agnostic interface for the AI features in this app.

    Concrete providers (Claude, OpenAI, etc.) implement this so the rest of
    the codebase never imports a vendor SDK directly.
    """

    @abstractmethod
    async def extract_structured(
        self,
        *,
        system_prompt: str,
        user_content: str,
        json_schema: dict[str, Any],
        schema_name: str,
    ) -> dict[str, Any]:
        """Return a dict matching json_schema, extracted from user_content."""

    @abstractmethod
    async def generate_text(self, *, system_prompt: str, user_content: str) -> str:
        """Return a free-text completion (used for draft bid text, etc.)."""
