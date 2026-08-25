"""
GraphRAG engine — the central orchestrator implementing the pipeline:

    Query -> Query Understanding -> Graph Retrieval (multi-hop)
          -> Text Retrieval (hybrid: vector + BM25) -> Reranking
          -> Context Fusion -> LLM (or Demo Mode) -> Grounded Answer
          -> Sources + Reasoning Path + Recommendations
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.disaster.hospital_matcher import find_hospitals_for_area
from app.disaster.resource_coordinator import get_shortages_only, get_resource_status
from app.disaster.shelter_matcher import rank_shelters_for_area
from app.graph.graph_queries import (
    find_agencies_for_action,
    find_affected_population,
    multi_hop_shelter_recommendation,
)
from app.graph.graph_store import graph_store
from app.llm.llm_service import call_llm
from app.llm.prompt_templates import build_graphrag_prompt
from app.rag.context_fusion import build_sources, format_graph_context, format_text_context
from app.rag.query_understanding import understand_query
from app.retrieval.hybrid_retriever import hybrid_retriever
from app.retrieval.reranker import rerank


@dataclass
class GraphRAGResponse:
    query: str
    intent: str
    answer: str
    is_demo_mode: bool
    sources: list[dict] = field(default_factory=list)
    reasoning_path: list[str] = field(default_factory=list)
    graph_facts: list[dict] = field(default_factory=list)
    related_entities: list[str] = field(default_factory=list)
    confidence: float = 0.0


def _graph_facts_for_query(qu) -> tuple[list[dict], list[str], list[str]]:
    """Returns (facts, reasoning_path, related_entity_ids) depending on intent."""
    facts: list[dict] = []
    reasoning_path: list[str] = []
    related: set[str] = set()
    store = graph_store

    area = qu.locations[0] if qu.locations else None

    if qu.intent == "shelter_recommendation":
        if area:
            result = multi_hop_shelter_recommendation(area, store)
            reasoning_path.append(f"Area: {area}")
            pop = result.get("population_affected")
            reasoning_path.append(f"Affected population: {pop if pop is not None else 'unknown'}")
            ranked = rank_shelters_for_area(area, population_needing_shelter=pop, store=store)
            for s in ranked[:4]:
                facts.append({
                    "statement": (
                        f"{s.shelter_id}: available capacity {s.shelter_data.get('available_capacity')}, "
                        f"drinking water={s.shelter_data.get('drinking_water')}, "
                        f"medical support={s.shelter_data.get('medical_support')}, "
                        f"food available={s.shelter_data.get('food_available')} "
                        f"(suitability {s.suitability_percent}%)"
                    )
                })
                related.add(s.shelter_id)
            if ranked:
                reasoning_path.append(f"Top candidate shelter: {ranked[0].shelter_id} ({ranked[0].suitability_percent}% suitability)")
        else:
            for s in store.find_nodes(node_type="Shelter"):
                facts.append({"statement": f"{s.get('id')}: available capacity {s.get('available_capacity')}"})
                related.add(s.get("id"))

    elif qu.intent == "resource_shortage":
        shortages = get_resource_status(store)
        for r in shortages:
            facts.append({
                "statement": f"{r['resource']}: available {r['available']} {r['unit']}, required {r['required']} {r['unit']}, shortage {r['shortage']} {r['unit']} (responsible: {', '.join(r['responsible_agencies']) or 'unassigned'})"
            })
            related.add(r["resource"])
        reasoning_path.append("Retrieved resource inventory from knowledge graph (Disaster -REQUIRES-> Resource).")

    elif qu.intent == "hospital_lookup":
        hospitals = find_hospitals_for_area(area, store=store) if area else store.find_nodes(node_type="Hospital")
        for h in hospitals:
            facts.append({
                "statement": f"{h.get('id')}: available emergency beds {h.get('available_emergency_beds')}/{h.get('emergency_beds')}, facilities: {', '.join(h.get('facilities', []))}"
            })
            related.add(h.get("id"))
        reasoning_path.append(f"Retrieved hospitals {'near ' + area if area else 'in the district'} with available emergency capacity.")

    elif qu.intent == "agency_lookup":
        action_terms = [e for e in qu.entities if store.get_node(e) and store.get_node(e).get("type") == "ResponseAction"]
        action = action_terms[0] if action_terms else "Evacuation"
        agencies = find_agencies_for_action(action, store)
        for a in agencies:
            facts.append({"statement": f"{a.get('id')} is responsible for {action}."})
            related.add(a.get("id"))
        reasoning_path.append(f"Graph traversal: Agency -RESPONSIBLE_FOR-> {action}")

    elif qu.intent in ("action_recommendation", "situation_summary"):
        target_area = area or "Area A"
        from app.disaster.recommendation_engine import generate_recommendation
        rec = generate_recommendation(target_area, store)
        for action in rec["recommended_actions"]:
            facts.append({"statement": action})
        reasoning_path.append(f"Generated structured recommendation for {target_area} (priority: {rec['priority']['priority_level']}).")
        related.add(target_area)

    elif qu.intent == "graph_relationship":
        if area:
            from app.graph.graph_queries import find_connected_entities
            sub = find_connected_entities(area, depth=2, store=store)
            for edge in sub["edges"][:15]:
                facts.append({"statement": f"{edge['source']} -{edge['relation']}-> {edge['target']}"})
            related.update(n.get("id") for n in sub["nodes"] if n.get("id"))
            reasoning_path.append(f"Expanded 2-hop subgraph around {area}.")

    else:
        # general_query fallback: pull any facts touching mentioned entities
        for entity in qu.entities[:5]:
            node = store.get_node(entity)
            if node:
                facts.append({"statement": f"{entity} ({node.get('type')}): {node}"})
                related.add(entity)

    return facts, reasoning_path, sorted(related)


def answer_query(query: str, top_k: int = 5) -> GraphRAGResponse:
    qu = understand_query(query)

    graph_facts, reasoning_path, related_entities = _graph_facts_for_query(qu)
    graph_context = format_graph_context(graph_facts)

    retrieved = hybrid_retriever.retrieve(query, top_k=top_k)
    retrieved = rerank(query, retrieved, graph_entities=related_entities)
    text_context = format_text_context(retrieved)
    sources = build_sources(retrieved)

    prompt = build_graphrag_prompt(query, graph_context, text_context)
    llm_text, is_real_llm = call_llm(prompt)

    if not is_real_llm:
        llm_text = _compose_demo_answer(qu, graph_facts, retrieved)

    confidence = _estimate_confidence(graph_facts, retrieved)

    return GraphRAGResponse(
        query=query,
        intent=qu.intent,
        answer=llm_text,
        is_demo_mode=not is_real_llm,
        sources=sources,
        reasoning_path=reasoning_path or ["No multi-hop graph path was needed for this query type."],
        graph_facts=graph_facts,
        related_entities=related_entities,
        confidence=confidence,
    )


def _estimate_confidence(graph_facts: list[dict], retrieved) -> float:
    """A simple, transparent grounding indicator: proportion of the answer
    that is backed by retrieved graph facts and/or document sources."""
    score = 0.0
    if graph_facts:
        score += 0.6
    if retrieved:
        score += 0.4
    return round(min(1.0, score), 2)


def _compose_demo_answer(qu, graph_facts: list[dict], retrieved) -> str:
    lines = ["[DEMO MODE — deterministic answer generated from retrieved graph + document context, not a live LLM call]", ""]

    if graph_facts:
        lines.append("Facts (from knowledge graph):")
        for f in graph_facts[:6]:
            lines.append(f"  - {f['statement']}")
        lines.append("")
    else:
        lines.append("No directly matching graph facts were found for this query in the current demo dataset.")
        lines.append("")

    if retrieved:
        lines.append("Supporting evidence (from retrieved documents):")
        for item in retrieved[:3]:
            snippet = item.chunk.text[:180].strip()
            lines.append(f"  - \"{snippet}...\" (Source: {item.chunk.document_name} — {item.chunk.section_label})")
        lines.append("")

    lines.append(
        "Recommendation: Based on the information above, coordinators should verify current "
        "on-ground conditions before acting. This is AI-assisted decision support based on "
        "synthetic demo data, not an official emergency directive — always contact official "
        "disaster-management authorities for real incidents."
    )
    return "\n".join(lines)
