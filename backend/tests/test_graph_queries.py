from __future__ import annotations

from app.graph import graph_queries as gq
from app.graph.graph_store import graph_store


def test_graph_has_nodes_and_edges():
    assert graph_store.node_count() > 0
    assert graph_store.edge_count() > 0


def test_find_shelters_near_area():
    shelters = gq.find_shelters_near_area("Area A")
    ids = {s.get("id") for s in shelters}
    assert "Shelter A - Government High School" in ids
    assert "Shelter D - Town Community Center" in ids


def test_find_available_resources():
    resources = gq.find_available_resources()
    names = {r.get("id") for r in resources}
    assert "Drinking Water" in names


def test_find_hospitals_with_beds():
    hospitals = gq.find_hospitals_with_beds(min_available_beds=1)
    assert len(hospitals) >= 1


def test_find_agencies_for_action():
    agencies = gq.find_agencies_for_action("Evacuation")
    names = {a.get("id") for a in agencies}
    assert "Fire and Rescue Department" in names


def test_find_affected_population():
    pop = gq.find_affected_population("Area A")
    assert pop == 1200


def test_multi_hop_shelter_recommendation():
    result = gq.multi_hop_shelter_recommendation("Area A")
    assert result["population_affected"] == 1200
    assert len(result["shelters"]) > 0


def test_find_alternative_shelters():
    alternatives = gq.find_alternative_shelters(exclude_shelter="Shelter A - Government High School", min_capacity=100)
    ids = {a.get("id") for a in alternatives}
    assert "Shelter A - Government High School" not in ids
    assert "Shelter B - Community Hall" in ids
