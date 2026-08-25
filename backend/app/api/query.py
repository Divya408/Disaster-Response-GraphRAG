from __future__ import annotations

from fastapi import APIRouter
from dataclasses import asdict

from app.api.schemas import QueryRequest
from app.database import db
from app.rag.graphrag_engine import answer_query

router = APIRouter(prefix="/api", tags=["graphrag"])


@router.post("/query")
def query(req: QueryRequest):
    result = answer_query(req.query, top_k=req.top_k)
    db.log_query(req.query, result.intent, result.is_demo_mode, result.confidence)
    return asdict(result)
