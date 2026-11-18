from __future__ import annotations

import os
import wave
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class WAVMetadata:
    filename: str
    sample_rate: int
    channels: int = 1
    bits: int = 16


class WAVRecorder:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self._wav: Optional[wave.Wave_write] = None
        self._path: Optional[str] = None
        self._metadata: Optional[WAVMetadata] = None

    @property
    def is_recording(self) -> bool:
        return self._wav is not None

    def start(self, metadata: WAVMetadata) -> str:
        if self.is_recording:
            raise RuntimeError("Recording already in progress.")

        path = os.path.join(self.base_dir, metadata.filename)
        self._path = path
        self._metadata = metadata

        self._wav = wave.open(path, "wb")
        self._wav.setnchannels(metadata.channels)
        self._wav.setsampwidth(metadata.bits // 8)
        self._wav.setframerate(metadata.sample_rate)

        return path

    def write(self, audio: np.ndarray) -> None:
        if not self.is_recording or self._wav is None:
            raise RuntimeError("No recording in progress.")

        audio = np.asarray(audio)
        if audio.dtype != np.int16:
            audio = np.clip(audio, -1.0, 1.0)
            audio = (audio * 32767).astype(np.int16)

        self._wav.writeframes(audio.tobytes())

    def stop(self) -> Optional[str]:
        if not self.is_recording:
            return None
        if self._wav is not None:
            self._wav.close()
            self._wav = None
        path = self._path
        self._path = None
        self._metadata = None
        return path