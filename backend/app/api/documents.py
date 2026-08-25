from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import DOCUMENTS_DIR, settings
from app.database import db
from app.documents.indexer import build_vector_index

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _sanitize_filename(name: str) -> str:
    name = Path(name).name  # strip any path components
    safe = "".join(c for c in name if c.isalnum() or c in "._- ")
    return safe or "uploaded_file"


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = _sanitize_filename(file.filename or "uploaded_file")
    suffix = Path(filename).suffix.lower()

    if suffix not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large ({size_mb:.1f} MB > {settings.MAX_UPLOAD_SIZE_MB} MB limit)")

    dest = DOCUMENTS_DIR / filename
    dest.write_bytes(contents)
    db.record_document(filename, suffix.lstrip("."))

    return {"filename": filename, "size_bytes": len(contents), "status": "uploaded"}


@router.post("/index")
def index_documents():
    summary = build_vector_index()
    db.mark_documents_indexed()
    return summary


@router.get("")
def list_documents():
    files = []
    for path in sorted(DOCUMENTS_DIR.iterdir()):
        if path.suffix.lower() in settings.ALLOWED_UPLOAD_EXTENSIONS:
            files.append({"filename": path.name, "size_bytes": path.stat().st_size})
    return {"documents": files, "records": db.list_documents()}


@router.delete("/{filename}")
def delete_document(filename: str):
    filename = _sanitize_filename(filename)
    path = DOCUMENTS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    path.unlink()
    return {"filename": filename, "status": "deleted"}
