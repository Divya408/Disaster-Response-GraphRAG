#!/usr/bin/env python3
"""
Build (or rebuild) the knowledge graph from structured demo data and every
document currently in backend/data/documents/.

Usage:
    python scripts/build_graph.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.graph.graph_builder import rebuild_full_graph


def main():
    summary = rebuild_full_graph()
    print(f"Graph backend: {summary['backend']}")
    print(f"Nodes: {summary['node_count']}  Edges: {summary['edge_count']}")
    print("\nDocuments ingested:")
    for doc in summary["documents_ingested"]:
        if "error" in doc:
            print(f"  ! {doc['document_name']}: ERROR - {doc['error']}")
        else:
            print(f"  - {doc['document_name']}: {doc['edges_added']} relationships added")


if __name__ == "__main__":
    main()
