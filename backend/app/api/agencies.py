from __future__ import annotations

from fastapi import APIRouter, Query

from app.graph.graph_queries import find_agencies_for_action
from app.graph.graph_store import graph_store

router = APIRouter(prefix="/api/agencies", tags=["agencies"])


@router.get("")
def list_agencies(responsible_for: str | None = Query(default=None)):
    if responsible_for:
        return {"action": responsible_for, "agencies": find_agencies_for_action(responsible_for)}
    return {"agencies": graph_store.find_nodes(node_type="Agency")}
