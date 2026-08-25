from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.graph.graph_builder import rebuild_full_graph
from app.graph.graph_queries import find_connected_entities
from app.graph.graph_store import graph_store

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.post("/build")
def build_graph():
    return rebuild_full_graph()


@router.get("")
def get_graph():
    return {
        "backend": graph_store.backend_name,
        "nodes": graph_store.all_nodes(),
        "edges": graph_store.all_edges(),
    }


@router.get("/node/{node_id}")
def get_node(node_id: str, depth: int = 1):
    node = graph_store.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    subgraph = find_connected_entities(node_id, depth=depth)
    return {"node": node, "subgraph": subgraph}
