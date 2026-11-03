from __future__ import annotations
import asyncio
import uuid
import json
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from .router import router, ChatMessage, GenerationConfig
from .agents.base_agent import BaseAgent
from .agents.code_architect import CodeArchitectAgent
from .agents.research_agent import ResearchAgent
from .agents.data_analyst import DataAnalystAgent
from .agents.creative_vision import CreativeVisionAgent
from .rag.memory import MemoryManager


class AgentRole(str, Enum):
    CODE = "code_architect"
    RESEARCH = "research"
    DATA = "data_analyst"
    CREATIVE = "creative_vision"
    ORCHESTRATOR = "orchestrator"


class AgentTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: AgentRole
    prompt: str
    context: Dict[str, Any] = {}
    status: str = "pending"
    result: Optional[str] = None


class SwarmOrchestrator:
    """
    Hierarchical Multi-Agent Swarm Orchestrator.
    Automatically decomposes user requests and distributes work
    across specialized sub-agents, then synthesizes the final answer.
    """

    def __init__(self):
        self.agents: Dict[AgentRole, BaseAgent] = {
            AgentRole.CODE: CodeArchitectAgent(),
            AgentRole.RESEARCH: ResearchAgent(),
            AgentRole.DATA: DataAnalystAgent(),
            AgentRole.CREATIVE: CreativeVisionAgent(),
        }
        self.memory = MemoryManager()
        self.active_tasks: Dict[str, AgentTask] = {}

    async def process(
        self,
        user_message: str,
        conversation_id: str = "default",
        preferred_model: str = "claude-3-5-sonnet-20241022",
        enable_swarm: bool = True,
    ) -> AsyncIterator[dict]:
        history = await self.memory.get_history(conversation_id, limit=10)
        rag_context = await self.memory.semantic_search(user_message, top_k=4)

        system_prompt = self._build_system_prompt(rag_context)
        messages = [
            ChatMessage(role="system", content=system_prompt),
            *history,
            ChatMessage(role="user", content=user_message),
        ]

        if not enable_swarm:
            async for chunk in router.chat(messages, preferred_model):
                yield {"type": "token", "content": chunk}
            full = ""
            # (streaming already yielded)
            await self.memory.add_message(conversation_id, "user", user_message)
            return

        # Planning step
        plan = await self._create_execution_plan(user_message, preferred_model)
        yield {"type": "plan", "content": plan}

        if plan.get("use_single_agent", True):
            role_str = plan.get("primary_agent", "code_architect")
            try:
                role = AgentRole(role_str)
            except ValueError:
                role = AgentRole.CODE

            agent = self.agents[role]
            yield {"type": "agent_status", "agent": role.value, "status": "running"}

            result_parts = []
            async for event in agent.run(user_message, context={"history": history}):
                if event.get("type") == "token":
                    result_parts.append(event["content"])
                yield event

            yield {"type": "agent_status", "agent": role.value, "status": "completed"}

            final = "".join(result_parts)
            await self.memory.add_message(conversation_id, "user", user_message)
            await self.memory.add_message(conversation_id, "assistant", final)
            yield {"type": "final", "content": final}
            return

        # Multi-agent parallel execution
        tasks = []
        for step in plan.get("steps", []):
            try:
                role = AgentRole(step["agent"])
            except (ValueError, KeyError):
                continue
            task = AgentTask(role=role, prompt=step.get("prompt", user_message))
            self.active_tasks[task.id] = task
            tasks.append(self._run_agent_task(task))

        if not tasks:
            # Fallback
            async for chunk in router.chat(messages, preferred_model):
                yield {"type": "token", "content": chunk}
            return

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Synthesis
        synthesis_prompt = self._build_synthesis_prompt(user_message, results)
        synth_messages = messages + [ChatMessage(role="user", content=synthesis_prompt)]

        yield {"type": "agent_status", "agent": "orchestrator", "status": "synthesizing"}

        final_chunks = []
        async for chunk in router.chat(synth_messages, preferred_model, GenerationConfig(temperature=0.35)):
            final_chunks.append(chunk)
            yield {"type": "token", "content": chunk}

        final = "".join(final_chunks)
        await self.memory.add_message(conversation_id, "user", user_message)
        await self.memory.add_message(conversation_id, "assistant", final)
        yield {"type": "final", "content": final}

    async def _create_execution_plan(self, query: str, model: str) -> dict:
        planner_prompt = f"""You are the master orchestrator of OmniMind AI Studio.
Analyze the user request and return a JSON execution plan.

Available specialized agents:
- code_architect: writing, reviewing, testing, executing code in sandbox
- research: web search, documentation, up-to-date information
- data_analyst: CSV/JSON/databases, analysis, charts
- creative_vision: image generation, vision analysis, multimodal tasks

User request: {query}

Return ONLY valid JSON (no markdown):
{{
  "use_single_agent": true or false,
  "primary_agent": "code_architect" | "research" | "data_analyst" | "creative_vision",
  "steps": [
    {{"agent": "...", "prompt": "specific sub-task"}}
  ],
  "reasoning": "short explanation"
}}"""

        messages = [ChatMessage(role="user", content=planner_prompt)]
        full = ""
        try:
            async for chunk in router.chat(messages, model, GenerationConfig(temperature=0.15, max_tokens=800)):
                full += chunk

            start = full.find("{")
            end = full.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(full[start:end])
        except Exception as e:
            logger.warning(f"Planner failed: {e}")

        return {
            "use_single_agent": True,
            "primary_agent": "code_architect",
            "steps": [],
            "reasoning": "Fallback to single agent",
        }

    async def _run_agent_task(self, task: AgentTask) -> AgentTask:
        task.status = "running"
        agent = self.agents.get(task.role)
        if not agent:
            task.status = "failed"
            task.result = "Agent not found"
            return task

        try:
            result_parts = []
            async for event in agent.run(task.prompt, context=task.context):
                if event.get("type") == "token":
                    result_parts.append(event["content"])
            task.result = "".join(result_parts)
            task.status = "completed"
        except Exception as e:
            task.status = "failed"
            task.result = str(e)
            logger.exception(f"Agent {task.role} failed")
        return task

    def _build_system_prompt(self, rag_context: list) -> str:
        ctx = "\n\n".join([c.get("text", "") for c in rag_context]) if rag_context else "No additional context."
        return f"""You are OmniMind AI Studio — the ultimate desktop AI assistant with multi-agent capabilities.
Use the provided local memory / RAG context when relevant.

Context from memory:
{ctx}
"""

    def _build_synthesis_prompt(self, original: str, results: list) -> str:
        parts = []
        for r in results:
            if isinstance(r, AgentTask) and r.result:
                parts.append(f"### Agent: {r.role.value}\n{r.result}\n")
            elif isinstance(r, Exception):
                parts.append(f"### Error\n{str(r)}\n")
        return f"""Original user request:
{original}

Results from specialized agents:
{chr(10).join(parts)}

Synthesize a final, coherent, high-quality response. Remove duplication, keep important code and details, structure the answer clearly."""


# Global instance
swarm = SwarmOrchestrator()
