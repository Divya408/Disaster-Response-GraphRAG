# Final-Year Project Documentation

**Title:** GraphRAG-Based Disaster Response Intelligence and Resource
Coordination System
**Short Name:** DisasterGraph AI

---

## Abstract

During natural disasters, critical information about affected locations,
shelters, resources, hospitals, and response agencies is scattered across
many documents and data sources, making it hard for coordinators to answer
multi-part questions quickly. This project implements **DisasterGraph AI**,
a decision-support system that builds a knowledge graph from disaster
documents and structured operational data, combines it with hybrid
(vector + keyword) document retrieval, and uses a GraphRAG pipeline to
answer natural-language questions with grounded, cited, multi-hop-aware
answers. The system also provides shelter-matching, resource-shortage
detection, hospital-referral suggestions, a transparent priority-scoring
heuristic, offline data entry for low-connectivity responders, and
downloadable PDF situation reports — all built and demonstrated on a
clearly labeled synthetic demo scenario (a flood in "Salem District").

## Problem Statement

See `docs/research_problem.md` for the full problem statement and research
questions.

## Existing System

Most existing disaster-information tools fall into two categories:
(1) **static dashboards** that display shelter/resource data without any
natural-language query capability, and (2) **plain RAG chatbots** that
retrieve semantically similar text passages but cannot reliably answer
questions requiring relationship reasoning across multiple documents (e.g.
"which shelter has both capacity and medical support near this area").
Neither approach models the explicit entity relationships that connect
disasters, locations, shelters, resources, agencies, and hospitals.

## Proposed System

DisasterGraph AI adds a knowledge-graph layer between the raw documents and
the language model. Structured demo data (shelters, resources, hospitals,
agencies) is loaded directly as ground-truth graph nodes/edges; unstructured
documents are parsed, chunked, and mined for additional entities and
relationships using gazetteer + regex extraction, and merged into the same
graph via entity normalization. A GraphRAG engine then combines graph
traversal with hybrid text retrieval to answer questions, always returning
sources and a reasoning path alongside the answer.

## Objectives

See `README.md` → "Main Objective" and item 4 of the original project
brief; summarized: ingest documents, extract entities/relationships, build
and query a knowledge graph, perform hybrid + multi-hop retrieval, generate
grounded answers with sources and reasoning paths, and produce shelter /
resource / hospital recommendations and downloadable reports.

## Methodology

1. **Data preparation**: synthetic demo scenario (`backend/data/demo/demo_scenario.json`)
   + demo documents (`backend/data/documents/`).
2. **Graph construction**: `app/graph/graph_builder.py` seeds structured
   data, then ingests every document, extracting entities/relations and
   merging them via normalization.
3. **Hybrid indexing**: `app/documents/indexer.py` chunks every document and
   builds a BM25 + vector index.
4. **GraphRAG querying**: `app/rag/graphrag_engine.py` — see
   `docs/graphrag_pipeline.md` for the full stage-by-stage breakdown.
5. **Domain logic**: shelter/resource/hospital matching and priority scoring
   in `app/disaster/`.
6. **Evaluation**: `scripts/evaluate.py` compares vector-only, GraphRAG-only,
   and hybrid retrieval.

## System Architecture

See `docs/architecture.md`.

## Knowledge Graph Design

See `docs/graph_schema.md`.

## GraphRAG Methodology

See `docs/graphrag_pipeline.md`.

## Algorithms

- **BM25** (custom numpy implementation) for keyword retrieval.
- **TF-IDF cosine similarity** (scikit-learn) as the default vector-retrieval
  fallback, or embeddings + ChromaDB when available.
- **Reciprocal Rank Fusion** to merge vector and BM25 rankings.
- **Rule-based reranking** using entity-overlap signals (optional
  cross-encoder reranking when `sentence-transformers` is installed).
- **Breadth-first multi-hop graph traversal** for subgraph expansion
  (`find_connected_entities`) and shelter/hospital/resource reasoning.
- **Transparent weighted-sum scoring** for shelter suitability and disaster
  priority (explicitly documented as a demo heuristic, not a validated
  formula).

## Database Design

- **Neo4j / in-memory graph**: entities + relationships (see
  `docs/graph_schema.md`).
- **ChromaDB / TF-IDF**: document chunk embeddings + metadata
  (document_id, section, file_type).
- **SQLite** (`app/database/db.py`): `query_log`, `documents`, `reports`,
  `offline_records` tables for operational bookkeeping.

## Implementation

Backend: Python 3.11+, FastAPI, networkx, scikit-learn, ReportLab, pypdf,
python-docx. Frontend: React 18 + Vite + Tailwind CSS, with a
dependency-free custom SVG graph-visualization component. See
`README.md` for the full technology stack and setup instructions.

## Testing

`backend/tests/` contains pytest test modules covering document parsing,
entity/relation extraction, graph construction and querying, hybrid
retrieval, the GraphRAG engine, disaster domain logic, and the FastAPI
endpoints. See `docs/setup.md` → "Running Tests".

## Evaluation

`scripts/evaluate.py` computes Precision@K, Recall@K, Hit Rate, and a
multi-hop accuracy proxy for Vector-only RAG, GraphRAG-only, and Hybrid
Graph+Vector RAG against a small hand-labeled question set drawn from the
demo scenario. Results are always computed live from the current codebase
and demo data — see `docs/results_template.md` for how to record and report
your own run's numbers (do not present the example numbers in this
documentation as final research results without re-running the script
yourself).

## Limitations and Future Scope

See `docs/limitations_and_future_scope.md`.

## Conclusion

DisasterGraph AI demonstrates that combining a knowledge graph with hybrid
document retrieval — a GraphRAG architecture — enables more reliable
multi-hop question answering for disaster-response coordination than plain
vector RAG alone, while remaining fully demonstrable without requiring paid
LLM access, a running Neo4j instance, or GPU-based embedding models, through
carefully designed fallbacks at every layer.
