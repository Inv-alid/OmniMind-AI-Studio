from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any
from app.core.router import router, ChatMessage, GenerationConfig


class BaseAgent(ABC):
    name: str
    description: str
    default_model: str = "claude-3-5-sonnet-20241022"

    @abstractmethod
    async def run(self, prompt: str, context: Dict[str, Any] | None = None) -> AsyncIterator[dict]:
        """Yield events: {type: 'token'|'status'|'tool', content: ...}"""
        ...

    async def _stream_llm(
        self,
        system: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.5,
    ) -> AsyncIterator[dict]:
        model = model or self.default_model
        messages = [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=user_prompt),
        ]
        async for chunk in router.chat(
            messages, model, GenerationConfig(temperature=temperature)
        ):
            yield {"type": "token", "content": chunk}
