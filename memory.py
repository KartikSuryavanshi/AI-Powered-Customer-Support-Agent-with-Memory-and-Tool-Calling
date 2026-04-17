from datetime import UTC, datetime

from langchain_core.documents import Document

from config import settings

try:
    from langchain_chroma import Chroma
    from langchain_ollama import OllamaEmbeddings
except Exception:  # pragma: no cover
    Chroma = None
    OllamaEmbeddings = None


class CustomerMemoryStore:
    def __init__(self) -> None:
        self.vectorstore = None
        self._enabled = bool(Chroma and OllamaEmbeddings)

        if self._enabled:
            embeddings = OllamaEmbeddings(
                model=settings.ollama_model,
            )
            self.vectorstore = Chroma(
                collection_name="customer_memory",
                embedding_function=embeddings,
                persist_directory=settings.chroma_persist_dir,
            )

    def add_memory(self, customer_id: str, memory_text: str) -> None:
        if self.vectorstore:
            doc_id = f"{customer_id}-{datetime.now(UTC).timestamp()}"
            doc = Document(page_content=memory_text, metadata={"customer_id": customer_id})
            self.vectorstore.add_documents([doc], ids=[doc_id])

    def get_relevant_memories(self, customer_id: str, query: str, k: int = 3) -> list[str]:
        if not self.vectorstore:
            return []
        docs = self.vectorstore.similarity_search(
            query,
            k=k,
            filter={"customer_id": customer_id},
        )
        return [d.page_content for d in docs]
