from __future__ import annotations

from fastapi import APIRouter, Query

from app.disaster.shelter_matcher import rank_shelters_for_area
from app.graph.graph_store import graph_store

router = APIRouter(prefix="/api/shelters", tags=["shelters"])


@router.get("")
def list_shelters(area: str | None = Query(default=None)):
    if area:
        ranked = rank_shelters_for_area(area)
        return {
            "area": area,
            "shelters": [
                {"id": r.shelter_id, "suitability_percent": r.suitability_percent, "factors": r.factors, **r.shelter_data}
                for r in ranked
            ],
        }
    return {"shelters": graph_store.find_nodes(node_type="Shelter")}
