# GraphRAG Pipeline

## Why GraphRAG instead of plain vector RAG?

Plain vector RAG retrieves text chunks that are *semantically similar* to a
query, but has no explicit model of how entities relate to each other. A
question like *"Which shelter can accommodate flood victims from Area A and
has drinking water and medical support?"* requires combining facts that may
never appear together in a single sentence:

1. Area A is affected by the flood, with population 1,200.
2. Area A `HAS_SHELTER` Shelter A and Shelter D.
3. Shelter A does **not** have drinking water; Shelter D does.
4. Neither has medical support, but Shelter B (in Area B) does and has 900
   available capacity — a reasonable district-wide fallback recommendation.

A knowledge graph lets the system traverse `Area -> HAS_SHELTER -> Shelter
-> HAS_RESOURCE -> {Drinking Water, Medical Support}` explicitly, which is
the multi-hop reasoning plain retrieval cannot reliably perform.

## Pipeline Stages (see `app/rag/graphrag_engine.py`)

1. **Query Understanding** (`app/rag/query_understanding.py`)
   Classifies intent (`shelter_recommendation`, `resource_shortage`,
   `hospital_lookup`, `agency_lookup`, `action_recommendation`,
   `graph_relationship`, `situation_summary`, `general_query`) and extracts
   entities/locations/constraints using the domain gazetteer.

2. **Graph Retrieval** (`app/graph/graph_queries.py`)
   Depending on intent, runs the relevant graph traversal — e.g.
   `multi_hop_shelter_recommendation()` walks Area → Population → Shelters
   → Resources. Produces a list of `graph_facts` (short factual statements)
   and a human-readable `reasoning_path`.

3. **Hybrid Text Retrieval** (`app/retrieval/hybrid_retriever.py`)
   Retrieves supporting document passages using both:
   - **Vector retrieval**: ChromaDB + sentence-transformers, or a
     scikit-learn TF-IDF cosine-similarity fallback.
   - **BM25 keyword retrieval**: a custom numpy implementation.
   Results are merged with **Reciprocal Rank Fusion (RRF)**.

4. **Reranking** (`app/retrieval/reranker.py`)
   Adjusts the fused score using query/chunk entity overlap and overlap
   with entities discovered during graph retrieval, so passages that
   corroborate the graph facts are promoted. A cross-encoder reranker is
   used automatically if `sentence-transformers` is installed.

5. **Context Fusion** (`app/rag/context_fusion.py`)
   Formats graph facts and retrieved passages into two text blocks used to
   build the LLM prompt.

6. **LLM / Demo Mode** (`app/llm/llm_service.py`)
   Calls a configured OpenAI-compatible endpoint with a system prompt that
   enforces: use only retrieved context, never invent shelters/resources/
   agencies, cite sources, separate facts from recommendations, and never
   claim official emergency authority. If no API key is configured (or the
   call fails), a deterministic **Demo Mode** answer is composed directly
   from the graph facts and retrieved passages and is always clearly
   labeled `[DEMO MODE]`.

7. **Response Packaging**
   The final `GraphRAGResponse` includes: `answer`, `is_demo_mode`,
   `sources` (document + section + relevance score), `reasoning_path`,
   `graph_facts`, `related_entities`, and a `confidence` grounding
   indicator (a simple, transparent proxy: whether graph facts and/or
   retrieved documents backed the answer — not a calibrated probability).

## Multi-Hop Retrieval Example

```text
Area A
 ↓ (affected_population property)
Population: 1,200
 ↓ (HAS_SHELTER)
Candidate Shelters: Shelter A, Shelter D
 ↓ (HAS_RESOURCE)
Resource check: Shelter A has Food only; Shelter D has Water + Food
 ↓ (shelter_matcher.py suitability scoring)
Ranked recommendation with transparent scoring factors
```

## Reranking Weights (documented, not hidden)

`rerank()` combines:
- fused retrieval score (vector + BM25 via RRF)
- `+0.15` per overlapping entity between the query and the chunk
- `+0.25` per overlapping entity between the chunk and the graph-derived
  related entities for this query

This weighting is intentionally simple and fully visible in
`app/retrieval/reranker.py` — it is not a black box.
