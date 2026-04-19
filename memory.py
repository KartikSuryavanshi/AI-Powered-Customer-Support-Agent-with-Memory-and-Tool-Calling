from datetime import UTC, datetime
from typing import Any

from langchain_core.documents import Document

from config import settings
from embeddings import SentenceTransformerEmbeddings

try:
    from langchain_chroma import Chroma
except Exception:  # pragma: no cover
    Chroma = None

try:
    from mem0 import MemoryClient
except Exception:  # pragma: no cover
    MemoryClient = None


class CustomerMemoryStore:
    def __init__(self) -> None:
        self.mem0_client = None
        self.vectorstore = None
        self._enabled = False

        if settings.mem0_api_key and MemoryClient:
            try:
                self.mem0_client = MemoryClient(api_key=settings.mem0_api_key)
                self._enabled = True
            except Exception:
                self.mem0_client = None

        local_enabled = bool(Chroma and SentenceTransformerEmbeddings)

        if local_enabled:
            try:
                embeddings = SentenceTransformerEmbeddings(settings.embedding_model)
                self.vectorstore = Chroma(
                    collection_name="customer_memory_minilm",
                    embedding_function=embeddings,
                    persist_directory=settings.chroma_persist_dir,
                )
                self._enabled = True
            except Exception:
                self.vectorstore = None

    def add_memory(self, customer_id: str, memory_text: str) -> None:
        if self.mem0_client:
            try:
                messages: list[dict[str, str]] = [{"role": "user", "content": memory_text}]
                self.mem0_client.add(messages, user_id=customer_id)
                return
            except Exception:
                pass

        if self.vectorstore:
            doc_id = f"{customer_id}-{datetime.now(UTC).timestamp()}"
            doc = Document(page_content=memory_text, metadata={"customer_id": customer_id})
            self.vectorstore.add_documents([doc], ids=[doc_id])

    def get_relevant_memories(self, customer_id: str, query: str, k: int = 3) -> list[str]:
        if self.mem0_client:
            try:
                response: dict[str, Any] = self.mem0_client.search(query, filters={"user_id": customer_id})
                results = response.get("results", []) if isinstance(response, dict) else []
                memories: list[str] = []
                for item in results[:k]:
                    if not isinstance(item, dict):
                        continue
                    value = item.get("memory") or item.get("text") or item.get("content")
                    if value:
                        memories.append(str(value))
                if memories:
                    return memories
            except Exception:
                pass

        if not self.vectorstore:
            return []
        docs = self.vectorstore.similarity_search(
            query,
            k=k,
            filter={"customer_id": customer_id},
        )
        return [d.page_content for d in docs]
