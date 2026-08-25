# Results Template

Use this template to record your own evaluation run's results (run
`python scripts/evaluate.py` from inside `backend/` and paste the numbers
below — do not reuse example numbers from documentation as if they were
your own results; always regenerate them).

## Run Metadata

- Date run: __________
- Git commit / project version: __________
- LLM configuration: DEMO_MODE = [true/false], model = __________
- Graph backend used: [Neo4j / in-memory fallback]
- Vector backend used: [ChromaDB / TF-IDF fallback]

## Vector-Only RAG

| Query | Hop Type | Precision@5 | Recall@5 | Hit Rate | Response Time (s) |
|---|---|---|---|---|---|
| | | | | | |

**Averages:** Precision@5 = ____, Recall@5 = ____, Hit Rate = ____

## GraphRAG (graph-only)

| Query | Hop Type | Multi-hop Accuracy | Graph Facts Returned | Response Time (s) |
|---|---|---|---|---|
| | | | | |

**Average multi-hop accuracy:** ____

## Hybrid Graph + Vector RAG

| Query | Hop Type | Precision@5 | Recall@5 | Hit Rate | Multi-hop Accuracy | Faithfulness (proxy) | Response Time (s) |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

**Averages:** Precision@5 = ____, Recall@5 = ____, Hit Rate = ____, Multi-hop Accuracy = ____, Faithfulness = ____

## Discussion

- Did Hybrid outperform Vector-only on multi-hop questions? __________
- Did GraphRAG's multi-hop accuracy exceed Vector-only's recall on the same
  questions? __________
- Any surprising results, and what do you think explains them? __________

## Note on Methodology

Metrics here are computed against a small, hand-labeled question set
defined in `scripts/evaluate.py` (`EVAL_SET`), using document-level
precision/recall (a chunk retrieval "hits" if it comes from a
manually-labeled relevant document) and an entity-overlap proxy for
multi-hop accuracy. This is appropriate for demonstrating the evaluation
methodology in a final-year project; a larger, independently-labeled
question set would be needed for a publishable research claim.
