from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import HealthResponse
from app.config import settings
from app.graph.graph_store import graph_store
from app.retrieval.vector_store import vector_store

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        demo_mode=settings.DEMO_MODE,
        graph_backend=graph_store.backend_name,
        vector_backend=vector_store.backend_name if hasattr(vector_store, "backend_name") else "unknown",
        version=settings.APP_VERSION,
    )
