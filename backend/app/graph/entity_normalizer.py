"""
Entity normalization.

Disaster documents refer to the same real-world entity using slightly
different surface forms, e.g. "Salem", "Salem District", "salem district".
This module builds an alias -> canonical-id map from the demo dataset and
exposes a `normalize()` function used by both the entity extractor and the
graph builder so that duplicate nodes are not created for the same entity.
"""
from __future__ import annotations

import re
from functools import lru_cache

from app.utils.demo_data import load_demo_scenario


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip().lower()
    if text.startswith("the "):
        text = text[4:]
    return text


@lru_cache(maxsize=1)
def _build_alias_map() -> dict[str, str]:
    """Returns {cleaned_alias: canonical_name}."""
    scenario = load_demo_scenario()
    alias_map: dict[str, str] = {}

    def register(name: str, aliases: list[str] | None = None):
        alias_map[_clean(name)] = name
        for alias in aliases or []:
            alias_map[_clean(alias)] = name

    for loc in scenario["locations"]:
        register(loc["name"], loc.get("aliases"))
    for shelter in scenario["shelters"]:
        register(shelter["name"])
        # also register short forms like "Shelter A"
        short = shelter["name"].split(" - ")[0]
        alias_map.setdefault(_clean(short), shelter["name"])
    for res in scenario["resources"]:
        register(res["name"])
    for agy in scenario["agencies"]:
        register(agy["name"])
    for hos in scenario["hospitals"]:
        register(hos["name"])
        short = hos["name"].split(" (Demo)")[0]
        alias_map.setdefault(_clean(short), hos["name"])
    register(scenario["disaster"]["type"])
    for action in scenario["response_actions"]:
        register(action)

    return alias_map


def normalize(text: str) -> str:
    """
    Return the canonical form of an entity mention if it is a known alias,
    otherwise return the input stripped of extra whitespace (title-cased
    only when the input was already capitalized, to avoid mangling proper
    nouns we don't recognize).
    """
    alias_map = _build_alias_map()
    cleaned = _clean(text)
    if cleaned in alias_map:
        return alias_map[cleaned]

    # Fuzzy fallback: strip trailing punctuation and try again.
    cleaned2 = cleaned.rstrip(".,;:")
    if cleaned2 in alias_map:
        return alias_map[cleaned2]

    return " ".join(text.split())


def all_known_entities() -> dict[str, str]:
    """Expose the alias map for gazetteer-based entity extraction."""
    return dict(_build_alias_map())
