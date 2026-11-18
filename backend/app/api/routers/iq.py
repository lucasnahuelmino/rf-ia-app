from __future__ import annotations

import base64
import json
import os

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.rf.iq_recorder import IQMetadata, IQRecorder
from app.rf.iq_player import IQPlayer
from app.services.recording_service import RecordingService, data_dir

router = APIRouter()

_recorder = IQRecorder(data_dir())
_player = IQPlayer(data_dir())
_service = RecordingService()


class IQRecordStart(BaseModel):
    filename: str
    center_frequency_hz: float = 100e6
    sample_rate_hz: float = 1e6
    bandwidth_hz: float = 200e3
    gain: int = -1
    attenuation: int = -1


class IQChunk(BaseModel):
    iq: list[float]


@router.post("/iq/record/start")
def iq_record_start(payload: IQRecordStart):
    if _recorder.is_recording:
        raise HTTPException(status_code=409, detail="Already recording")
    meta = IQMetadata(
        filename=payload.filename,
        center_frequency_hz=payload.center_frequency_hz,
        sample_rate_hz=payload.sample_rate_hz,
        bandwidth_hz=payload.bandwidth_hz,
        gain=payload.gain,
        attenuation=payload.attenuation,
    )
    path = _recorder.start(meta)
    return {"status": "recording", "path": path}


@router.post("/iq/record/chunk")
def iq_record_chunk(payload: IQChunk):
    if not _recorder.is_recording:
        raise HTTPException(status_code=409, detail="No recording in progress")
    arr = np.asarray(payload.iq, dtype=np.float32)
    if arr.size % 2 != 0:
        raise HTTPException(status_code=400, detail="IQ data must be interleaved I/Q pairs")
    iq = arr[0::2] + 1j * arr[1::2]
    _recorder.write(iq.astype(np.complex64))
    return {"status": "ok", "samples": int(iq.size)}


@router.post("/iq/record/stop")
def iq_record_stop():
    meta = _recorder.stop()
    if meta is None:
        raise HTTPException(status_code=409, detail="No recording in progress")
    return {"status": "stopped", "metadata": meta.__dict__}


@router.post("/iq/record/demo")
def iq_record_demo(seconds: float = 1.0, sample_rate: float = 1e6):
    if _recorder.is_recording:
        raise HTTPException(status_code=409, detail="Already recording")
    meta = IQMetadata(
        filename="demo.iq",
        center_frequency_hz=100e6,
        sample_rate_hz=sample_rate,
        bandwidth_hz=200e3,
        gain=-1,
        attenuation=-1,
    )
    _recorder.start(meta)
    t = np.arange(int(seconds * sample_rate)) / sample_rate
    iq = np.exp(1j * 2 * np.pi * 1000 * t).astype(np.complex64)
    _recorder.write(iq)
    result_meta = _recorder.stop()
    return {"status": "ok", "metadata": result_meta.__dict__ if result_meta else None}


@router.post("/iq/play/open")
def iq_play_open(filename: str):
    try:
        meta = _player.open(filename)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"status": "opened", "metadata": meta}


@router.post("/iq/play/start")
def iq_play_start():
    _player.play()
    return {"status": "playing"}


@router.post("/iq/play/pause")
def iq_play_pause():
    _player.pause()
    return {"status": "paused"}


@router.post("/iq/play/stop")
def iq_play_stop():
    _player.stop()
    return {"status": "stopped"}


@router.get("/iq/play/chunk")
def iq_play_chunk(size: int = 4096):
    chunk = _player.read_chunk(size)
    if chunk is None:
        return {"status": "empty", "iq": []}
    interleaved = []
    for c in chunk:
        interleaved.append(float(c.real))
        interleaved.append(float(c.imag))
    return {
        "status": "ok",
        "iq": interleaved,
        "position": _player.state().position,
        "total": _player.state().total,
        "sample_rate": _player.sample_rate,
    }


@router.get("/iq/play/state")
def iq_play_state():
    st = _player.state()
    return {
        "filename": st.filename,
        "position": st.position,
        "total": st.total,
        "is_playing": st.is_playing,
        "is_paused": st.is_paused,
        "sample_rate": _player.sample_rate,
        "metadata": _player.metadata,
    }