import json

import httpx

from app.core.config import settings
from app.llm.base import ChatMessage, LLMProvider


class OpenAIProvider:
    """Chat-completions compatible provider for OpenAI and OpenRouter."""

    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self.base_url = settings.llm_base_url.rstrip("/")
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key

        if self.provider == "openrouter":
            self.base_url = "https://openrouter.ai/api/v1"
            self.model = settings.openrouter_model or settings.openai_model
            self.api_key = settings.openrouter_api_key

    async def complete(self, prompt: str) -> str:
        response = await self._create_chat_completion(
            [{"role": "user", "content": prompt}],
            json_response=False,
        )
        return response["choices"][0]["message"]["content"]

    async def chat_json(self, messages: list[ChatMessage]) -> dict:
        response = await self._create_chat_completion(messages, json_response=True)
        content = response["choices"][0]["message"]["content"]

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned invalid JSON.") from exc

    async def _create_chat_completion(
        self,
        messages: list[ChatMessage],
        json_response: bool,
    ) -> dict:
        if not self.api_key:
            raise ValueError(f"Missing API key for LLM provider: {self.provider}")

        payload: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
        }

        if json_response:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()


def get_llm_provider() -> LLMProvider:
    return OpenAIProvider()
