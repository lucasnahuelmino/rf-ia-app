from dataclasses import dataclass

import numpy as np


@dataclass
class SweepConfiguration:
    center_frequency_hz: float
    span_hz: float
    rbw_hz: float
    vbw_hz: float
    reference_level_dbm: float = 0.0


@dataclass
class TraceInfo:
    trace_length: int
    bin_size_hz: float
    start_frequency_hz: float


@dataclass
class TraceData:
    trace_min: np.ndarray
    trace_max: np.ndarray
    info: TraceInfo