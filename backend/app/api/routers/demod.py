from __future__ import annotations

import os

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.audio.wav_recorder import WAVMetadata, WAVRecorder
from app.dsp.demod import demodulate
from app.rf.iq_player import IQPlayer
from app.services.recording_service import data_dir

router = APIRouter()

_player = IQPlayer(data_dir())


class DemodRequest(BaseModel):
    mode: str = "WFM"
    filename: str | None = None
    sample_rate: float = 1e6
    audio_rate: float = 48000.0
    duration_seconds: float = 1.0


@router.post("/demod/synthetic")
def demod_synthetic(payload: DemodRequest):
    # Generate a synthetic FM signal for validation.
    sr = payload.sample_rate
    t = np.arange(int(payload.duration_seconds * sr)) / sr
    # FM with 1 kHz tone modulation
    mod = np.sin(2 * np.pi * 1000 * t)
    phase = 2 * np.pi * (payload.sample_rate * 0 + 5000 * np.cumsum(mod) / sr)
    iq = np.exp(1j * phase).astype(np.complex64)

    audio = demodulate(payload.mode, iq, sr, payload.audio_rate)

    recorder = WAVRecorder(data_dir())
    meta = WAVMetadata(
        filename=f"demod_{payload.mode.lower()}.wav",
        sample_rate=int(payload.audio_rate),
    )
    path = recorder.start(meta)
    recorder.write(audio)
    recorder.stop()

    return {
        "status": "ok",
        "mode": payload.mode,
        "audio_samples": int(audio.size),
        "wav_path": path,
        "wav_filename": meta.filename,
    }


@router.post("/demod/file")
def demod_file(payload: DemodRequest):
    if not payload.filename:
        raise HTTPException(status_code=400, detail="filename is required")

    try:
        _player.open(payload.filename)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    chunk = _player.read_chunk(1 << 20)
    if chunk is None:
        raise HTTPException(status_code=400, detail="No IQ data")

    # Read remaining
    chunks = [chunk]
    while True:
        c = _player.read_chunk(1 << 20)
        if c is None or c.size == 0:
            break
        chunks.append(c)
    iq = np.concatenate(chunks)

    sr = payload.sample_rate or _player.sample_rate
    audio = demodulate(payload.mode, iq, sr, payload.audio_rate)

    recorder = WAVRecorder(data_dir())
    meta = WAVMetadata(
        filename=f"demod_{payload.mode.lower()}_{os.path.splitext(payload.filename)[0]}.wav",
        sample_rate=int(payload.audio_rate),
    )
    path = recorder.start(meta)
    recorder.write(audio)
    recorder.stop()

    return {
        "status": "ok",
        "mode": payload.mode,
        "audio_samples": int(audio.size),
        "wav_path": path,
        "wav_filename": meta.filename,
    }