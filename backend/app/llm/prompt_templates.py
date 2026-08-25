"""Prompt construction for the GraphRAG LLM call."""
from __future__ import annotations


def build_graphrag_prompt(query: str, graph_context: str, text_context: str) -> str:
    return f"""User question:
{query}

--- Retrieved Knowledge Graph Context ---
{graph_context or "(no graph facts retrieved)"}

--- Retrieved Document Context ---
{text_context or "(no document passages retrieved)"}

Instructions:
Answer the user's question using ONLY the information above. Cite sources by
document name and page/section where applicable. If capacity, resources, or
responsibilities are not covered above, say the information is not available
rather than guessing. Clearly separate "Facts" from "Recommendations". End
with a one-line reminder that this is AI-assisted decision support, not an
official directive.
"""
