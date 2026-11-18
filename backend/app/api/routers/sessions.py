from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.session_service import SessionService

router = APIRouter()
_service = SessionService()


class SessionCreate(BaseModel):
    name: str
    config: dict | None = None
    notes: str = ""


@router.post("/sessions")
def create_session(payload: SessionCreate):
    sid = _service.create_session(payload.name, payload.config, payload.notes)
    return {"id": sid}


@router.get("/sessions")
def list_sessions():
    return {"items": _service.list_sessions()}


@router.get("/sessions/{session_id}")
def get_session(session_id: int):
    item = _service.get_session(session_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.get("/sessions/{session_id}/captures")
def list_captures(session_id: int):
    return {"items": _service.list_captures(session_id)}


@router.get("/sessions/{session_id}/events")
def list_events(session_id: int):
    return {"items": _service.list_events(session_id)}