#!/usr/bin/env python3
"""
Build (or rebuild) the hybrid vector + BM25 retrieval index from every
document in backend/data/documents/.

Usage:
    python scripts/build_vector_index.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.documents.indexer import build_vector_index


def main():
    summary = build_vector_index()
    print(f"Total chunks indexed: {summary['total_chunks']}")
    print("\nDocuments indexed:")
    for doc in summary["documents_indexed"]:
        print(f"  - {doc['document_name']}: {doc['chunks']} chunks")
    if summary["errors"]:
        print("\nErrors:")
        for err in summary["errors"]:
            print(f"  ! {err['document_name']}: {err['error']}")


if __name__ == "__main__":
    main()
