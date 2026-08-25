"""
Shelter matching and ranking.

Implements a transparent, explainable suitability score (NOT a scientifically
validated formula — this is explicitly documented as a demo heuristic, per
project requirements) based on:
  - available capacity (normalized against the affected population)
  - drinking water availability
  - medical support availability
  - food availability
  - same-area proximity bonus
"""
from __future__ import annotations

from dataclasses import dataclass

from app.graph.graph_store import graph_store


@dataclass
class ShelterMatch:
    shelter_id: str
    suitability_percent: float
    factors: dict
    shelter_data: dict


def rank_shelters_for_area(area_name: str, population_needing_shelter: int | None = None, store=None) -> list[ShelterMatch]:
    store = store or graph_store
    shelters = store.find_nodes(node_type="Shelter")
    if not shelters:
        return []

    area_shelter_ids = {n["node"].get("id") for n in store.get_neighbors(area_name, relation="HAS_SHELTER")}

    results = []
    for s in shelters:
        capacity_score = 0.0
        available = s.get("available_capacity", 0)
        if population_needing_shelter and population_needing_shelter > 0:
            capacity_score = min(1.0, available / population_needing_shelter)
        else:
            capacity_score = min(1.0, available / max(1, s.get("capacity", 1)))

        water_score = 1.0 if s.get("drinking_water") else 0.0
        medical_score = 1.0 if s.get("medical_support") else 0.0
        food_score = 1.0 if s.get("food_available") else 0.0
        proximity_score = 1.0 if s.get("id") in area_shelter_ids else 0.4

        # Transparent, documented weighting (see docs/graphrag_pipeline.md).
        weights = {"capacity": 0.4, "water": 0.2, "medical": 0.15, "food": 0.1, "proximity": 0.15}
        total = (
            weights["capacity"] * capacity_score
            + weights["water"] * water_score
            + weights["medical"] * medical_score
            + weights["food"] * food_score
            + weights["proximity"] * proximity_score
        )
        suitability_percent = round(total * 100, 1)

        results.append(
            ShelterMatch(
                shelter_id=s.get("id"),
                suitability_percent=suitability_percent,
                factors={
                    "capacity_score": round(capacity_score, 2),
                    "water_score": water_score,
                    "medical_score": medical_score,
                    "food_score": food_score,
                    "proximity_score": proximity_score,
                    "weights": weights,
                },
                shelter_data=s,
            )
        )

    results.sort(key=lambda r: r.suitability_percent, reverse=True)
    return results
