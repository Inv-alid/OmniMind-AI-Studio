from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api import chat, models, agents, rag
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="OmniMind AI Studio",
    version="1.0.0",
    description="Ultimate Multi-Agent Desktop AI Command Center",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])


@app.on_event("startup")
async def startup():
    logger.info("OmniMind AI Studio backend started")
    logger.info(f"Available providers will be loaded on first request")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "OmniMind AI Studio"}
