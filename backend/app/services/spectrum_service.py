from app.devices.bb60c.adapter import BB60CAdapter
from app.devices.bb60c.models import SweepConfiguration


class SpectrumService:

    def __init__(self):
        self._device = BB60CAdapter()

    def get_current_spectrum(self):

        self._device.connect()

        try:

            config = SweepConfiguration(
                center_frequency_hz=124.650e6,
                span_hz=5e6,
                rbw_hz=10e3,
                vbw_hz=10e3,
                reference_level_dbm=0,
            )

            self._device.configure_sweep(config)

            self._device.start_sweep()

            trace = self._device.get_trace()

            return {
                "trace_length": trace.info.trace_length,
                "bin_size_hz": trace.info.bin_size_hz,
                "start_frequency_hz": trace.info.start_frequency_hz,
                "trace": trace.trace_max.tolist(),
            }

        finally:
            self._device.disconnect()