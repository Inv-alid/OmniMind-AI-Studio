from typing import AsyncIterator, List
import httpx
import json
from loguru import logger

from .base import BaseLLMProvider, ChatMessage, GenerationConfig


class LocalProvider(BaseLLMProvider):
    name = "local"
    models = [
        "llama3.3",
        "llama3.2",
        "mistral",
        "qwen2.5",
        "phi3",
        "gemma2",
        "deepseek-r1:local",
    ]
    supports_vision = False
    supports_tools = False

    def __init__(self, ollama_url: str, lmstudio_url: str, llamacpp_url: str):
        self.ollama_url = ollama_url.rstrip("/")
        self.lmstudio_url = lmstudio_url.rstrip("/")
        self.llamacpp_url = llamacpp_url.rstrip("/")

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        config: GenerationConfig,
    ) -> AsyncIterator[str]:
        # Prefer Ollama OpenAI-compatible endpoint
        url = f"{self.ollama_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "stream": config.stream,
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                if config.stream:
                    async with client.stream("POST", url, headers=headers, json=payload) as resp:
                        if resp.status_code == 200:
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
                            return
            except Exception as e:
                logger.warning(f"Ollama failed: {e}, trying LM Studio...")

            # Fallback to LM Studio
            url = f"{self.lmstudio_url}/chat/completions"
            try:
                if config.stream:
                    async with client.stream("POST", url, headers=headers, json=payload) as resp:
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
            except Exception as e:
                logger.error(f"Local providers failed: {e}")
                yield f"[Local runtime error: {str(e)}. Make sure Ollama or LM Studio is running.]"
