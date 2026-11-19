from pathlib import Path
import hashlib
import re
from pypdf import PdfReader
from app.core.config import settings

class _LocalFallbackCollection:
    """Small keyword fallback for environments where optional vector packages are not installed."""
    def __init__(self): self.rows = {}
    def count(self): return len(self.rows)
    def upsert(self, ids, documents, metadatas):
        for key, doc, meta in zip(ids, documents, metadatas): self.rows[key] = (doc, meta)
    def query(self, query_texts, n_results):
        terms = set(re.findall(r"[a-z0-9]+", query_texts[0].lower()))
        ranked = []
        for doc, meta in self.rows.values():
            words = set(re.findall(r"[a-z0-9]+", doc.lower()))
            overlap = len(terms & words) / max(1, len(terms))
            ranked.append((overlap, doc, meta))
        ranked.sort(key=lambda item: item[0], reverse=True)
        chosen = ranked[:n_results]
        return {"documents": [[x[1] for x in chosen]], "metadatas": [[x[2] for x in chosen]], "distances": [[1-x[0] for x in chosen]]}

class KnowledgeRetriever:
    def __init__(self):
        Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
        self.client = None
        try:
            import chromadb
            from chromadb.utils import embedding_functions
            self.client = chromadb.PersistentClient(path=settings.chroma_path)
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=settings.embedding_model)
            self.collection = self.client.get_or_create_collection(
                name="role_knowledge", embedding_function=ef, metadata={"hnsw:space": "cosine"}
            )
        except ImportError:
            self.collection = _LocalFallbackCollection()

    def _read_file(self, path: Path) -> str:
        if path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        return path.read_text(encoding="utf-8", errors="ignore")

    def ingest_directory(self, directory: str | None = None) -> int:
        root = Path(directory or settings.knowledge_base_path)
        root.mkdir(parents=True, exist_ok=True)
        docs, ids, metas = [], [], []
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".pdf", ".txt", ".md"}:
                text = self._read_file(path)
                chunks = self._chunk(text)
                for index, chunk in enumerate(chunks):
                    key = hashlib.sha1(f"{path}:{index}:{chunk}".encode()).hexdigest()
                    ids.append(key); docs.append(chunk)
                    metas.append({"source": path.name, "chunk": index, "role": self._role_for(path)})
        if docs:
            # Upsert makes ingestion safe to repeat.
            self.collection.upsert(ids=ids, documents=docs, metadatas=metas)
        return len(docs)

    @staticmethod
    def _role_for(path: Path) -> str:
        name = path.name.lower()
        if "backend" in name: return "Backend Engineer"
        if "ai" in name or "ml" in name or "machine" in name: return "AI/ML Engineer"
        return "General"

    @staticmethod
    def _chunk(text: str, size: int = 850, overlap: int = 120) -> list[str]:
        clean = re.sub(r"\s+", " ", text).strip()
        if not clean: return []
        chunks, start = [], 0
        while start < len(clean):
            end = min(start + size, len(clean))
            if end < len(clean):
                boundary = clean.rfind(". ", start + size // 2, end)
                if boundary > start: end = boundary + 1
            part = clean[start:end].strip()
            if len(part) > 80: chunks.append(part)
            if end >= len(clean): break
            start = max(end - overlap, start + 1)
        return chunks

    def retrieve(self, query: str, role: str, k: int = 4) -> list[dict]:
        if self.collection.count() == 0:
            return []
        result = self.collection.query(query_texts=[query], n_results=min(max(k * 3, k), self.collection.count()))
        ranked = []
        for doc, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
            ranked.append({"text": doc, "source": meta.get("source", "Knowledge base"),
                           "relevance": round(1 - distance, 3), "role": meta.get("role", "General")})
        matched = [item for item in ranked if item["role"] in ("General", role)]
        # Keep the experience useful for adjacent roles when the corpus has no exact role label.
        selected = matched if matched else ranked
        return [{key: value for key, value in item.items() if key != "role"} for item in selected[:k]]

rag = KnowledgeRetriever()
