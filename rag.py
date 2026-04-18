from pathlib import Path

from langchain_core.documents import Document

from config import settings

try:
    from langchain_chroma import Chroma
    from langchain_ollama import OllamaEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:  # pragma: no cover
    Chroma = None
    OllamaEmbeddings = None
    RecursiveCharacterTextSplitter = None


class KnowledgeBaseRetriever:
    def __init__(self) -> None:
        self.kb_dir = Path(settings.knowledge_base_dir)
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        self.vectorstore = None
        self._enabled = bool(Chroma and OllamaEmbeddings and RecursiveCharacterTextSplitter)

        if self._enabled:
            try:
                embeddings = OllamaEmbeddings(
                    model=settings.ollama_model,
                )
                self.vectorstore = Chroma(
                    collection_name="support_kb",
                    embedding_function=embeddings,
                    persist_directory=settings.chroma_persist_dir,
                )
                self._ensure_indexed()
            except Exception:
                self.vectorstore = None
                self._enabled = False

    def _load_source_docs(self) -> list[Document]:
        docs: list[Document] = []
        for file_path in sorted(self.kb_dir.glob("**/*")):
            if not file_path.is_file() or file_path.suffix.lower() not in {".md", ".txt"}:
                continue
            content = file_path.read_text(encoding="utf-8")
            docs.append(Document(page_content=content, metadata={"source": str(file_path)}))
        return docs

    def _ensure_indexed(self) -> None:
        if not self.vectorstore:
            return
        try:
            count = self.vectorstore._collection.count()  # pylint: disable=protected-access
            if count > 0:
                return

            source_docs = self._load_source_docs()
            if not source_docs:
                return

            splitter = RecursiveCharacterTextSplitter(chunk_size=650, chunk_overlap=100)
            chunks = splitter.split_documents(source_docs)
            ids = [f"kb-{idx}" for idx in range(len(chunks))]
            self.vectorstore.add_documents(chunks, ids=ids)
        except Exception:
            self.vectorstore = None
            self._enabled = False

    def search(self, query: str, k: int = 4) -> list[str]:
        if self.vectorstore:
            docs = self.vectorstore.similarity_search(query, k=k)
            return [d.page_content.strip()[:700] for d in docs]
        return self._naive_search(query, k)

    def _naive_search(self, query: str, k: int = 4) -> list[str]:
        terms = {w.lower() for w in query.split() if len(w) > 2}
        candidates: list[tuple[int, str]] = []
        for doc in self._load_source_docs():
            text = doc.page_content
            score = sum(text.lower().count(t) for t in terms)
            if score > 0:
                candidates.append((score, text.strip()[:700]))
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in candidates[:k]]
