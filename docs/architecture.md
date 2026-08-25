# System Architecture

## 1. Overview

DisasterGraph AI is a **GraphRAG-based disaster response intelligence and
resource coordination system**. It combines a knowledge graph, a hybrid
(vector + keyword) document retrieval index, and an LLM (or a deterministic
Demo Mode) to answer multi-hop questions about shelters, resources,
hospitals, and agencies during a disaster response.

## 2. High-Level Pipeline

```text
                 DISASTER DOCUMENTS (PDF / DOCX / TXT / MD / CSV)
                        |
                 Document Parser (app/documents/parser.py)
                        |
                    Chunking (app/documents/chunker.py)
                        |
        +---------------+---------------------+
        |                                     |
Entity/Relation Extraction              Hybrid Indexing
(app/graph/entity_extractor.py,         (app/retrieval/hybrid_retriever.py)
 app/graph/relation_extractor.py)         - BM25 (custom numpy implementation)
        |                                  - Vector (ChromaDB+embeddings, or
Knowledge Graph                             TF-IDF fallback)
(app/graph/graph_store.py:
 Neo4j or in-memory networkx fallback)
        |
        +-----------------+-------------------+
                          |
                   GraphRAG Engine (app/rag/graphrag_engine.py)
                          |
        Query Understanding -> Multi-hop Graph Retrieval
        -> Hybrid Text Retrieval -> Reranking -> Context Fusion
                          |
                LLM (OpenAI-compatible) or Demo Mode
                          |
        Grounded Answer + Sources + Reasoning Path + Confidence
                          |
        +-----------------+-------------------+
        |                 |                   |
  Disaster Domain    FastAPI REST API    PDF Report Generator
  Logic (shelter/          |             (app/reports/report_generator.py)
  resource/hospital   React Frontend
  matching, priority   (frontend/)
  scoring)
```

## 3. Backend Modules

| Module | Responsibility |
|---|---|
| `app/config.py` | Environment-driven settings (no hardcoded secrets) |
| `app/documents/` | Parsing (PDF/DOCX/TXT/MD/CSV), chunking, indexing orchestration |
| `app/graph/` | Entity extraction, relation extraction, normalization, graph storage (Neo4j/in-memory), graph queries, graph construction |
| `app/retrieval/` | BM25 keyword retrieval, vector retrieval (Chroma or TF-IDF), hybrid fusion, reranking |
| `app/llm/` | OpenAI-compatible LLM client with Demo Mode fallback, prompt templates |
| `app/rag/` | Query understanding, context fusion, the core GraphRAG orchestration engine |
| `app/disaster/` | Shelter matching, resource shortage detection, hospital matching, priority scoring, recommendation generation, offline sync |
| `app/database/` | SQLite persistence for operational records (documents, query logs, reports, offline records) |
| `app/reports/` | PDF report generation (ReportLab) |
| `app/api/` | FastAPI routers exposing all of the above over HTTP |

## 4. Frontend

React (Vite) + Tailwind CSS single-page app with a persistent sidebar and
11 pages (Dashboard, Disaster Events, Graph Explorer, GraphRAG Assistant,
Shelters, Resources, Hospitals, Agencies, Documents, Offline Mode, Reports).
The Graph Explorer uses a dependency-free custom SVG force-directed graph
visualization component (`src/components/GraphCanvas.jsx`) supporting pan,
zoom, drag, and node-click inspection — no external graph-visualization
library is required.

## 5. Fallback / Resilience Design

The project is designed to remain fully demonstrable even when optional
infrastructure (Neo4j, ChromaDB, a real LLM API key) is unavailable:

- **Graph backend**: Neo4j if `NEO4J_URI`/`NEO4J_USERNAME`/`NEO4J_PASSWORD`
  are set and reachable; otherwise an in-memory `networkx` graph with an
  identical query interface.
- **Vector backend**: ChromaDB + sentence-transformers if installed;
  otherwise a scikit-learn TF-IDF cosine-similarity index (no downloads
  required).
- **LLM**: a configured OpenAI-compatible endpoint if `LLM_API_KEY` is set
  and `DEMO_MODE=false`; otherwise a deterministic, clearly-labeled
  "[DEMO MODE]" answer built directly from retrieved graph facts and
  document evidence.

## 6. Data Stores

| Store | Purpose |
|---|---|
| Neo4j / in-memory graph | Entities and relationships |
| ChromaDB / TF-IDF index | Document chunk embeddings for semantic search |
| SQLite | Operational records: documents, query logs, reports, offline sync records |
