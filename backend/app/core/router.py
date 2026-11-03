from __future__ import annotations
import asyncio
from typing import AsyncIterator, Dict, Optional, List
from loguru import logger

from .config import get_settings
from .providers.base import BaseLLMProvider, ChatMessage, GenerationConfig
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.google_provider import GoogleProvider
from .providers.xai_provider import XAIProvider
from .providers.deepseek_provider import DeepSeekProvider
from .providers.local_provider import LocalProvider


class ModelRouter:
    """
    Universal asynchronous LLM Router.
    Dynamically connects to all major providers + local runtimes.
    """

    def __init__(self):
        self.settings = get_settings()
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._model_to_provider: Dict[str, str] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        if self.settings.openai_api_key:
            p = OpenAIProvider(api_key=self.settings.openai_api_key)
            self.providers["openai"] = p
            for m in p.models:
                self._model_to_provider[m] = "openai"

        if self.settings.anthropic_api_key:
            p = AnthropicProvider(api_key=self.settings.anthropic_api_key)
            self.providers["anthropic"] = p
            for m in p.models:
                self._model_to_provider[m] = "anthropic"

        if self.settings.google_api_key:
            p = GoogleProvider(api_key=self.settings.google_api_key)
            self.providers["google"] = p
            for m in p.models:
                self._model_to_provider[m] = "google"

        if self.settings.xai_api_key:
            p = XAIProvider(api_key=self.settings.xai_api_key)
            self.providers["xai"] = p
            for m in p.models:
                self._model_to_provider[m] = "xai"

        if self.settings.deepseek_api_key:
            p = DeepSeekProvider(api_key=self.settings.deepseek_api_key)
            self.providers["deepseek"] = p
            for m in p.models:
                self._model_to_provider[m] = "deepseek"

        # Local always available
        local = LocalProvider(
            ollama_url=self.settings.ollama_base_url,
            lmstudio_url=self.settings.lmstudio_base_url,
            llamacpp_url=self.settings.llamacpp_base_url,
        )
        self.providers["local"] = local
        for m in local.models:
            self._model_to_provider[m] = "local"

        logger.info(f"Router ready. Providers: {list(self.providers.keys())}")

    def list_models(self) -> List[dict]:
        result = []
        for name, provider in self.providers.items():
            for model in provider.models:
                result.append({
                    "id": model,
                    "provider": name,
                    "supports_vision": getattr(provider, "supports_vision", False),
                    "supports_tools": getattr(provider, "supports_tools", True),
                })
        return result

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        config: Optional[GenerationConfig] = None,
    ) -> AsyncIterator[str]:
        config = config or GenerationConfig()
        provider_name = self._model_to_provider.get(model)
        if not provider_name:
            # Try fuzzy match for local models
            for m, p in self._model_to_provider.items():
                if model in m or m in model:
                    provider_name = p
                    model = m
                    break
        if not provider_name:
            raise ValueError(f"Model '{model}' not found. Available: {list(self._model_to_provider.keys())}")

        provider = self.providers[provider_name]
        logger.debug(f"Routing {model} → {provider_name}")

        async for chunk in provider.chat(messages, model, config):
            yield chunk

    async def battle(
        self,
        messages: List[ChatMessage],
        models: List[str],
        config: Optional[GenerationConfig] = None,
    ) -> Dict[str, str]:
        """Parallel multi-model battle mode"""
        config = config or GenerationConfig(stream=False)
        tasks = {}

        async def collect(m: str) -> str:
            chunks = []
            try:
                async for c in self.chat(messages, m, config):
                    chunks.append(c)
                return "".join(chunks)
            except Exception as e:
                return f"[Error from {m}: {str(e)}]"

        for model in models:
            tasks[model] = asyncio.create_task(collect(model))

        results = {}
        for model, task in tasks.items():
            results[model] = await task
        return results


# Global singleton
router = ModelRouter()
