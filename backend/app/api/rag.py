from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import List
import uuid

from app.core.rag.memory import MemoryManager

router = APIRouter()
memory = MemoryManager()


class IndexRequest(BaseModel):
    texts: List[str]
    conversation_id: str = "default"


@router.post("/index")
async def index_documents(req: IndexRequest):
    ids = [f"doc_{uuid.uuid4().hex[:10]}" for _ in req.texts]
    memory.store.add(ids=ids, documents=req.texts)
    return {"indexed": len(req.texts), "ids": ids}


@router.get("/search")
async def search(q: str, top_k: int = 5):
    results = await memory.semantic_search(q, top_k=top_k)
    return {"results": results}
