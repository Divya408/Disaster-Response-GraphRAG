from __future__ import annotations

from app.retrieval.hybrid_retriever import hybrid_retriever
from app.retrieval.reranker import rerank


def test_hybrid_retriever_returns_results():
    results = hybrid_retriever.retrieve("Which shelter has drinking water in Area A?", top_k=5)
    assert len(results) > 0


def test_bm25_finds_keyword_matches():
    results = hybrid_retriever.bm25.search("rescue boats shortage", top_k=5)
    assert len(results) > 0
    assert any("boat" in r[0].text.lower() or "rescue" in r[0].text.lower() for r in results)


def test_reranker_preserves_all_items():
    results = hybrid_retriever.retrieve("hospital emergency beds", top_k=5)
    reranked = rerank("hospital emergency beds", results, graph_entities=["Salem General Hospital (Demo)"])
    assert len(reranked) == len(results)
