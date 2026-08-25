#!/usr/bin/env python3
"""
RAG Evaluation: Vector-only RAG vs GraphRAG vs Hybrid Graph+Vector RAG.

This script runs a small, hand-labeled evaluation set (single-hop and
multi-hop disaster-response questions with known-relevant document
sections) against three retrieval configurations and reports standard
IR/RAG metrics. Results are computed directly from this project's own
demo data and code — nothing here is fabricated or hardcoded as a result;
re-running this script will always recompute fresh numbers.

Usage:
    cd backend
    python ../scripts/evaluate.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.documents.indexer import build_vector_index
from app.graph.graph_builder import rebuild_full_graph
from app.rag.graphrag_engine import answer_query
from app.rag.query_understanding import understand_query
from app.retrieval.hybrid_retriever import hybrid_retriever
from app.retrieval.vector_store import vector_store

# --- Hand-labeled evaluation set -------------------------------------------------
# `relevant` = set of (document_name, section_label_prefix) pairs considered
# ground-truth relevant for that question, based on manual inspection of the
# demo document set. `hop_type` marks whether answering requires combining
# facts across more than one relationship hop in the knowledge graph.
EVAL_SET = [
    {
        "query": "Which shelters can accommodate flood victims from Area A?",
        "hop_type": "multi-hop",
        "relevant_documents": {"flood_response_guidelines.pdf", "emergency_shelter_guidelines.txt"},
        "expected_entities": {"Shelter A - Government High School", "Shelter D - Town Community Center"},
    },
    {
        "query": "Which resources are currently insufficient?",
        "hop_type": "single-hop",
        "relevant_documents": {"resource_coordination_guidelines.txt"},
        "expected_entities": {"Drinking Water", "Food Packets", "Medical Kits", "Rescue Boats"},
    },
    {
        "query": "Which hospitals have emergency capacity for patients from Area B?",
        "hop_type": "multi-hop",
        "relevant_documents": {"hospital_emergency_guidelines.txt"},
        "expected_entities": {"Community Health Center B (Demo)"},
    },
    {
        "query": "Which agencies are responsible for flood evacuation?",
        "hop_type": "single-hop",
        "relevant_documents": {"disaster_agency_roles.docx", "flood_response_guidelines.pdf"},
        "expected_entities": {"District Disaster Management Authority", "Fire and Rescue Department", "Police Department"},
    },
    {
        "query": "Which shelter can accommodate flood victims from Area A and has drinking water and medical support?",
        "hop_type": "multi-hop",
        "relevant_documents": {"emergency_shelter_guidelines.txt", "flood_response_guidelines.pdf"},
        "expected_entities": {"Shelter B - Community Hall"},
    },
]

TOP_K = 5


def _vector_only_documents(query: str) -> set[str]:
    results = vector_store.search(query, top_k=TOP_K)
    return {chunk.document_name for chunk, _ in results}


def _hybrid_documents(query: str) -> set[str]:
    results = hybrid_retriever.retrieve(query, top_k=TOP_K)
    return {item.chunk.document_name for item in results}


def _precision_recall_hit(retrieved_docs: set[str], relevant_docs: set[str]) -> dict:
    if not retrieved_docs:
        precision = 0.0
    else:
        precision = len(retrieved_docs & relevant_docs) / len(retrieved_docs)
    recall = len(retrieved_docs & relevant_docs) / len(relevant_docs) if relevant_docs else 0.0
    hit = 1.0 if (retrieved_docs & relevant_docs) else 0.0
    return {"precision_at_k": round(precision, 3), "recall_at_k": round(recall, 3), "hit_rate": hit}


def evaluate_vector_only() -> list[dict]:
    rows = []
    for item in EVAL_SET:
        start = time.time()
        retrieved = _vector_only_documents(item["query"])
        elapsed = time.time() - start
        metrics = _precision_recall_hit(retrieved, item["relevant_documents"])
        rows.append({"query": item["query"], "hop_type": item["hop_type"], **metrics, "response_time_sec": round(elapsed, 4)})
    return rows


def evaluate_graphrag() -> list[dict]:
    """GraphRAG-only: relies purely on the graph_facts entity coverage
    (multi-hop accuracy), since GraphRAG's primary contribution is
    structured entity/relationship grounding rather than document
    retrieval."""
    rows = []
    for item in EVAL_SET:
        start = time.time()
        resp = answer_query(item["query"], top_k=TOP_K)
        elapsed = time.time() - start
        found_entities = set(resp.related_entities)
        expected = item["expected_entities"]
        multi_hop_accuracy = len(found_entities & expected) / len(expected) if expected else 0.0
        rows.append({
            "query": item["query"],
            "hop_type": item["hop_type"],
            "multi_hop_accuracy": round(multi_hop_accuracy, 3),
            "graph_facts_returned": len(resp.graph_facts),
            "response_time_sec": round(elapsed, 4),
        })
    return rows


def evaluate_hybrid() -> list[dict]:
    rows = []
    for item in EVAL_SET:
        start = time.time()
        retrieved = _hybrid_documents(item["query"])
        resp = answer_query(item["query"], top_k=TOP_K)
        elapsed = time.time() - start
        metrics = _precision_recall_hit(retrieved, item["relevant_documents"])
        found_entities = set(resp.related_entities)
        expected = item["expected_entities"]
        multi_hop_accuracy = len(found_entities & expected) / len(expected) if expected else 0.0
        rows.append({
            "query": item["query"],
            "hop_type": item["hop_type"],
            **metrics,
            "multi_hop_accuracy": round(multi_hop_accuracy, 3),
            "faithfulness_proxy": 1.0 if resp.graph_facts or resp.sources else 0.0,
            "context_relevance_proxy": round(len(resp.sources) / TOP_K, 3),
            "response_time_sec": round(elapsed, 4),
        })
    return rows


def _average(rows: list[dict], key: str) -> float:
    vals = [r[key] for r in rows if key in r]
    return round(sum(vals) / len(vals), 3) if vals else 0.0


def main():
    print("Rebuilding graph and vector index for a clean evaluation run...\n")
    rebuild_full_graph()
    build_vector_index()

    print("=" * 70)
    print("1) VECTOR-ONLY RAG")
    print("=" * 70)
    vector_rows = evaluate_vector_only()
    for r in vector_rows:
        print(json.dumps(r))
    print(f"\nAverages -> Precision@{TOP_K}: {_average(vector_rows, 'precision_at_k')}, "
          f"Recall@{TOP_K}: {_average(vector_rows, 'recall_at_k')}, "
          f"Hit Rate: {_average(vector_rows, 'hit_rate')}, "
          f"Avg time: {_average(vector_rows, 'response_time_sec')}s")

    print("\n" + "=" * 70)
    print("2) GRAPHRAG (graph-only, multi-hop entity grounding)")
    print("=" * 70)
    graph_rows = evaluate_graphrag()
    for r in graph_rows:
        print(json.dumps(r))
    print(f"\nAverage multi-hop accuracy: {_average(graph_rows, 'multi_hop_accuracy')}, "
          f"Avg time: {_average(graph_rows, 'response_time_sec')}s")

    print("\n" + "=" * 70)
    print("3) HYBRID GRAPH + VECTOR RAG (this project's default pipeline)")
    print("=" * 70)
    hybrid_rows = evaluate_hybrid()
    for r in hybrid_rows:
        print(json.dumps(r))
    print(f"\nAverages -> Precision@{TOP_K}: {_average(hybrid_rows, 'precision_at_k')}, "
          f"Recall@{TOP_K}: {_average(hybrid_rows, 'recall_at_k')}, "
          f"Hit Rate: {_average(hybrid_rows, 'hit_rate')}, "
          f"Multi-hop accuracy: {_average(hybrid_rows, 'multi_hop_accuracy')}, "
          f"Faithfulness (proxy): {_average(hybrid_rows, 'faithfulness_proxy')}, "
          f"Avg time: {_average(hybrid_rows, 'response_time_sec')}s")

    print("\n" + "=" * 70)
    print("SUMMARY (fill into docs/results_template.md for your report)")
    print("=" * 70)
    print(json.dumps({
        "vector_only": {
            "precision_at_k": _average(vector_rows, "precision_at_k"),
            "recall_at_k": _average(vector_rows, "recall_at_k"),
            "hit_rate": _average(vector_rows, "hit_rate"),
        },
        "graphrag_only": {
            "multi_hop_accuracy": _average(graph_rows, "multi_hop_accuracy"),
        },
        "hybrid": {
            "precision_at_k": _average(hybrid_rows, "precision_at_k"),
            "recall_at_k": _average(hybrid_rows, "recall_at_k"),
            "hit_rate": _average(hybrid_rows, "hit_rate"),
            "multi_hop_accuracy": _average(hybrid_rows, "multi_hop_accuracy"),
        },
        "note": "Computed live from this project's demo dataset and code — not fabricated. "
                "Small sample size (5 questions); intended to demonstrate the evaluation "
                "methodology for a final-year project, not to be a statistically powerful study.",
    }, indent=2))


if __name__ == "__main__":
    main()
