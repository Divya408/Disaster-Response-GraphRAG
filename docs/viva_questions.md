# Viva Preparation — Questions & Answers

Simple, student-friendly answers you can use in your final-year project
defense. Each answer also points to the relevant code file so you can show
the examiner exactly where it's implemented.

---

**1. What is RAG?**
Retrieval-Augmented Generation. Instead of relying only on what a language
model memorized during training, RAG retrieves relevant information from an
external source (documents, a database, a graph) at query time and gives it
to the model as context, so answers can be grounded in real, up-to-date
evidence.

**2. What is GraphRAG?**
GraphRAG is RAG that retrieves from a **knowledge graph** (entities and
relationships) in addition to, or instead of, plain text chunks. It lets the
system follow explicit relationships (e.g. Area → HAS_SHELTER → Shelter →
HAS_RESOURCE → Drinking Water) to answer questions that require combining
facts from multiple places.

**3. Why GraphRAG instead of normal RAG?**
Normal (vector-only) RAG finds text that is *semantically similar* to the
query, but doesn't understand structured relationships. Multi-hop questions
like "which shelter near Area A has both capacity and medical support"
need the system to connect several separate facts — that's what the graph
traversal in `app/graph/graph_queries.py` does.

**4. What is a knowledge graph?**
A graph database of entities (nodes) and the relationships between them
(edges), e.g. `Shelter B -[LOCATED_IN]-> Area B`.

**5. What is a node?**
A single entity in the graph — e.g. a Shelter, a Location, an Agency.

**6. What is an edge?**
A directed, typed relationship between two nodes — e.g.
`Agency -[RESPONSIBLE_FOR]-> ResponseAction`.

**7. What is multi-hop reasoning?**
Answering a question that requires traversing more than one relationship —
e.g. Area → Shelter → Resource is two hops. See
`multi_hop_shelter_recommendation()` in `app/graph/graph_queries.py`.

**8. Why Neo4j?**
Neo4j is a mature, widely used graph database with a query language
(Cypher) built for exactly this kind of relationship traversal. This
project uses it as the *preferred* backend but automatically falls back to
an in-memory graph if Neo4j isn't available, so the demo never breaks.

**9. Why ChromaDB?**
ChromaDB is a lightweight, easy-to-run vector database for storing document
embeddings and doing semantic similarity search. Like Neo4j, it's optional
here — a TF-IDF fallback is used if it's not installed.

**10. What is hybrid retrieval?**
Combining more than one retrieval method — here, semantic (vector) search
and keyword (BM25) search — and merging their ranked results (this project
uses Reciprocal Rank Fusion) so that both semantic *and* exact-keyword
matches are found.

**11. What is BM25?**
A classic keyword-ranking algorithm (an improvement on TF-IDF) that scores
documents based on term frequency, inverse document frequency, and document
length normalization. Implemented from scratch with numpy in
`app/retrieval/bm25_retriever.py`.

**12. What are embeddings?**
Numeric vector representations of text such that semantically similar text
has vectors that are close together, enabling similarity search.

**13. What is reranking?**
A second-pass scoring step that reorders initially retrieved results using
additional signals (here: entity overlap with the query and with graph
facts) to push the most relevant results to the top. See
`app/retrieval/reranker.py`.

**14. How are entities extracted?**
Using a **gazetteer** (a list of known entity names built from the
structured demo data) matched against document text with longest-match-first
regex matching, plus numeric-pattern rules for things like capacity and bed
counts. See `app/graph/entity_extractor.py`. This is modular — it can be
swapped for a transformer NER model or an LLM-based extractor later.

**15. How are relationships extracted?**
Using regex patterns tuned to common sentence structures in the disaster
documents (e.g. "X is located in Y", "X is responsible for Y"). See
`app/graph/relation_extractor.py`. An optional LLM-assisted extraction hook
also exists (`extract_relations_llm`) for when an LLM is configured.

**16. How do you prevent hallucination?**
The LLM system prompt (`app/llm/llm_service.py`) explicitly instructs the
model to use only the retrieved graph and document context, never invent
shelters/resources/agencies, and say when information is unavailable. In
Demo Mode, answers are built deterministically from retrieved facts only —
there is no generative step that could hallucinate.

**17. How are citations generated?**
Every retrieved document chunk carries its source document name and
section/page label from parsing time (`app/documents/parser.py`); these are
attached to the response as `sources` (`app/rag/context_fusion.py`).

**18. What if there is no relevant information?**
The system says so explicitly rather than guessing — both the LLM prompt
rules and the Demo Mode answer composer (`_compose_demo_answer` in
`app/rag/graphrag_engine.py`) are written to state when no matching facts or
documents were found.

**19. What if Neo4j is unavailable?**
`build_graph_store()` in `app/graph/graph_store.py` tries to connect to
Neo4j; on any failure (not configured, driver missing, connection refused,
auth failure) it transparently falls back to an in-memory `networkx` graph
with an identical interface, so the rest of the app doesn't need to know
which backend is active.

**20. What if the victim's phone has no battery?**
The system does not depend on the victim's smartphone. Data is collected
**responder-side** — by volunteers, shelters, hospitals, police, and fire &
rescue — via the Offline Data Entry page, which works even without
connectivity and marks records "Pending Sync" until they can be
synchronized. See `app/disaster/offline_sync.py` and the "Offline Mode"
frontend page.

**21. What if there is no internet?**
Responders can still record assessments locally (stored in SQLite with
status "Pending Sync"); a `sync` operation later pushes them centrally once
connectivity returns. This is a simplified, simulated version of a
store-and-forward pattern appropriate for an academic project.

**22. How does offline mode work?**
`POST /api/offline/records` stores a record with `status='Pending Sync'`.
`GET /api/offline/status` shows the pending count. `POST /api/offline/sync`
marks all pending records as synced. See `app/disaster/offline_sync.py`.

**23. What is your research contribution?**
"A graph-enhanced retrieval framework for multi-hop disaster-response
information retrieval and decision support" — see
`docs/research_problem.md`.

**24. How will you evaluate GraphRAG?**
`scripts/evaluate.py` compares Vector-only RAG, GraphRAG-only, and Hybrid
Graph+Vector RAG on a small hand-labeled question set, computing
Precision@K, Recall@K, Hit Rate, and a multi-hop accuracy proxy — computed
live, not fabricated.

**25. What are the limitations?**
(1) All data is synthetic demo data, not a real disaster feed. (2) Entity
and relationship extraction is rule/gazetteer-based, not a trained NER
model, so it won't generalize to arbitrary unseen documents without
extending the gazetteer/patterns. (3) The priority score is an explicitly
documented demo heuristic, not a validated emergency-management formula.
(4) Demo Mode answers are template-based, not generative, when no LLM key
is configured. See `docs/limitations_and_future_scope.md`.

**26. Why not use only vector RAG?**
Because vector similarity alone cannot reliably answer multi-hop,
relationship-based questions (see Q3) — it retrieves *similar text*, not
*connected facts*.

**27. What is multi-hop retrieval?** *(see also Q7)*
Retrieval that must traverse more than one relationship edge to assemble
the full answer, e.g. Area → affected population → candidate shelters →
each shelter's resource availability.

**28. How does resource matching work?**
`app/disaster/resource_coordinator.py` computes `shortage = max(0, required
- available)` per resource from the graph, and looks up the responsible
agency via the `SUPPLIES` relationship.

**29. How does shelter ranking work?**
`app/disaster/shelter_matcher.py` computes a transparent, documented
weighted score from available capacity (relative to population needing
shelter), drinking water, medical support, food availability, and
same-area proximity. Weights are visible in the code and are explicitly
labeled as a demo heuristic, not a validated formula.

**30. Can this system replace disaster-management authorities?**
No. Every recommendation includes the disclaimer: *"This system provides
AI-assisted decision support and does not replace official
disaster-management authorities or emergency command decisions."* The
system is designed to help coordinators think faster, not to issue
commands.

---

### Bonus questions

**31. Why SQLite alongside Neo4j and ChromaDB?**
Different data has different natural shapes: relationships → graph
database; document semantics → vector database; simple operational records
(query logs, uploaded document metadata, generated reports, offline sync
records) → a plain relational table is simplest and requires no extra
infrastructure.

**32. How is entity normalization handled?**
`app/graph/entity_normalizer.py` builds an alias → canonical-name map from
the demo dataset (e.g. "Salem", "Salem district" → "Salem District") so
that document mentions and structured data merge into the same graph node
instead of creating duplicates.

**33. Is the reranker a machine-learning model?**
By default no — it's a transparent, explainable scoring function (fused
retrieval score + entity-overlap bonuses) with no model download required.
If `sentence-transformers` is installed, an optional cross-encoder reranker
(`try_cross_encoder_rerank`) can be used instead.
