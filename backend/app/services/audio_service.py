from __future__ import annotations

import os
import wave
import threading
import time
from typing import Any, Dict, List, Optional

import numpy as np

from app.devices.bb60c.sdk import bb_api


class AudioService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._handle = None
        self._mode = "FM"
        self._frequency = 100e6
        self._running = False
        self._thread = None
        self._audio_buffer: List[float] = []
        self._max_buffer = 48000 * 5
        self._volume = 1.0
        self._muted = False

    def configure(self, mode: str, frequency: float, if_bandwidth: float = 12500.0) -> None:
        self._mode = mode
        self._frequency = frequency

    def start(self, handle: int | None = None) -> None:
        self._handle = handle
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None

    def _loop(self) -> None:
        while self._running:
            # Simulated audio tone for now (real SDK integration requires hardware)
            t = time.time()
            samples = 0.3 * np.sin(2 * np.pi * 440 * np.arange(1024) / 48000).tolist()
            with self._lock:
                self._audio_buffer.extend(samples)
                if len(self._audio_buffer) > self._max_buffer:
                    self._audio_buffer = self._audio_buffer[-self._max_buffer:]
            time.sleep(1024 / 48000)

    def get_audio_chunk(self, size: int = 1024) -> List[float]:
        with self._lock:
            if not self._audio_buffer:
                return []
            chunk = self._audio_buffer[:size]
            self._audio_buffer = self._audio_buffer[size:]
            if self._muted:
                return [0.0] * len(chunk)
            return [s * self._volume for s in chunk]

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))

    def set_mute(self, muted: bool) -> None:
        self._muted = muted

    def record_wav(self, path: str, duration: float = 5.0) -> str:
        import wave, struct
        frames = int(48000 * duration)
        data = []
        # generate tone
        for i in range(frames):
            data.append(int(32767 * 0.3 * __import__("math").sin(2 * __import__("math").pi * 440 * i / 48000)))
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(48000)
            w.writeframes(struct.pack("<" + "h" * len(data), *data))
        return path

    @property
    def is_running(self) -> bool:
        return self._running