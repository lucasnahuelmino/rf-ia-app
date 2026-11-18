from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class SweepConfiguration:
    """Full sweep configuration accepted by the BB60C.

    Frequency can be specified either as center/span or as start/stop. When both
    are provided, start/stop takes precedence and center/span are derived.
    """

    center_frequency_hz: Optional[float] = None
    span_hz: Optional[float] = None
    start_frequency_hz: Optional[float] = None
    stop_frequency_hz: Optional[float] = None

    rbw_hz: float = 10000.0
    vbw_hz: float = 10000.0

    reference_level_dbm: float = 0.0

    # -1 means automatic for both attenuation and gain (BB_AUTO_*).
    attenuation: int = -1
    gain: int = -1
    auto_attenuation: bool = True
    auto_gain: bool = True

    detector: int = 1  # BB_AVERAGE
    rbw_shape: int = 0  # BB_RBW_SHAPE_NUTTALL
    spur_reject: int = 0  # BB_NO_SPUR_REJECT

    sweep_time_s: float = 0.0

    def normalized_center_span(self) -> tuple[float, float, float, float]:
        """Return (center, span, start, stop) in Hz."""
        if (
            self.start_frequency_hz is not None
            and self.stop_frequency_hz is not None
        ):
            start = float(self.start_frequency_hz)
            stop = float(self.stop_frequency_hz)
            center = (start + stop) / 2.0
            span = stop - start
        else:
            center = float(self.center_frequency_hz if self.center_frequency_hz is not None else 0.0)
            span = float(self.span_hz if self.span_hz is not None else 0.0)
            start = center - span / 2.0
            stop = center + span / 2.0

        if span <= 0:
            raise ValueError("Span must be greater than zero.")

        return center, span, start, stop


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