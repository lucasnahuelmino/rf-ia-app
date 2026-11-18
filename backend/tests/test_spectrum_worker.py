import numpy as np

from app.devices.bb60c.interfaces import DeviceInfo
from app.devices.bb60c.models import TraceData, TraceInfo
from app.rf.state import spectrum_state
from app.rf.spectrum_worker import SpectrumWorker
from app.services.device_manager import DeviceManager


class FakeAdapter:
    def connect(self):
        pass

    def disconnect(self):
        pass

    def configure_sweep(self, config):
        pass

    def start_sweep(self):
        pass

    def get_trace(self):
        trace = np.array([1.0, 2.0, 3.0], dtype=float)
        return TraceData(
            trace_min=trace - 1,
            trace_max=trace,
            info=TraceInfo(
                trace_length=3,
                bin_size_hz=1000.0,
                start_frequency_hz=100e6,
            ),
        )

    def get_device_info(self):
        return DeviceInfo(2, 1, 1)


def test_worker_single_sweep_updates_state():
    manager = DeviceManager(FakeAdapter)
    worker = SpectrumWorker(manager)

    worker.single_sweep()

    with spectrum_state.lock:
        snapshot = spectrum_state.snapshot

    assert snapshot.trace == [1.0, 2.0, 3.0]
    assert snapshot.trace_min == [0.0, 1.0, 2.0]
    assert snapshot.trace_max == [1.0, 2.0, 3.0]
    assert snapshot.trace_length == 3
    assert snapshot.bin_size_hz == 1000.0
    assert snapshot.start_frequency_hz == 100e6
    assert snapshot.stop_frequency_hz == 100003000.0