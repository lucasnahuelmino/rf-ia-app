from app.rf.config import spectrum_config

from app.schemas.spectrum import (
    SpectrumConfigUpdate,
)


class ConfigService:

    def get_config(self):

        with spectrum_config.lock:

            return {
                "center_frequency_hz":
                    spectrum_config.center_frequency_hz,

                "span_hz":
                    spectrum_config.span_hz,

                "rbw_hz":
                    spectrum_config.rbw_hz,

                "vbw_hz":
                    spectrum_config.vbw_hz,

                "reference_level_dbm":
                    spectrum_config.reference_level_dbm,
            }

    def update_config(
        self,
        config: SpectrumConfigUpdate,
    ):

        with spectrum_config.lock:

            spectrum_config.center_frequency_hz = (
                config.center_frequency_hz
            )

            spectrum_config.span_hz = (
                config.span_hz
            )

            spectrum_config.rbw_hz = (
                config.rbw_hz
            )

            spectrum_config.vbw_hz = (
                config.vbw_hz
            )

            spectrum_config.reference_level_dbm = (
                config.reference_level_dbm
            )

            spectrum_config.version += 1

        return self.get_config()