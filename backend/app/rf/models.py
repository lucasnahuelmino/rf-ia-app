from dataclasses import dataclass
from typing import Optional


@dataclass
class SpectrumSnapshot:
    timestamp: float

    center_frequency_hz: float
    span_hz: float

    start_frequency_hz: float
    stop_frequency_hz: float

    bin_size_hz: float
    trace_length: int

    trace: Optional[list]