"""
BM25 keyword retrieval.

Implemented directly with numpy (no dependency on the `rank_bm25` package,
though it is still listed in requirements.txt as an optional accelerated
alternative) so the retrieval layer works in any standard Python + numpy
environment.
"""
from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np

from app.documents.chunker import Chunk

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


class BM25Retriever:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: list[Chunk] = []
        self._doc_tokens: list[list[str]] = []
        self._doc_freqs: Counter = Counter()
        self._avg_doc_len = 0.0
        self._N = 0

    def index(self, chunks: list[Chunk]):
        self.chunks = chunks
        self._doc_tokens = [_tokenize(c.text) for c in chunks]
        self._N = len(chunks)
        self._doc_freqs = Counter()
        for tokens in self._doc_tokens:
            for term in set(tokens):
                self._doc_freqs[term] += 1
        lengths = [len(t) for t in self._doc_tokens] or [0]
        self._avg_doc_len = sum(lengths) / max(1, len(lengths))

    def _idf(self, term: str) -> float:
        df = self._doc_freqs.get(term, 0)
        return math.log(1 + (self._N - df + 0.5) / (df + 0.5))

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        if not self.chunks:
            return []
        query_terms = _tokenize(query)
        scores = np.zeros(self._N)
        for i, tokens in enumerate(self._doc_tokens):
            doc_len = len(tokens) or 1
            term_counts = Counter(tokens)
            score = 0.0
            for term in query_terms:
                if term not in term_counts:
                    continue
                freq = term_counts[term]
                idf = self._idf(term)
                denom = freq + self.k1 * (1 - self.b + self.b * doc_len / self._avg_doc_len)
                score += idf * (freq * (self.k1 + 1)) / denom
            scores[i] = score

        ranked_idx = np.argsort(-scores)[:top_k]
        return [(self.chunks[i], float(scores[i])) for i in ranked_idx if scores[i] > 0]
