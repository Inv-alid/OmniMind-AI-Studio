from typing import AsyncIterator, List
import httpx
import json
from loguru import logger

from .base import BaseLLMProvider, ChatMessage, GenerationConfig


class DeepSeekProvider(BaseLLMProvider):
    name = "deepseek"
    models = [
        "deepseek-chat",
        "deepseek-reasoner",
        "deepseek-v3",
        "deepseek-r1",
    ]
    supports_vision = False
    supports_tools = True

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com"

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
