"""
Reranking stage.

A lightweight, dependency-free reranker (no cross-encoder download required)
that adjusts the hybrid fused score using:
  - query/chunk entity overlap
  - graph path relevance (does the chunk mention entities that also appear
    in the multi-hop graph reasoning path?)
  - location and disaster-type relevance

This keeps the project runnable without large model downloads while still
implementing a genuine, explainable reranking signal. A cross-encoder
(`sentence-transformers` CrossEncoder) is used instead when available.
"""
from __future__ import annotations

from app.graph.entity_extractor import extract_entities
from app.retrieval.hybrid_retriever import RetrievedItem


def _entity_texts(text: str) -> set[str]:
    return {e.canonical.lower() for e in extract_entities(text)}


def rerank(query: str, items: list[RetrievedItem], graph_entities: list[str] | None = None) -> list[RetrievedItem]:
    if not items:
        return items

    query_entities = _entity_texts(query)
    graph_entities_lower = {e.lower() for e in (graph_entities or [])}

    scored = []
    for item in items:
        chunk_entities = _entity_texts(item.chunk.text)

        entity_overlap = len(query_entities & chunk_entities)
        graph_overlap = len(graph_entities_lower & chunk_entities)

        rerank_score = (
            item.fused_score
            + 0.15 * entity_overlap
            + 0.25 * graph_overlap
        )
        scored.append((rerank_score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    reranked_items = []
    for score, item in scored:
        item.fused_score = score
        reranked_items.append(item)
    return reranked_items


def try_cross_encoder_rerank(query: str, items: list[RetrievedItem]) -> list[RetrievedItem] | None:
    """Optional cross-encoder reranking if sentence-transformers is installed.
    Returns None (caller should fall back to `rerank`) on any failure."""
    try:
        from sentence_transformers import CrossEncoder

        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = [(query, item.chunk.text) for item in items]
        scores = model.predict(pairs)
        for item, score in zip(items, scores):
            item.fused_score = float(score)
        items.sort(key=lambda i: i.fused_score, reverse=True)
        return items
    except Exception:
        return None
