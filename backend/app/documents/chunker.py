"""
Chunking utilities: turn a ParsedDocument into overlapping text chunks with
metadata, suitable for embedding / BM25 indexing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from uuid import uuid4

from app.documents.parser import ParsedDocument


@dataclass
class Chunk:
    chunk_id: str
    document_name: str
    section_label: str
    text: str
    metadata: dict = field(default_factory=dict)


def _split_into_sentences(text: str) -> list[str]:
    # Simple, dependency-free sentence splitter.
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_document(
    parsed: ParsedDocument,
    max_chars: int = 500,
    overlap_sentences: int = 1,
) -> list[Chunk]:
    """
    Chunk a parsed document section-by-section (page/section-aware), further
    splitting long sections into ~max_chars pieces with a small sentence
    overlap so context isn't lost at chunk boundaries.
    """
    chunks: list[Chunk] = []

    sections = parsed.sections or [type("S", (), {"label": "Full Document", "text": parsed.full_text})()]

    for section in sections:
        sentences = _split_into_sentences(section.text)
        if not sentences:
            continue

        current: list[str] = []
        current_len = 0
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            current.append(sentence)
            current_len += len(sentence)
            if current_len >= max_chars or i == len(sentences) - 1:
                chunk_text = " ".join(current)
                chunks.append(
                    Chunk(
                        chunk_id=str(uuid4()),
                        document_name=parsed.document_name,
                        section_label=section.label,
                        text=chunk_text,
                        metadata={
                            "document_name": parsed.document_name,
                            "file_type": parsed.file_type,
                            "section": section.label,
                        },
                    )
                )
                # keep the last `overlap_sentences` for context continuity
                current = current[-overlap_sentences:] if overlap_sentences else []
                current_len = sum(len(s) for s in current)
            i += 1

    return chunks
