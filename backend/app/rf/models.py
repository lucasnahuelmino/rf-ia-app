from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class SpectrumSnapshot:
    timestamp: float = 0.0

    center_frequency_hz: float = 0.0
    span_hz: float = 0.0

    start_frequency_hz: float = 0.0
    stop_frequency_hz: float = 0.0

    bin_size_hz: float = 0.0
    trace_length: int = 0

    trace: Optional[List[float]] = None
    trace_min: Optional[List[float]] = None
    trace_max: Optional[List[float]] = None

    config_version: int = 0