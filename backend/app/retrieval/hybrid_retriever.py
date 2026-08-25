"""
Hybrid retrieval: combines vector (semantic) retrieval, BM25 (keyword)
retrieval, and graph-derived facts using Reciprocal Rank Fusion (RRF), which
is a simple, well-known, parameter-light way to merge ranked lists from
heterogeneous retrievers without needing to calibrate raw score scales.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.documents.chunker import Chunk
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.vector_store import vector_store


@dataclass
class RetrievedItem:
    chunk: Chunk
    vector_score: float = 0.0
    bm25_score: float = 0.0
    fused_score: float = 0.0
    sources: list[str] = field(default_factory=list)


class HybridRetriever:
    def __init__(self):
        self.bm25 = BM25Retriever()
        self._indexed_chunks: list[Chunk] = []

    def index(self, chunks: list[Chunk]):
        self._indexed_chunks = chunks
        self.bm25.index(chunks)
        vector_store.index(chunks)

    def retrieve(self, query: str, top_k: int = 5, rrf_k: int = 60) -> list[RetrievedItem]:
        if not self._indexed_chunks:
            return []

        vector_results = vector_store.search(query, top_k=top_k * 2)
        bm25_results = self.bm25.search(query, top_k=top_k * 2)

        merged: dict[str, RetrievedItem] = {}

        for rank, (chunk, score) in enumerate(vector_results, start=1):
            item = merged.setdefault(chunk.chunk_id, RetrievedItem(chunk=chunk))
            item.vector_score = score
            item.fused_score += 1.0 / (rrf_k + rank)
            item.sources.append("vector")

        for rank, (chunk, score) in enumerate(bm25_results, start=1):
            item = merged.setdefault(chunk.chunk_id, RetrievedItem(chunk=chunk))
            item.bm25_score = score
            item.fused_score += 1.0 / (rrf_k + rank)
            item.sources.append("bm25")

        ranked = sorted(merged.values(), key=lambda x: x.fused_score, reverse=True)
        return ranked[:top_k]


hybrid_retriever = HybridRetriever()
