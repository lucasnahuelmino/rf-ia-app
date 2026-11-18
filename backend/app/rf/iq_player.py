from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Iterator, Optional

import numpy as np


@dataclass
class IQPlaybackState:
    filename: str
    position: int
    total: int
    is_playing: bool
    is_paused: bool


class IQPlayer:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        self._meta = None
        self._data = None
        self._position = 0
        self._playing = False
        self._paused = False

    def open(self, filename: str) -> dict:
        self.close()
        base_name = os.path.splitext(filename)[0]
        meta_path = os.path.join(self.base_dir, base_name + ".json")
        iq_path = os.path.join(self.base_dir, base_name + ".iq")

        with open(meta_path, "r", encoding="utf-8") as f:
            self._meta = json.load(f)

        self._data = np.fromfile(iq_path, dtype=np.float32)
        # interleaved -> complex
        self._complex = (
            self._data[0::2].astype(np.float32)
            + 1j * self._data[1::2].astype(np.float32)
        )
        self._position = 0
        self._playing = False
        self._paused = False
        return self._meta

    def play(self) -> None:
        if self._complex is None:
            raise RuntimeError("No file opened.")
        self._playing = True
        self._paused = False

    def pause(self) -> None:
        self._paused = True

    def stop(self) -> None:
        self._playing = False
        self._paused = False
        self._position = 0

    def close(self) -> None:
        self._playing = False
        self._paused = False
        self._position = 0
        self._complex = None
        self._meta = None

    def read_chunk(self, size: int = 4096) -> Optional[np.ndarray]:
        if self._complex is None or not self._playing or self._paused:
            return None
        if self._position >= len(self._complex):
            self._playing = False
            return None
        chunk = self._complex[self._position:self._position + size]
        self._position += len(chunk)
        return chunk

    def seek(self, position: int) -> None:
        if self._complex is None:
            return
        self._position = max(0, min(position, len(self._complex)))

    def state(self) -> IQPlaybackState:
        total = len(self._complex) if self._complex is not None else 0
        filename = self._meta.get("filename", "") if self._meta else ""
        return IQPlaybackState(
            filename=filename,
            position=self._position,
            total=total,
            is_playing=self._playing,
            is_paused=self._paused,
        )

    @property
    def metadata(self):
        return self._meta

    @property
    def sample_rate(self) -> float:
        return float(self._meta.get("sample_rate_hz", 48000.0)) if self._meta else 48000.0