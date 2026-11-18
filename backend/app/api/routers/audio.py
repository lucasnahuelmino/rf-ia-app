from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.audio.wav_recorder import WAVMetadata, WAVRecorder
from app.services.recording_service import RecordingService, data_dir

router = APIRouter()

_recorder = WAVRecorder(data_dir())
_service = RecordingService()


class AudioRecordStart(BaseModel):
    filename: str = "audio.wav"
    sample_rate: int = 48000
    bits: int = 16


@router.post("/audio/record/start")
def audio_record_start(payload: AudioRecordStart):
    if _recorder.is_recording:
        raise HTTPException(status_code=409, detail="Already recording")
    meta = WAVMetadata(
        filename=payload.filename,
        sample_rate=payload.sample_rate,
        bits=payload.bits,
    )
    path = _recorder.start(meta)
    return {"status": "recording", "path": path}


@router.post("/audio/record/chunk")
def audio_record_chunk(samples: list[float]):
    if not _recorder.is_recording:
        raise HTTPException(status_code=409, detail="No recording in progress")
    import numpy as np

    _recorder.write(np.asarray(samples, dtype=np.float32))
    return {"status": "ok"}


@router.post("/audio/record/stop")
def audio_record_stop():
    path = _recorder.stop()
    if path is None:
        raise HTTPException(status_code=409, detail="No recording in progress")
    return {"status": "stopped", "path": path}


@router.post("/audio/demo")
def audio_demo():
    import numpy as np

    sr = 48000
    t = np.arange(sr) / sr
    tone = 0.5 * np.sin(2 * np.pi * 440 * t)
    meta = WAVMetadata(filename="audio_demo.wav", sample_rate=sr)
    path = _recorder.start(meta) if not _recorder.is_recording else None
    if path is None:
        # already recording; stop first
        _recorder.stop()
        path = _recorder.start(meta)
    _recorder.write(tone.astype(np.float32))
    _recorder.stop()
    return {"status": "ok", "path": path}