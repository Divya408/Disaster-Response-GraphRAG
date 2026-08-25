from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.api.schemas import ReportRequest
from app.database import db
from app.graph.graph_store import graph_store
from app.reports.report_generator import generate_report

router = APIRouter(prefix="/api/report", tags=["report"])


@router.post("/generate")
def generate(req: ReportRequest):
    node = graph_store.get_node(req.area)
    if not node:
        raise HTTPException(status_code=404, detail=f"Unknown area: {req.area}")
    path = generate_report(req.area)
    db.record_report(req.area, path)
    return FileResponse(path, media_type="application/pdf", filename=path.split("/")[-1])
