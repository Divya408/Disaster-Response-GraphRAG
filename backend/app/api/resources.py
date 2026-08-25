from __future__ import annotations

from fastapi import APIRouter

from app.disaster.resource_coordinator import get_resource_status

router = APIRouter(prefix="/api/resources", tags=["resources"])


@router.get("")
def list_resources():
    return {"resources": get_resource_status()}
