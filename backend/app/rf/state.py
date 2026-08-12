from threading import Lock

from app.rf.models import SpectrumSnapshot


class SpectrumState:

    def __init__(self):

        self.lock = Lock()

        self.snapshot = SpectrumSnapshot(
            timestamp=0.0,
            center_frequency_hz=0.0,
            span_hz=0.0,
            start_frequency_hz=0.0,
            stop_frequency_hz=0.0,
            bin_size_hz=0.0,
            trace_length=0,
            trace=None,
        )


spectrum_state = SpectrumState()