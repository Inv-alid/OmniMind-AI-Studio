from typing import AsyncIterator, Dict, Any
from .base_agent import BaseAgent


class DataAnalystAgent(BaseAgent):
    name = "data_analyst"
    description = "Processes CSV, JSON, databases, performs analysis and generates insights + charts descriptions."
    default_model = "gpt-4o"

    async def run(self, prompt: str, context: Dict[str, Any] | None = None) -> AsyncIterator[dict]:
        system = """You are Data Analyst Agent.
You are expert in data analysis, statistics, pandas, SQL, visualization recommendations.
When given data, you clean it, explore it, find insights and suggest visualizations.
Provide clear, actionable conclusions and Python code examples when useful."""

        yield {"type": "status", "content": "Data Analyst is processing..."}
        async for event in self._stream_llm(system, prompt, temperature=0.35):
            yield event
