"""
Entity extraction.

This project uses a modular, dependency-light NLP approach rather than a
mandatory large NLP model download: a domain gazetteer (built from the
knowledge base / demo data) drives longest-match-first entity recognition,
combined with regex patterns for numeric facts (capacity, beds, quantities).

The extractor is intentionally modular (`extract_entities`) so it can later
be swapped for a transformer-based NER pipeline or an LLM-based extractor
without changing the rest of the pipeline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from app.graph.entity_normalizer import normalize
from app.utils.demo_data import load_demo_scenario


@dataclass
class ExtractedEntity:
    text: str
    canonical: str
    entity_type: str
    start: int
    end: int


@lru_cache(maxsize=1)
def _category_lookup() -> dict[str, str]:
    """Map canonical entity name -> entity type (Disaster/Location/Shelter/...)."""
    scenario = load_demo_scenario()
    lookup: dict[str, str] = {}
    lookup[scenario["disaster"]["type"]] = "Disaster"
    for loc in scenario["locations"]:
        lookup[loc["name"]] = "Location"
    for shelter in scenario["shelters"]:
        lookup[shelter["name"]] = "Shelter"
    for res in scenario["resources"]:
        lookup[res["name"]] = "Resource"
    for agy in scenario["agencies"]:
        lookup[agy["name"]] = "Agency"
    for hos in scenario["hospitals"]:
        lookup[hos["name"]] = "Hospital"
    for action in scenario["response_actions"]:
        lookup[action] = "ResponseAction"
    return lookup


@lru_cache(maxsize=1)
def _gazetteer_terms() -> list[str]:
    """All known surface forms, sorted longest-first for greedy matching."""
    from app.graph.entity_normalizer import all_known_entities

    terms = sorted(set(all_known_entities().keys()), key=len, reverse=True)
    return terms


def extract_entities(text: str) -> list[ExtractedEntity]:
    """Gazetteer-driven entity recognition over free text."""
    results: list[ExtractedEntity] = []
    lowered = text.lower()
    consumed = [False] * len(text)
    categories = _category_lookup()

    for term in _gazetteer_terms():
        if not term or len(term) < 3:
            continue
        for match in re.finditer(re.escape(term), lowered):
            start, end = match.start(), match.end()
            if any(consumed[start:end]):
                continue
            surface = text[start:end]
            canonical = normalize(surface)
            entity_type = categories.get(canonical, "Entity")
            results.append(ExtractedEntity(surface, canonical, entity_type, start, end))
            for i in range(start, end):
                consumed[i] = True

    # Numeric facts: capacity / beds / quantities, useful for relation extraction.
    results.extend(_extract_numeric_entities(text))

    results.sort(key=lambda e: e.start)
    return results


_NUMERIC_PATTERNS = [
    (re.compile(r"\b(\d{1,3}(?:,\d{3})*|\d+)\s+(?:people|persons)\b", re.I), "Population"),
    (re.compile(r"\b(\d{1,3}(?:,\d{3})*|\d+)\s+(?:liters|litres|packets|kits|pieces|units|beds)\b", re.I), "Quantity"),
]


def _extract_numeric_entities(text: str) -> list[ExtractedEntity]:
    out = []
    for pattern, etype in _NUMERIC_PATTERNS:
        for m in pattern.finditer(text):
            out.append(ExtractedEntity(m.group(0), m.group(1).replace(",", ""), etype, m.start(), m.end()))
    return out
