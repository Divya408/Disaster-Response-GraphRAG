# DisasterGraph AI

**GraphRAG-Based Disaster Response Intelligence and Resource Coordination System**

> ⚠️ **All disaster, shelter, resource, hospital, and agency data in this
> project is SYNTHETIC DEMO DATA** created for an academic final-year
> project. It does not represent a real disaster event, real government
> data, or real emergency instructions. This system provides **AI-assisted
> decision support** and does not replace official disaster-management
> authorities or emergency command decisions.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Features](#features)
- [Architecture](#architecture)
- [Graph Schema](#graph-schema)
- [GraphRAG Pipeline](#graphrag-pipeline)
- [Technology Stack](#technology-stack)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
  - [Python Setup](#python-setup)
  - [Node Setup](#node-setup)
  - [Neo4j Setup (optional)](#neo4j-setup-optional)
  - [Environment Variables](#environment-variables)
- [Running the Backend](#running-the-backend)
- [Running the Frontend](#running-the-frontend)
- [Demo Mode](#demo-mode)
- [Loading Documents](#loading-documents)
- [Building the Knowledge Graph](#building-the-knowledge-graph)
- [Building the Vector Index](#building-the-vector-index)
- [Using GraphRAG](#using-graphrag)
- [Using Offline Mode](#using-offline-mode)
- [Generating Reports](#generating-reports)
- [Running Tests](#running-tests)
- [Running Evaluation](#running-evaluation)
- [Windows Setup (exact commands)](#windows-setup-exact-commands)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [Future Scope](#future-scope)
- [Viva Questions](#viva-questions)

---

## Project Overview

DisasterGraph AI is a text/data-based **GraphRAG (Graph + Retrieval-Augmented
Generation) system** for disaster-response decision support. It builds a
knowledge graph from disaster documents and structured operational data
(shelters, resources, hospitals, agencies), combines it with hybrid
vector+keyword document retrieval, and answers natural-language questions
with grounded, cited, multi-hop-aware responses — plus shelter/resource/
hospital recommendations, a transparent priority score, offline data entry,
and downloadable PDF reports.

The system does **not** require computer vision, IoT sensors, or mobile GPS.

## Problem Statement

See [`docs/research_problem.md`](docs/research_problem.md).

## Objectives

Ingest disaster documents → extract entities & relationships → build a
knowledge graph → perform hybrid + multi-hop retrieval → generate
source-grounded answers with an explainable reasoning path → provide
shelter/resource/hospital recommendations → generate downloadable reports.

## Features

- **GraphRAG query engine** — multi-hop graph traversal + hybrid (vector +
  BM25) text retrieval + reranking + LLM (or Demo Mode) answer generation
- **Interactive knowledge graph visualization** (Graph Explorer) — pan,
  zoom, drag, click-to-inspect, no external graph-viz library required
- **Shelter matching** with a transparent, documented suitability score
- **Resource shortage detection** and coordination
- **Hospital referral matching**
- **Transparent, documented priority-scoring heuristic** (clearly labeled
  as a demo heuristic, not a validated formula)
- **Document management** — upload/view/delete/index PDF, DOCX, TXT, MD, CSV
- **Offline / low-connectivity data entry** with "Pending Sync" simulation
  for responders (not victims — see [Viva Q20](docs/viva_questions.md))
- **Downloadable PDF situation reports** with sources, reasoning path, and
  the mandatory disclaimer
- **RAG evaluation harness** comparing Vector-only vs GraphRAG vs Hybrid
- **Runs fully in Demo Mode** — no Neo4j, ChromaDB, or LLM API key required

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full pipeline
diagram and module breakdown.

## Graph Schema

See [`docs/graph_schema.md`](docs/graph_schema.md).

## GraphRAG Pipeline

See [`docs/graphrag_pipeline.md`](docs/graphrag_pipeline.md).

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite, Tailwind CSS |
| Backend | Python + FastAPI |
| Graph Database | Neo4j (optional; in-memory `networkx` fallback) |
| Vector Database | ChromaDB (optional; scikit-learn TF-IDF fallback) |
| Relational Database | SQLite |
| NLP / Retrieval | Gazetteer + regex extraction, custom BM25 (numpy), TF-IDF / sentence-transformers |
| LLM | Any OpenAI-compatible API (optional; deterministic Demo Mode fallback) |
| PDF Reports | ReportLab |
| Graph Visualization | Custom dependency-free SVG force-directed component |

## Folder Structure

```text
Disaster-Response-GraphRAG/
├── frontend/                # React + Vite + Tailwind SPA
│   └── src/{components,pages,services}/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entrypoint
│   │   ├── api/              # HTTP routers
│   │   ├── graph/            # extraction, normalization, graph store, queries, builder
│   │   ├── rag/               # query understanding, context fusion, GraphRAG engine
│   │   ├── retrieval/         # BM25, vector store, hybrid retriever, reranker
│   │   ├── llm/                # LLM service + prompts (with Demo Mode)
│   │   ├── documents/          # parsing, chunking, indexing
│   │   ├── disaster/           # shelter/resource/hospital matching, priority, offline sync
│   │   ├── database/            # SQLite layer
│   │   ├── reports/              # PDF report generator
│   │   └── utils/
│   ├── data/{documents,demo,sample_data}/
│   ├── tests/
│   └── requirements.txt
├── docs/                      # architecture, schema, pipeline, setup, research, viva, etc.
├── scripts/                   # seed_demo_data, build_graph, build_vector_index, evaluate
├── .env.example
└── README.md
```

## Installation

### Python Setup

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### Node Setup

```bash
cd frontend
npm install
cp .env.example .env
```

### Neo4j Setup (optional)

The project runs fine without Neo4j — see [`docs/setup.md`](docs/setup.md)
for full Neo4j instructions. In short: set `NEO4J_URI`, `NEO4J_USERNAME`,
`NEO4J_PASSWORD` in `backend/.env`; if unset or unreachable, an in-memory
graph is used automatically.

### Environment Variables

```bash
cp .env.example backend/.env
```

`DEMO_MODE=true` (the default) requires no further configuration.

## Running the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

- App: http://localhost:8000/
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## Running the Frontend

```bash
cd frontend
npm run dev
```

Open http://localhost:5173.

## Demo Mode

With `DEMO_MODE=true` (default), on backend startup the app automatically:
1. Seeds the SQLite database
2. Builds the knowledge graph from `backend/data/demo/` + `backend/data/documents/`
3. Builds the hybrid vector/BM25 index

No manual setup steps are required before you can start asking questions.

## Loading Documents

Use the **Documents** page in the UI, or:

```bash
curl -X POST http://localhost:8000/api/documents/upload -F "file=@mydoc.pdf"
curl -X POST http://localhost:8000/api/documents/index
curl -X POST http://localhost:8000/api/graph/build
```

## Building the Knowledge Graph

```bash
cd backend
python ../scripts/build_graph.py
```

## Building the Vector Index

```bash
cd backend
python ../scripts/build_vector_index.py
```

## Using GraphRAG

Open the **GraphRAG Assistant** page and click one of the example questions,
or type your own, e.g.:

> "Which shelter should receive displaced people from Area A, and which
> agency should coordinate the response?"

The response includes: answer, confidence indicator, reasoning path,
sources, and related entities.

## Using Offline Mode

Open the **Offline Mode** page to simulate a responder submitting a field
assessment without connectivity; records are stored as "Pending Sync" and
can be synchronized with the "Sync Now" button. See
[Viva Q20](docs/viva_questions.md) for why this doesn't depend on the
victim's phone.

## Generating Reports

Open the **Reports** page, pick an affected area, and click "Generate PDF
Report" to download a full situation report.

## Running Tests

```bash
cd backend
pytest -v
```

## Running Evaluation

```bash
cd backend
python ../scripts/evaluate.py
```

## Windows Setup (exact commands)

```powershell
# Backend
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.example .env
uvicorn app.main:app --reload
```

In a second terminal:

```powershell
# Frontend
cd frontend
npm install
copy .env.example .env
npm run dev
```

Then open http://localhost:5173 in your browser.

If Neo4j is not installed, no action is needed — the app automatically uses
its in-memory graph fallback. See [`docs/setup.md`](docs/setup.md) for
optional Neo4j installation instructions on Windows.

## Troubleshooting

See [`docs/setup.md`](docs/setup.md#13-troubleshooting).

## Limitations

See [`docs/limitations_and_future_scope.md`](docs/limitations_and_future_scope.md).

## Future Scope

See [`docs/limitations_and_future_scope.md`](docs/limitations_and_future_scope.md).

## Viva Questions

See [`docs/viva_questions.md`](docs/viva_questions.md) for 30+ questions and
student-friendly answers.

---

## Disclaimer

This system provides AI-assisted decision support and does not replace
official disaster-management authorities or emergency command decisions.
All data shipped with this project is synthetic demo data for academic use.
#   D i s a s t e r - R e s p o n s e - G r a p h R A G  
 