from __future__ import annotations

import pytest

from app.database.db import init_db
from app.documents.indexer import build_vector_index
from app.graph.graph_builder import rebuild_full_graph


@pytest.fixture(scope="session", autouse=True)
def bootstrap_demo_environment():
    """Build the graph and vector index once for the whole test session,
    matching what happens on app startup in Demo Mode."""
    init_db()
    rebuild_full_graph()
    build_vector_index()
    yield
