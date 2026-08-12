import threading
import time

from app.devices.bb60c.adapter import BB60CAdapter
from app.devices.bb60c.models import SweepConfiguration

from .state import spectrum_state


class SpectrumWorker:

    def __init__(self):

        self._thread = None

        self._running = False

    def start(self):

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self._thread.start()

    def stop(self):

        self._running = False

    def _run(self):

        device = BB60CAdapter()

        try:

            device.connect()

            config = SweepConfiguration(
                center_frequency_hz=124.650e6,
                span_hz=5e6,
                rbw_hz=10e3,
                vbw_hz=10e3,
            )

            device.configure_sweep(config)

            device.start_sweep()

            while self._running:

                trace = device.get_trace()

                with spectrum_state.lock:

                    spectrum_state.trace = (
                        trace.trace_max.tolist()
                    )

                    spectrum_state.trace_length = (
                        trace.info.trace_length
                    )

                    spectrum_state.bin_size_hz = (
                        trace.info.bin_size_hz
                    )

                    spectrum_state.start_frequency_hz = (
                        trace.info.start_frequency_hz
                    )

                time.sleep(0.05)

        finally:

            device.disconnect()