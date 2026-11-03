from typing import AsyncIterator, List
import httpx
import json
from loguru import logger

from .base import BaseLLMProvider, ChatMessage, GenerationConfig


class GoogleProvider(BaseLLMProvider):
    name = "google"
    models = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro-latest",
    ]
    supports_vision = True
    supports_tools = True

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        config: GenerationConfig,
    ) -> AsyncIterator[str]:
        # Convert to Gemini format
        contents = []
        for m in messages:
            role = "user" if m.role in ("user", "system") else "model"
            contents.append({
                "role": role,
                "parts": [{"text": m.content if isinstance(m.content, str) else str(m.content)}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": config.temperature,
                "maxOutputTokens": config.max_tokens,
            },
        }

        url = f"{self.base_url}/models/{model}:streamGenerateContent?key={self.api_key}&alt=sse"

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        try:
                            chunk = json.loads(data)
                            candidates = chunk.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for part in parts:
                                    text = part.get("text")
                                    if text:
                                        yield text
                        except Exception:
                            continue
