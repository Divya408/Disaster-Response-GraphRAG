"""
Relationship extraction.

Pattern-based (regex) relation extraction tuned to the sentence structures
found in the disaster-response demo documents, e.g.:

    "Shelter A is located in Area B and can accommodate 500 people."
    "The Fire and Rescue Department is responsible for rescue operations."

Each rule returns (subject, predicate, object) triples. The module is
deliberately modular: `RELATION_RULES` can be extended with more patterns,
or replaced by an LLM-based extractor via `extract_relations_llm` (used only
when an LLM API key is configured; the app works without it).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.graph.entity_normalizer import normalize


@dataclass
class ExtractedRelation:
    subject: str
    predicate: str
    obj: str
    evidence: str


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"([A-Z][\w \-']+?) is located in ([A-Z][\w \-']+)", re.I), "LOCATED_IN"),
    (re.compile(r"([A-Z][\w \-']+?) can accommodate (\d[\d,]*)\s*people", re.I), "HAS_CAPACITY"),
    (re.compile(r"([A-Z][\w \-']+?) has capacity (\d[\d,]*)", re.I), "HAS_CAPACITY"),
    (re.compile(r"([A-Z][\w \-']+?) is responsible for ([A-Z][\w \-']+)", re.I), "RESPONSIBLE_FOR"),
    (re.compile(r"([A-Z][\w \-']+?) operates? in ([A-Z][\w \-']+)", re.I), "OPERATES_IN"),
    (re.compile(r"([A-Z][\w \-']+?) requires? ([A-Z][\w \-']+)", re.I), "REQUIRES"),
    (re.compile(r"([A-Z][\w \-']+?) has (?:both )?drinking water", re.I), "HAS_RESOURCE:Drinking Water"),
    (re.compile(r"([A-Z][\w \-']+?) has (?:both )?medical support", re.I), "HAS_RESOURCE:Medical Support"),
    (re.compile(r"([A-Z][\w \-']+?) affected ([A-Z][\w \-']+)", re.I), "AFFECTED"),
    (re.compile(r"([A-Z][\w \-']+?) occurred in ([A-Z][\w \-']+)", re.I), "OCCURRED_IN"),
]


def extract_relations(text: str) -> list[ExtractedRelation]:
    relations: list[ExtractedRelation] = []
    for sentence in _split_sentences(text):
        for pattern, predicate in _RULES:
            for match in pattern.finditer(sentence):
                if ":" in predicate:
                    pred, fixed_obj = predicate.split(":", 1)
                    subj = normalize(match.group(1))
                    relations.append(ExtractedRelation(subj, pred, fixed_obj, sentence))
                else:
                    groups = match.groups()
                    subj = normalize(groups[0])
                    obj = normalize(groups[1]) if len(groups) > 1 else ""
                    relations.append(ExtractedRelation(subj, predicate, obj, sentence))
    return relations


def extract_relations_llm(text: str, llm_call) -> list[ExtractedRelation]:
    """
    Optional LLM-assisted relation extraction hook. `llm_call` is a callable
    (prompt: str) -> str that returns newline-delimited "subject | predicate |
    object" triples. Only used when an LLM is configured; falls back silently
    to the empty list on any error so the pipeline never depends on it.
    """
    prompt = (
        "Extract subject|predicate|object relationship triples from the "
        "following disaster-response text. One triple per line, using the "
        "exact format 'subject|predicate|object'. Text:\n\n" + text
    )
    try:
        raw = llm_call(prompt)
    except Exception:
        return []
    relations = []
    for line in raw.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3 and all(parts):
            relations.append(ExtractedRelation(normalize(parts[0]), parts[1].upper().replace(" ", "_"), normalize(parts[2]), line))
    return relations
