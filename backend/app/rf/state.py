from __future__ import annotations

from threading import Lock

from app.rf.models import SpectrumSnapshot


class SpectrumState:
    def __init__(self):
        self.lock = Lock()
        self.snapshot = SpectrumSnapshot()


spectrum_state = SpectrumState()