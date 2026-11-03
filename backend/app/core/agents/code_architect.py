from typing import AsyncIterator, Dict, Any
from .base_agent import BaseAgent


class CodeArchitectAgent(BaseAgent):
    name = "code_architect"
    description = "Writes, reviews, tests and reasons about code. Architecture & implementation expert."
    default_model = "claude-3-5-sonnet-20241022"

    async def run(self, prompt: str, context: Dict[str, Any] | None = None) -> AsyncIterator[dict]:
        system = """You are CodeArchitect Agent — elite software engineer and system architect.
You write clean, production-ready, well-commented code.
You think about architecture, edge cases, performance and security.
When asked to implement something, provide complete, working solutions.
Prefer modern best practices (type hints, async, clean architecture).
Respond in the language of the user's request."""

        yield {"type": "status", "content": "CodeArchitect is designing solution..."}
        async for event in self._stream_llm(system, prompt, temperature=0.3):
            yield event
