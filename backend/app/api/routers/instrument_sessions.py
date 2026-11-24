from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.instrument_session_service import InstrumentSessionService

router = APIRouter()
_service = InstrumentSessionService()


class SessionCreate(BaseModel):
    name: str
    receiver_serial: int | None = None
    session_type: str = "sweep"
    config: dict | None = None


@router.get("/instrument-sessions")
def list_sessions(receiver_serial: int | None = None):
    return {"items": _service.list(receiver_serial)}


@router.post("/instrument-sessions")
def create_session(payload: SessionCreate):
    sid = _service.create(payload.name, payload.receiver_serial, payload.session_type, payload.config)
    return {"id": sid}


@router.get("/instrument-sessions/{session_id}")
def get_session(session_id: int):
    item = _service.get(session_id)
    if not item:
        return {"error": "not found"}
    return item


@router.post("/instrument-sessions/{session_id}/status")
def set_status(session_id: int, status: str):
    _service.update_status(session_id, status)
    return {"status": "ok"}