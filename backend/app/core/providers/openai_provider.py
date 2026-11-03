from typing import AsyncIterator, List
import httpx
from loguru import logger

from .base import BaseLLMProvider, ChatMessage, GenerationConfig


class OpenAIProvider(BaseLLMProvider):
    name = "openai"
    models = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4.5-preview",
        "o1",
        "o1-mini",
        "o3-mini",
        "gpt-4-turbo",
    ]
    supports_vision = True
    supports_tools = True

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        config: GenerationConfig,
    ) -> AsyncIterator[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "stream": config.stream,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            if config.stream:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data.strip() == "[DONE]":
                                break
                            try:
                                import json
                                chunk = json.loads(data)
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    yield content
                            except Exception:
                                continue
            else:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                yield data["choices"][0]["message"]["content"]
