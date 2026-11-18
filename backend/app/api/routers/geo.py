from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.geo_service import GeoMeasurementService

router = APIRouter()
_service = GeoMeasurementService()


class GeoRecord(BaseModel):
    timestamp: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    altitude: float | None = None
    gps_valid: bool = False
    gps_source: str | None = None
    receiver_serial: int | None = None
    antenna_chain_id: int | None = None
    frequency_hz: float | None = None
    level_dbm: float | None = None
    noise_floor_dbm: float | None = None
    session_id: int | None = None
    mission_id: int | None = None


@router.post("/geo/record")
def record_geo(payload: GeoRecord):
    mid = _service.record(payload.dict())
    return {"id": mid}


@router.get("/geo/list")
def list_geo(mission_id: int | None = None, limit: int = 500):
    return {"items": _service.list(mission_id, limit)}