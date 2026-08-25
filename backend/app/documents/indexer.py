"""
Orchestrates parsing + chunking of every document in the documents directory,
then builds/refreshes the hybrid (vector + BM25) retrieval index.
"""
from __future__ import annotations

from pathlib import Path

from app.config import DOCUMENTS_DIR
from app.documents.chunker import chunk_document
from app.documents.parser import parse_document, UnsupportedFileTypeError
from app.retrieval.hybrid_retriever import hybrid_retriever


def build_vector_index(documents_dir: Path | None = None) -> dict:
    documents_dir = documents_dir or DOCUMENTS_DIR
    all_chunks = []
    indexed_documents = []
    errors = []

    for path in sorted(documents_dir.iterdir()):
        if path.suffix.lower() not in (".pdf", ".docx", ".txt", ".md", ".csv"):
            continue
        try:
            parsed = parse_document(path)
            chunks = chunk_document(parsed)
            all_chunks.extend(chunks)
            indexed_documents.append({"document_name": path.name, "chunks": len(chunks)})
        except UnsupportedFileTypeError:
            continue
        except Exception as exc:
            errors.append({"document_name": path.name, "error": str(exc)})

    hybrid_retriever.index(all_chunks)

    return {
        "total_chunks": len(all_chunks),
        "documents_indexed": indexed_documents,
        "errors": errors,
        "vector_backend": type(hybrid_retriever.bm25).__name__,
    }
