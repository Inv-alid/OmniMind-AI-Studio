from typing import AsyncIterator, Dict, Any
from .base_agent import BaseAgent


class CreativeVisionAgent(BaseAgent):
    name = "creative_vision"
    description = "Multimodal tasks, image generation prompts, visual analysis, creative writing."
    default_model = "gpt-4o"

    async def run(self, prompt: str, context: Dict[str, Any] | None = None) -> AsyncIterator[dict]:
        system = """You are Creative & Vision Agent.
You handle image generation prompt engineering (DALL-E, Midjourney, Flux, SD), visual analysis,
creative writing, storytelling and multimodal reasoning.
Craft highly detailed, effective prompts for image models and provide artistic direction."""

        yield {"type": "status", "content": "Creative Vision Agent is working..."}
        async for event in self._stream_llm(system, prompt, temperature=0.7):
            yield event
