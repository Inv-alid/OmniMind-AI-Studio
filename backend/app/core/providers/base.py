from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, List, Any
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str | list


class GenerationConfig(BaseModel):
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = True
    tools: Optional[list] = None


class BaseLLMProvider(ABC):
    name: str
    models: List[str]
    supports_vision: bool = False
    supports_tools: bool = True

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        config: GenerationConfig,
    ) -> AsyncIterator[str]:
        ...

    async def embed(self, texts: List[str], model: str = "default") -> List[List[float]]:
        raise NotImplementedError

    async def health_check(self) -> bool:
        return True
