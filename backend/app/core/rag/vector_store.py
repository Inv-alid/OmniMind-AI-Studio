from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from loguru import logger
from app.core.config import get_settings


class VectorStore:
    def __init__(self):
        settings = get_settings()
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="omnimind_memory",
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, ids: List[str], documents: List[str], metadatas: Optional[List[dict]] = None):
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas or [{} for _ in ids],
        )

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
            )
            docs = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    docs.append({
                        "text": doc,
                        "id": results["ids"][0][i] if results["ids"] else None,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results.get("distances") else None,
                    })
            return docs
        except Exception as e:
            logger.warning(f"Vector query failed: {e}")
            return []
