from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import OfflineRecordRequest
from app.disaster.offline_sync import get_sync_status, submit_offline_record, sync_pending_records

router = APIRouter(prefix="/api/offline", tags=["offline"])


@router.post("/records")
def create_offline_record(req: OfflineRecordRequest):
    return submit_offline_record(req.record_type, req.payload)


@router.get("/status")
def sync_status():
    return get_sync_status()


@router.post("/sync")
def sync():
    return sync_pending_records()
