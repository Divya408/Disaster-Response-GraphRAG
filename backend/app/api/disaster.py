from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.schemas import DisasterAnalyzeRequest
from app.disaster.recommendation_engine import generate_recommendation
from app.graph.graph_store import graph_store

router = APIRouter(prefix="/api/disaster", tags=["disaster"])


@router.post("/analyze")
def analyze(req: DisasterAnalyzeRequest):
    node = graph_store.get_node(req.area)
    if not node:
        raise HTTPException(status_code=404, detail=f"Unknown area: {req.area}")
    return generate_recommendation(req.area)
