from __future__ import annotations

from fastapi import APIRouter, Query

from app.disaster.hospital_matcher import find_hospitals_for_area
from app.graph.graph_store import graph_store

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])


@router.get("")
def list_hospitals(area: str | None = Query(default=None)):
    if area:
        return {"area": area, "hospitals": find_hospitals_for_area(area)}
    return {"hospitals": graph_store.find_nodes(node_type="Hospital")}
