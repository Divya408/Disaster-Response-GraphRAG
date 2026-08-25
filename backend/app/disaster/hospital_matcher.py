"""Hospital coordination: find suitable hospitals for patient referral."""
from __future__ import annotations

from app.graph.graph_store import graph_store


def find_hospitals_for_area(area_name: str, min_available_beds: int = 1, store=None) -> list[dict]:
    store = store or graph_store
    hospitals = store.find_nodes(node_type="Hospital")

    def in_same_area(h: dict) -> bool:
        links = store.get_neighbors(h.get("id"), relation="LOCATED_IN")
        return any(n["node"].get("id") == area_name for n in links)

    same_area = [h for h in hospitals if in_same_area(h)]
    candidates = same_area if same_area else hospitals

    ranked = sorted(
        [h for h in candidates if h.get("available_emergency_beds", 0) >= min_available_beds],
        key=lambda h: h.get("available_emergency_beds", 0),
        reverse=True,
    )
    return ranked
