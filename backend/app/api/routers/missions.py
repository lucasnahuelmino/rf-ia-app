from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.mission_service import MissionService

router = APIRouter()
_service = MissionService()


class MissionCreate(BaseModel):
    name: str
    objective: str = ""
    receiver_serial: int | None = None
    antenna_chain_id: int | None = None
    profile: dict | None = None


@router.get("/missions")
def list_missions():
    return {"items": _service.list()}


@router.post("/missions")
def create_mission(payload: MissionCreate):
    mid = _service.create(payload.name, payload.objective, payload.receiver_serial, payload.antenna_chain_id, payload.profile)
    return {"id": mid}


@router.post("/missions/{mission_id}/execute")
def execute_mission(mission_id: int):
    return _service.execute(mission_id)


@router.post("/missions/{mission_id}/pause")
def pause_mission(mission_id: int):
    return _service.pause(mission_id)


@router.post("/missions/{mission_id}/resume")
def resume_mission(mission_id: int):
    return _service.resume(mission_id)


@router.post("/missions/{mission_id}/cancel")
def cancel_mission(mission_id: int):
    return _service.cancel(mission_id)


@router.get("/missions/recover")
def recover_missions():
    return {"items": _service.recover_interrupted()}