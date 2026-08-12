from app.rf.state import spectrum_state


class SpectrumService:

    def get_current_spectrum(self):

        with spectrum_state.lock:

            snapshot = (
                spectrum_state.snapshot
            )

            return {
                "timestamp":
                    snapshot.timestamp,

                "center_frequency_hz":
                    snapshot.center_frequency_hz,

                "span_hz":
                    snapshot.span_hz,

                "start_frequency_hz":
                    snapshot.start_frequency_hz,

                "stop_frequency_hz":
                    snapshot.stop_frequency_hz,

                "bin_size_hz":
                    snapshot.bin_size_hz,

                "trace_length":
                    snapshot.trace_length,

                "trace":
                    snapshot.trace,
            }