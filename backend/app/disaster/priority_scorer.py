"""
Response priority scoring.

IMPORTANT: This is a DEMO PRIORITIZATION HEURISTIC for academic
demonstration purposes only. It is NOT a scientifically validated
emergency-management formula. The full calculation is returned alongside
the score so it is always transparent to the user.
"""
from __future__ import annotations

from app.disaster.resource_coordinator import get_resource_status
from app.graph.graph_store import graph_store

_SEVERITY_WEIGHT = {"LOW": 0.3, "MEDIUM": 0.6, "HIGH": 1.0}


def calculate_priority(area_name: str, store=None) -> dict:
    store = store or graph_store
    area = store.get_node(area_name) or {}
    population = area.get("affected_population", 0)

    incidents = [
        n["node"] for n in store.get_neighbors(area_name, relation="OCCURRED_IN", direction="in")
    ]
    severity = "MEDIUM"
    if incidents:
        severity = incidents[0].get("severity", "MEDIUM")

    shelters = [n["node"] for n in store.get_neighbors(area_name, relation="HAS_SHELTER")]
    total_available_capacity = sum(s.get("available_capacity", 0) for s in shelters)
    shelter_gap = max(0, population - total_available_capacity)

    shortages = get_resource_status(store)
    total_shortage_percent = (
        sum(r["shortage_percent"] for r in shortages) / len(shortages) if shortages else 0.0
    )

    # Transparent, documented demo heuristic (0-100 scale):
    population_component = min(1.0, population / 2000) * 30
    severity_component = _SEVERITY_WEIGHT.get(severity, 0.5) * 30
    shelter_gap_component = min(1.0, shelter_gap / max(1, population or 1)) * 25
    resource_component = min(1.0, total_shortage_percent / 100) * 15

    score = round(population_component + severity_component + shelter_gap_component + resource_component, 1)

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "area": area_name,
        "priority_score": score,
        "priority_level": level,
        "is_demo_heuristic": True,
        "disclaimer": "Demo prioritization heuristic for academic demonstration only — not an official emergency-management formula.",
        "calculation": {
            "population_affected": population,
            "population_component": round(population_component, 1),
            "severity": severity,
            "severity_component": round(severity_component, 1),
            "shelter_capacity_gap": shelter_gap,
            "shelter_gap_component": round(shelter_gap_component, 1),
            "avg_resource_shortage_percent": round(total_shortage_percent, 1),
            "resource_component": round(resource_component, 1),
        },
    }
