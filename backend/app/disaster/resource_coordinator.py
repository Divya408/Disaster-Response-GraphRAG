"""Resource coordination: shortage detection and prioritization."""
from __future__ import annotations

from app.graph.graph_store import graph_store


def get_resource_status(store=None) -> list[dict]:
    store = store or graph_store
    resources = store.find_nodes(node_type="Resource")
    out = []
    for r in resources:
        available = r.get("available", 0)
        required = r.get("required", 0)
        shortage = max(0, required - available)
        agency_links = store.get_neighbors(r.get("id"), relation="SUPPLIES", direction="in")
        out.append(
            {
                "resource": r.get("id"),
                "unit": r.get("unit"),
                "available": available,
                "required": required,
                "shortage": shortage,
                "shortage_percent": round((shortage / required) * 100, 1) if required else 0.0,
                "responsible_agencies": [a["node"].get("id") for a in agency_links],
            }
        )
    out.sort(key=lambda x: x["shortage"], reverse=True)
    return out


def get_shortages_only(store=None) -> list[dict]:
    return [r for r in get_resource_status(store) if r["shortage"] > 0]
