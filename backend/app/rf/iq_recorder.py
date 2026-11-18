from __future__ import annotations

import json
import os
import struct
import time
from dataclasses import asdict, dataclass
from typing import Optional

import numpy as np


@dataclass
class IQMetadata:
    filename: str
    center_frequency_hz: float
    sample_rate_hz: float
    bandwidth_hz: float
    gain: int
    attenuation: int
    start_time: float = 0.0
    end_time: Optional[float] = None
    samples: int = 0
    dtype: str = "float32_interleaved"
    block_size: int = 4096


class IQRecorder:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self._file = None
        self._meta_path = None
        self._metadata: Optional[IQMetadata] = None
        self._samples = 0

    @property
    def is_recording(self) -> bool:
        return self._file is not None

    def start(self, metadata: IQMetadata) -> str:
        if self.is_recording:
            raise RuntimeError("Recording already in progress.")

        base_name = os.path.splitext(metadata.filename)[0]
        iq_path = os.path.join(self.base_dir, base_name + ".iq")
        self._meta_path = os.path.join(self.base_dir, base_name + ".json")

        self._file = open(iq_path, "wb")
        self._metadata = metadata
        self._samples = 0
        metadata.start_time = time.time()
        metadata.samples = 0

        with open(self._meta_path, "w", encoding="utf-8") as f:
            json.dump(asdict(metadata), f, indent=2)

        return iq_path

    def write(self, iq: np.ndarray) -> None:
        if not self.is_recording or self._file is None:
            raise RuntimeError("No recording in progress.")

        iq = np.asarray(iq)
        if iq.dtype != np.complex64 and iq.dtype != np.complex128:
            iq = iq.astype(np.complex64)

        interleaved = np.empty(iq.size * 2, dtype=np.float32)
        interleaved[0::2] = iq.real.astype(np.float32)
        interleaved[1::2] = iq.imag.astype(np.float32)

        self._file.write(interleaved.tobytes())
        self._samples += iq.size

        if self._metadata is not None:
            self._metadata.samples = self._samples
            self._metadata.end_time = time.time()
            with open(self._meta_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self._metadata), f, indent=2)

    def stop(self) -> Optional[IQMetadata]:
        if not self.is_recording:
            return None

        if self._file is not None:
            self._file.flush()
            os.fsync(self._file.fileno())
            self._file.close()
            self._file = None

        meta = self._metadata
        if meta is not None:
            meta.end_time = time.time()
            meta.samples = self._samples
            if self._meta_path:
                with open(self._meta_path, "w", encoding="utf-8") as f:
                    json.dump(asdict(meta), f, indent=2)

        self._metadata = None
        return meta