from __future__ import annotations

import threading
from typing import Optional


class SpectrumConfig:
    """Thread-safe runtime configuration for the spectrum analyzer."""

    def __init__(self) -> None:
        self.lock = threading.Lock()

        self.version = 1

        # Frequency
        self.center_frequency_hz = 124.650e6
        self.span_hz = 5e6
        self.start_frequency_hz: Optional[float] = None
        self.stop_frequency_hz: Optional[float] = None

        # Coupling
        self.rbw_hz = 10e3
        self.vbw_hz = 10e3
        self.sweep_time_s = 0.0

        # Level / gain
        self.reference_level_dbm = 0.0
        self.attenuation = -1
        self.gain = -1
        self.auto_attenuation = True
        self.auto_gain = True

        # Acquisition
        self.detector = 1  # BB_AVERAGE
        self.rbw_shape = 0  # BB_RBW_SHAPE_NUTTALL
        self.spur_reject = 0  # BB_NO_SPUR_REJECT


spectrum_config = SpectrumConfig()