from typing import AsyncIterator, Dict, Any
from .base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    name = "research"
    description = "Gathers up-to-date information, documentation, scientific papers and web knowledge."
    default_model = "gpt-4o"

    async def run(self, prompt: str, context: Dict[str, Any] | None = None) -> AsyncIterator[dict]:
        system = """You are Research & Web Search Agent.
You excel at gathering accurate, up-to-date information, summarizing documentation,
comparing technologies and providing well-structured research reports.
Always cite sources when possible and distinguish between facts and speculation.
Be thorough but concise."""

        yield {"type": "status", "content": "Research Agent is gathering information..."}
        async for event in self._stream_llm(system, prompt, temperature=0.4):
            yield event
