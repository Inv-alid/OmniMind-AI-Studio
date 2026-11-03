from typing import AsyncIterator, List
import httpx
import json
from loguru import logger

from .base import BaseLLMProvider, ChatMessage, GenerationConfig


class AnthropicProvider(BaseLLMProvider):
    name = "anthropic"
    models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
    ]
    supports_vision = True
    supports_tools = True

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1"

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        config: GenerationConfig,
    ) -> AsyncIterator[str]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        # Convert messages format
        system = None
        anthropic_messages = []
        for m in messages:
            if m.role == "system":
                system = m.content if isinstance(m.content, str) else str(m.content)
            else:
                anthropic_messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "stream": config.stream,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120.0) as client:
            if config.stream:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload,
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            try:
                                chunk = json.loads(data)
                                if chunk.get("type") == "content_block_delta":
                                    delta = chunk.get("delta", {})
                                    text = delta.get("text")
                                    if text:
                                        yield text
                            except Exception:
                                continue
            else:
                resp = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        yield block.get("text", "")
