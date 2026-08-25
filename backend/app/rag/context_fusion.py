"""Fuses graph retrieval results and text retrieval results into the two
context blocks (graph_context, text_context) consumed by the LLM prompt."""
from __future__ import annotations

from app.retrieval.hybrid_retriever import RetrievedItem


def format_graph_context(graph_facts: list[dict]) -> str:
    lines = []
    for fact in graph_facts:
        lines.append(f"- {fact['statement']}")
    return "\n".join(lines)


def format_text_context(items: list[RetrievedItem]) -> str:
    lines = []
    for item in items:
        source = f"{item.chunk.document_name} — {item.chunk.section_label}"
        lines.append(f"[Source: {source}]\n{item.chunk.text}\n")
    return "\n".join(lines)


def build_sources(items: list[RetrievedItem]) -> list[dict]:
    return [
        {
            "document": item.chunk.document_name,
            "section": item.chunk.section_label,
            "relevance_score": round(item.fused_score, 4),
        }
        for item in items
    ]
