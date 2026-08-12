import threading
import time

from app.devices.bb60c.adapter import BB60CAdapter
from app.devices.bb60c.models import SweepConfiguration
from app.rf.config import spectrum_config

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
                center_frequency_hz=
                    spectrum_config.center_frequency_hz,

                span_hz=
                    spectrum_config.span_hz,

                rbw_hz=
                    spectrum_config.rbw_hz,

                vbw_hz=
                    spectrum_config.vbw_hz,

                reference_level_dbm=
                    spectrum_config.reference_level_dbm,
            )

            device.configure_sweep(config)

            device.start_sweep()

            while self._running:

                trace = device.get_trace()

                stop_frequency_hz = (
                    trace.info.start_frequency_hz
                    +
                    (
                        trace.info.trace_length
                        * trace.info.bin_size_hz
                    )
                )

                with spectrum_state.lock:

                    spectrum_state.snapshot.timestamp = (
                        time.time()
                    )

                    spectrum_state.snapshot.center_frequency_hz = (
                        config.center_frequency_hz
                    )

                    spectrum_state.snapshot.span_hz = (
                        config.span_hz
                    )

                    spectrum_state.snapshot.start_frequency_hz = (
                        trace.info.start_frequency_hz
                    )

                    spectrum_state.snapshot.stop_frequency_hz = (
                        stop_frequency_hz
                    )

                    spectrum_state.snapshot.bin_size_hz = (
                        trace.info.bin_size_hz
                    )

                    spectrum_state.snapshot.trace_length = (
                        trace.info.trace_length
                    )

                    spectrum_state.snapshot.trace = (
                        trace.trace_max.tolist()
                    )

                time.sleep(0.05)

        finally:

            device.disconnect()