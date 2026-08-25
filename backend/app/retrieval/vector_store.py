"""
Vector (semantic) retrieval.

Preferred stack: ChromaDB + sentence-transformers embeddings, configured via
CHROMA_PATH. Both are optional dependencies; if either is unavailable the
module transparently falls back to a scikit-learn TF-IDF cosine-similarity
index, which requires no downloads and no external services, so the project
is always demonstrable.
"""
from __future__ import annotations

from app.config import settings
from app.documents.chunker import Chunk


class _TfidfVectorStore:
    """Dependency-light fallback: TF-IDF + cosine similarity."""

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = None
        self.chunks: list[Chunk] = []

    def index(self, chunks: list[Chunk]):
        self.chunks = chunks
        texts = [c.text for c in chunks] or [""]
        self._matrix = self._vectorizer.fit_transform(texts)

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        if not self.chunks or self._matrix is None:
            return []
        from sklearn.metrics.pairwise import cosine_similarity

        query_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self._matrix)[0]
        ranked = sims.argsort()[::-1][:top_k]
        return [(self.chunks[i], float(sims[i])) for i in ranked if sims[i] > 0]

    @property
    def backend_name(self) -> str:
        return "TF-IDF (scikit-learn fallback)"


class _ChromaVectorStore:
    """ChromaDB + sentence-transformers backed store."""

    def __init__(self, path: str):
        import chromadb
        from chromadb.utils import embedding_functions

        self._client = chromadb.PersistentClient(path=path)
        self._embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self._collection = self._client.get_or_create_collection(
            name="disaster_documents", embedding_function=self._embed_fn
        )
        self.chunks: dict[str, Chunk] = {}

    def index(self, chunks: list[Chunk]):
        # Reset collection for a clean rebuild.
        try:
            self._client.delete_collection("disaster_documents")
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name="disaster_documents", embedding_function=self._embed_fn
        )
        self.chunks = {c.chunk_id: c for c in chunks}
        if not chunks:
            return
        self._collection.add(
            ids=[c.chunk_id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[c.metadata for c in chunks],
        )

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        if not self.chunks:
            return []
        results = self._collection.query(query_texts=[query], n_results=min(top_k, len(self.chunks)))
        out = []
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        for chunk_id, dist in zip(ids, distances):
            chunk = self.chunks.get(chunk_id)
            if chunk:
                similarity = 1.0 - dist  # cosine distance -> similarity
                out.append((chunk, similarity))
        return out

    @property
    def backend_name(self) -> str:
        return "ChromaDB + sentence-transformers"


def build_vector_store():
    try:
        return _ChromaVectorStore(settings.CHROMA_PATH)
    except Exception:
        return _TfidfVectorStore()


vector_store = build_vector_store()
