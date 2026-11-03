from typing import List, Dict, Any
import uuid
from datetime import datetime
from loguru import logger

from .vector_store import VectorStore
from app.core.providers.base import ChatMessage


class MemoryManager:
    """Conversation history + long-term semantic memory via ChromaDB"""

    def __init__(self):
        self.store = VectorStore()
        self._history: Dict[str, List[ChatMessage]] = {}

    async def get_history(self, conversation_id: str, limit: int = 12) -> List[ChatMessage]:
        history = self._history.get(conversation_id, [])
        return history[-limit:]

    async def add_message(self, conversation_id: str, role: str, content: str):
        if conversation_id not in self._history:
            self._history[conversation_id] = []
        msg = ChatMessage(role=role, content=content)
        self._history[conversation_id].append(msg)

        # Also index assistant answers for semantic search
        if role == "assistant" and len(content) > 40:
            try:
                doc_id = f"{conversation_id}_{uuid.uuid4().hex[:8]}"
                self.store.add(
                    ids=[doc_id],
                    documents=[content[:4000]],
                    metadatas=[{
                        "conversation_id": conversation_id,
                        "role": role,
                        "timestamp": datetime.utcnow().isoformat(),
                    }],
                )
            except Exception as e:
                logger.warning(f"Failed to index memory: {e}")

    async def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.store.query(query, n_results=top_k)
