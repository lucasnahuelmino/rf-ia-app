from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.antenna_service import AntennaService

router = APIRouter()
_service = AntennaService()


class AntennaCreate(BaseModel):
    name: str
    components: list[str] = []
    receiver_serial: int | None = None
    losses_db: float = 0.0


@router.get("/antennas")
def list_antennas():
    return {"items": _service.list()}


@router.post("/antennas")
def create_antenna(payload: AntennaCreate):
    aid = _service.create(payload.name, payload.components, payload.receiver_serial, payload.losses_db)
    return {"id": aid}


@router.delete("/antennas/{antenna_id}")
def delete_antenna(antenna_id: int):
    ok = _service.delete(antenna_id)
    return {"status": "deleted" if ok else "not_found"}


@router.put("/antennas/{antenna_id}/topology")
def update_topology(antenna_id: int, topology: dict):
    ok = _service.update_topology(antenna_id, topology)
    return {"status": "updated" if ok else "not_found"}