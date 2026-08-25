"""
SQLite application database.

Stores operational records: disaster events, locations, shelters, resources,
hospitals, agencies, assessments, query logs, generated reports, and offline
sync records. Neo4j (or its in-memory fallback) stores graph relationships;
ChromaDB (or its TF-IDF fallback) stores document embeddings; this module is
the relational store for everything else.
"""
from __future__ import annotations

import sqlite3
import time
import uuid
from contextlib import contextmanager

from app.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS query_log (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    intent TEXT,
    is_demo_mode INTEGER,
    confidence REAL,
    created_at REAL
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT,
    uploaded_at REAL,
    indexed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    area TEXT,
    file_path TEXT,
    created_at REAL
);

CREATE TABLE IF NOT EXISTS offline_records (
    id TEXT PRIMARY KEY,
    record_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT DEFAULT 'Pending Sync',
    created_at REAL,
    synced_at REAL
);
"""


@contextmanager
def get_connection():
    conn = sqlite3.connect(settings.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def log_query(query: str, intent: str, is_demo_mode: bool, confidence: float) -> str:
    record_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO query_log (id, query, intent, is_demo_mode, confidence, created_at) VALUES (?,?,?,?,?,?)",
            (record_id, query, intent, int(is_demo_mode), confidence, time.time()),
        )
    return record_id


def record_document(filename: str, file_type: str) -> str:
    record_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO documents (id, filename, file_type, uploaded_at, indexed) VALUES (?,?,?,?,0)",
            (record_id, filename, file_type, time.time()),
        )
    return record_id


def mark_documents_indexed():
    with get_connection() as conn:
        conn.execute("UPDATE documents SET indexed = 1")


def list_documents() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM documents ORDER BY uploaded_at DESC").fetchall()
        return [dict(r) for r in rows]


def record_report(area: str, file_path: str) -> str:
    record_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO reports (id, area, file_path, created_at) VALUES (?,?,?,?)",
            (record_id, area, file_path, time.time()),
        )
    return record_id


def add_offline_record(record_type: str, payload: str) -> str:
    record_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO offline_records (id, record_type, payload, status, created_at) VALUES (?,?,?, 'Pending Sync', ?)",
            (record_id, record_type, payload, time.time()),
        )
    return record_id


def pending_sync_count() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) as c FROM offline_records WHERE status = 'Pending Sync'").fetchone()
        return row["c"]


def sync_all_pending() -> int:
    with get_connection() as conn:
        cur = conn.execute("SELECT id FROM offline_records WHERE status = 'Pending Sync'")
        ids = [r["id"] for r in cur.fetchall()]
        for rid in ids:
            conn.execute(
                "UPDATE offline_records SET status = 'Synced', synced_at = ? WHERE id = ?",
                (time.time(), rid),
            )
    return len(ids)


def list_offline_records(status: str | None = None) -> list[dict]:
    with get_connection() as conn:
        if status:
            rows = conn.execute("SELECT * FROM offline_records WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM offline_records ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
