"""
Generates a structured disaster-response recommendation for an affected
area, combining shelter matching, resource shortages, hospital availability,
responsible agencies, and the transparent priority score.
"""
from __future__ import annotations

from app.disaster.hospital_matcher import find_hospitals_for_area
from app.disaster.priority_scorer import calculate_priority
from app.disaster.resource_coordinator import get_shortages_only
from app.disaster.shelter_matcher import rank_shelters_for_area
from app.graph.graph_queries import find_agencies_for_action
from app.graph.graph_store import graph_store


def generate_recommendation(area_name: str, store=None) -> dict:
    store = store or graph_store
    area = store.get_node(area_name) or {}
    population = area.get("affected_population", 0)

    priority = calculate_priority(area_name, store)
    shelters = rank_shelters_for_area(area_name, population_needing_shelter=population, store=store)
    top_shelter = shelters[0] if shelters else None
    shortages = get_shortages_only(store)
    hospitals = find_hospitals_for_area(area_name, store=store)
    evacuation_agencies = find_agencies_for_action("Evacuation", store)

    actions = []
    if priority["priority_level"] in ("HIGH", "MEDIUM"):
        actions.append("Prioritize evacuation of the affected population.")
    if top_shelter:
        actions.append(f"Allocate available capacity at {top_shelter.shelter_id}.")
    for shortage in shortages[:3]:
        actions.append(f"Dispatch additional {shortage['resource']} ({shortage['shortage']} {shortage['unit']} shortage).")
    if hospitals:
        actions.append(f"Coordinate medical referral through {hospitals[0]['id']} if emergency care is needed.")
    if not actions:
        actions.append("Continue monitoring the situation; no urgent shortages detected in current data.")

    return {
        "situation": {
            "area": area_name,
            "disaster_type": "Flood",
            "affected_population": population,
        },
        "priority": priority,
        "recommended_shelter": {
            "id": top_shelter.shelter_id if top_shelter else None,
            "suitability_percent": top_shelter.suitability_percent if top_shelter else None,
            "available_capacity": top_shelter.shelter_data.get("available_capacity") if top_shelter else None,
        } if top_shelter else None,
        "alternative_shelters": [
            {"id": s.shelter_id, "suitability_percent": s.suitability_percent}
            for s in shelters[1:4]
        ],
        "resource_shortages": shortages,
        "hospitals": [
            {"id": h["id"], "available_emergency_beds": h.get("available_emergency_beds")}
            for h in hospitals
        ],
        "responsible_agencies": [a.get("id") for a in evacuation_agencies],
        "recommended_actions": actions,
        "disclaimer": (
            "This is AI-assisted decision support based on synthetic demo data. "
            "It does not replace official disaster-management authorities or emergency command decisions."
        ),
    }
