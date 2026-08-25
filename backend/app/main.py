"""
DisasterGraph AI — FastAPI application entrypoint.

On startup (Demo Mode): seeds the SQLite DB, builds the knowledge graph from
structured demo data + demo documents, and builds the hybrid vector/BM25
index — so the app is immediately queryable after `uvicorn app.main:app`.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agencies, disaster, documents, graph, health, hospitals, offline, query, report, resources, shelters
from app.config import settings
from app.database.db import init_db
from app.documents.indexer import build_vector_index
from app.graph.graph_builder import rebuild_full_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("disastergraph")

app = FastAPI(
    title=settings.APP_NAME,
    description="GraphRAG-Based Disaster Response Intelligence and Resource Coordination System",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(graph.router)
app.include_router(query.router)
app.include_router(disaster.router)
app.include_router(shelters.router)
app.include_router(resources.router)
app.include_router(hospitals.router)
app.include_router(agencies.router)
app.include_router(offline.router)
app.include_router(report.router)


@app.on_event("startup")
def startup_event():
    init_db()
    if settings.DEMO_MODE:
        logger.info("DEMO_MODE=true — seeding knowledge graph and vector index from demo data...")
        graph_summary = rebuild_full_graph()
        index_summary = build_vector_index()
        logger.info(
            "Graph ready: backend=%s nodes=%s edges=%s | Index ready: chunks=%s",
            graph_summary["backend"], graph_summary["node_count"], graph_summary["edge_count"],
            index_summary["total_chunks"],
        )
    else:
        logger.info("DEMO_MODE=false — call POST /api/graph/build and POST /api/documents/index to initialize data.")


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "demo_mode": settings.DEMO_MODE,
        "docs": "/docs",
    }
