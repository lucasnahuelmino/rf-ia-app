from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.gps_service import GPSService

router = APIRouter()
_service = GPSService()


class ConnectSerialRequest(BaseModel):
    port: str
    baudrate: int = 9600


@router.get("/gps/ports")
def list_ports():
    return {"items": _service.list_ports()}


@router.post("/gps/connect/simulated")
def connect_simulated():
    _service.connect_simulated()
    return _service.status()


@router.post("/gps/connect/serial")
def connect_serial(payload: ConnectSerialRequest):
    _service.connect_serial(payload.port, payload.baudrate)
    return _service.status()


@router.post("/gps/disconnect")
def disconnect():
    _service.disconnect()
    return _service.status()


@router.get("/gps/status")
def status():
    return _service.status()


@router.post("/gps/read")
def read_position():
    pos = _service.read_position()
    return {"position": pos.__dict__ if pos else None}


@router.get("/gps/history")
def history(limit: int = 100):
    return {"items": _service.history(limit)}