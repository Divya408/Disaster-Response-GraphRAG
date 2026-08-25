from __future__ import annotations

from app.disaster.priority_scorer import calculate_priority
from app.disaster.recommendation_engine import generate_recommendation
from app.disaster.resource_coordinator import get_shortages_only
from app.disaster.shelter_matcher import rank_shelters_for_area
from app.rag.graphrag_engine import answer_query
from app.rag.query_understanding import understand_query


def test_query_understanding_intent_detection():
    qu = understand_query("Which shelters can accommodate flood victims from Area A?")
    assert qu.intent == "shelter_recommendation"
    assert "Area A" in qu.locations


def test_graphrag_answer_shelter_query():
    resp = answer_query("Which shelters can accommodate flood victims from Area A?")
    assert resp.intent == "shelter_recommendation"
    assert len(resp.graph_facts) > 0
    assert resp.confidence > 0
    assert resp.is_demo_mode is True  # no LLM key configured in test env


def test_graphrag_resource_shortage_query():
    resp = answer_query("Which resources are currently insufficient?")
    assert resp.intent == "resource_shortage"
    assert any("Drinking Water" in f["statement"] for f in resp.graph_facts)


def test_shelter_matching_ranks_by_suitability():
    ranked = rank_shelters_for_area("Area A", population_needing_shelter=1200)
    assert ranked[0].suitability_percent >= ranked[-1].suitability_percent


def test_resource_shortage_detection():
    shortages = get_shortages_only()
    assert any(s["resource"] == "Drinking Water" for s in shortages)


def test_priority_scoring_is_transparent():
    priority = calculate_priority("Area A")
    assert priority["is_demo_heuristic"] is True
    assert "calculation" in priority
    assert priority["priority_level"] in ("LOW", "MEDIUM", "HIGH")


def test_recommendation_engine_end_to_end():
    rec = generate_recommendation("Area A")
    assert rec["situation"]["area"] == "Area A"
    assert rec["recommended_shelter"] is not None
    assert len(rec["recommended_actions"]) > 0
    assert "does not replace official disaster-management authorities" in rec["disclaimer"]
