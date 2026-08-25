"""
Query understanding.

Classifies the user's query intent and extracts the entities/constraints
mentioned, so the GraphRAG engine knows which graph traversal and domain
logic to invoke. Rule-based (regex + gazetteer), fast, and fully
explainable — appropriate for the bounded disaster-response domain.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.graph.entity_extractor import extract_entities

_INTENT_PATTERNS: list[tuple[str, list[str]]] = [
    ("shelter_recommendation", [r"\bshelter", r"\baccommodate", r"\bdisplaced", r"\bevacuee"]),
    ("resource_shortage", [r"\bresource", r"\bshortage", r"\binsufficient", r"\bavailable resources?\b"]),
    ("hospital_lookup", [r"\bhospital", r"\bmedical\b.*\bbed", r"\bemergency capacity"]),
    ("agency_lookup", [r"\bagency", r"\bagencies", r"\bresponsible for", r"\bwho.*coordinat"]),
    ("action_recommendation", [r"\bprioriti[sz]e", r"\bshould responders", r"\brecommended action"]),
    ("graph_relationship", [r"\brelationship\b", r"\bconnected\b", r"\bshow.*graph"]),
    ("situation_summary", [r"\bsummary\b", r"\bsituation\b", r"\boverview\b"]),
]


@dataclass
class QueryUnderstanding:
    raw_query: str
    intent: str
    entities: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


_CONSTRAINT_KEYWORDS = {
    "capacity": "Capacity",
    "location": "Location",
    "drinking water": "Drinking Water",
    "water": "Drinking Water",
    "medical": "Medical Support",
    "food": "Food Availability",
    "availability": "Availability",
}


def understand_query(query: str) -> QueryUnderstanding:
    lowered = query.lower()

    intent = "general_query"
    for candidate_intent, patterns in _INTENT_PATTERNS:
        if any(re.search(p, lowered) for p in patterns):
            intent = candidate_intent
            break

    extracted = extract_entities(query)
    entities = sorted({e.canonical for e in extracted})
    locations = sorted({e.canonical for e in extracted if e.entity_type == "Location"})

    constraints = [label for kw, label in _CONSTRAINT_KEYWORDS.items() if kw in lowered]

    return QueryUnderstanding(
        raw_query=query, intent=intent, entities=entities, locations=locations, constraints=sorted(set(constraints))
    )
