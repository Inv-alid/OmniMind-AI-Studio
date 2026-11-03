from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

from app.core.agent_swarm import swarm
from app.core.router import router, ChatMessage, GenerationConfig

router_api = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"
    model: str = "claude-3-5-sonnet-20241022"
    enable_swarm: bool = True
    battle_mode: bool = False
    battle_models: Optional[list[str]] = None


@router_api.post("/")
async def chat(request: ChatRequest):
    if request.battle_mode:
        models = request.battle_models or ["gpt-4o", "claude-3-5-sonnet-20241022", "grok-2"]
        messages = [ChatMessage(role="user", content=request.message)]
        results = await router.battle(messages, models)
        return {"type": "battle", "results": results}

    async def event_generator():
        try:
            async for event in swarm.process(
                user_message=request.message,
                conversation_id=request.conversation_id,
                preferred_model=request.model,
                enable_swarm=request.enable_swarm,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
