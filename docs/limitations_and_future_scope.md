# Limitations and Future Scope

## Limitations

1. **Synthetic demo data.** All disaster, shelter, resource, hospital, and
   agency data shipped with this project is synthetic, created for academic
   demonstration. It must not be presented or used as real disaster
   information.
2. **Rule/gazetteer-based extraction.** Entity and relationship extraction
   uses regex and a gazetteer built from the demo dataset, not a trained
   NER/relation-extraction model. It works well on the demo documents'
   sentence patterns but will need pattern/gazetteer extension (or a
   swap-in of a trained NLP model / LLM extractor) to generalize to
   arbitrary, unseen real-world disaster documents.
3. **Demo prioritization heuristic.** The priority score
   (`app/disaster/priority_scorer.py`) is an explicitly documented,
   transparent demo heuristic — not a scientifically validated
   emergency-management formula.
4. **Demo Mode answers are template-based**, not generative, when no LLM API
   key is configured — appropriate for a no-cost academic demo, but not a
   substitute for a real LLM's fluency when one is available.
5. **Small evaluation set.** `scripts/evaluate.py` uses 5 hand-labeled
   questions, sufficient to demonstrate the evaluation methodology but not
   large enough for statistically powerful conclusions.
6. **Single-tenant, single-scenario demo.** The system currently models one
   disaster scenario at a time; multi-disaster/multi-tenant support would
   require additional data-partitioning work.
7. **Offline sync is simulated.** The offline mode demonstrates the
   store-and-forward pattern using local SQLite storage and a manual "Sync"
   action; a production deployment would need a real device-to-server sync
   protocol with conflict resolution.

## Future Scope

- Swap rule-based extraction for a trained NER/relation-extraction model or
  an LLM-based extractor (`extract_relations_llm` hook already exists) for
  broader generalization to real-world documents.
- Add authentication/authorization and audit logging for a multi-user
  deployment.
- Support multiple concurrent disaster scenarios and historical comparison.
- Integrate real government/agency data feeds (with appropriate
  verification and provenance tracking) instead of synthetic demo data.
- Expand the evaluation set and add human-rated answer-relevance and
  faithfulness scoring alongside the automated metrics.
- Add role-based dashboards for different responder types (shelter staff,
  hospital staff, field coordinators).
- Explore graph embeddings (e.g. node2vec) to complement the current
  rule-based graph traversal with learned relationship-similarity search.
