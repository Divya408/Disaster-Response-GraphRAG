"""
Offline / low-connectivity support.

Responders (volunteers, shelters, hospitals, police, fire & rescue) can
record assessments locally even without internet connectivity. Records are
stored with status "Pending Sync" and can be synchronized later via
`sync_pending_records()`, simulating the store-and-forward pattern described
in the project brief. This directly answers the "what if the victim's phone
has no battery?" design question: data entry is responder-side, not
victim-side, so a dead phone is never a single point of failure.
"""
from __future__ import annotations

from app.database import db


def submit_offline_record(record_type: str, payload: dict) -> dict:
    import json

    record_id = db.add_offline_record(record_type, json.dumps(payload))
    return {
        "id": record_id,
        "status": "Pending Sync",
        "pending_sync_count": db.pending_sync_count(),
    }


def get_sync_status() -> dict:
    return {
        "pending_sync_count": db.pending_sync_count(),
        "records": db.list_offline_records(status="Pending Sync"),
    }


def sync_pending_records() -> dict:
    synced_count = db.sync_all_pending()
    return {
        "synced_count": synced_count,
        "pending_sync_count": db.pending_sync_count(),
    }
