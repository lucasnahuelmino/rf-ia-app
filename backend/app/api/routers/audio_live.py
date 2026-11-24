from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.audio_service import AudioService

router = APIRouter()
_service = AudioService()


class AudioConfig(BaseModel):
    mode: str = "FM"
    frequency: float = 100e6
    if_bandwidth: float = 12500.0


@router.post("/audio/live/start")
def start_audio(payload: AudioConfig):
    _service.configure(payload.mode, payload.frequency, payload.if_bandwidth)
    _service.start()
    return {"status": "started"}


@router.post("/audio/live/stop")
def stop_audio():
    _service.stop()
    return {"status": "stopped"}


@router.get("/audio/live/chunk")
def audio_chunk(size: int = 1024):
    return {"samples": _service.get_audio_chunk(size)}


@router.post("/audio/live/volume")
def set_volume(volume: float):
    _service.set_volume(volume)
    return {"status": "ok"}


@router.post("/audio/live/mute")
def set_mute(muted: bool):
    _service.set_mute(muted)
    return {"status": "ok"}