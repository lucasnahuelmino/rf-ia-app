from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.recording_service import RecordingService

router = APIRouter()

_service = RecordingService()


@router.get("/recordings")
def list_recordings():
    return {"items": _service.list_recordings()}


@router.delete("/recordings/{filename}")
def delete_recording(filename: str):
    ok = _service.delete(filename)
    if not ok:
        raise HTTPException(status_code=404, detail="File not found")
    return {"status": "deleted", "filename": filename}