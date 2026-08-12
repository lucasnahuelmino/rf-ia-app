from app.rf.state import spectrum_state


class SpectrumService:

    def get_current_spectrum(self):

        with spectrum_state.lock:

            return {
                "trace_length":
                    spectrum_state.trace_length,

                "bin_size_hz":
                    spectrum_state.bin_size_hz,

                "start_frequency_hz":
                    spectrum_state.start_frequency_hz,

                "trace":
                    spectrum_state.trace,
            }