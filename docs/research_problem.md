# Research Problem

## Problem Statement

During natural disasters such as floods, cyclones, earthquakes, landslides,
and droughts, critical information is distributed across emergency reports,
government guidelines, shelter records, resource inventories, hospitals,
relief organizations, and response agencies. Emergency responders may
struggle to quickly understand relationships between affected locations,
disaster types, severity, affected population, shelters, shelter capacity,
available resources, hospitals, emergency services, response agencies,
evacuation procedures, and relief requirements.

Traditional keyword search or basic vector RAG retrieves relevant text
passages but may fail to understand complex relationships and multi-hop
queries across multiple documents (e.g., "which shelter near the affected
area has both spare capacity and medical support" requires combining facts
from several different source sentences/documents).

## Proposed Approach

This project proposes a **Knowledge Graph + GraphRAG + LLM** system that
connects entities and relationships extracted from disaster-related
documents (and structured operational data), enabling evidence-grounded,
multi-hop decision support for disaster-response coordinators.

## Research Contribution

> "A graph-enhanced retrieval framework for multi-hop disaster-response
> information retrieval and decision support."

## Research Questions

1. Does GraphRAG improve multi-hop disaster information retrieval compared
   with vector-only RAG?
2. Does combining graph retrieval and semantic retrieval improve answer
   relevance?
3. Does explicit relationship reasoning improve resource and shelter
   recommendations?
4. Does source-grounded GraphRAG reduce unsupported responses?

`scripts/evaluate.py` implements a small, reproducible evaluation harness
comparing **Vector-only RAG**, **GraphRAG (graph-only)**, and **Hybrid
Graph+Vector RAG** against a hand-labeled question set, computing
Precision@K, Recall@K, Hit Rate, and a multi-hop accuracy proxy (see
`docs/results_template.md` for how to report findings — the script computes
live numbers from this project's own demo dataset and never fabricates
results).

## Scope and Non-Goals

- This is a **text/data-based** system. Computer vision, IoT sensors, and
  mobile GPS are explicitly **not** required for the system to function.
- The system is a **decision-support tool**, not an emergency command
  system, and does not claim official emergency authority. See
  `docs/viva_questions.md`, question 30.
- All disaster, shelter, resource, hospital, and agency data shipped with
  this project is **synthetic demo data** created for academic
  demonstration and is clearly labeled as such throughout the codebase and
  UI.
