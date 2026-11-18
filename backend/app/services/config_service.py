from __future__ import annotations

from typing import Optional

from app.rf.config import spectrum_config

from app.schemas.spectrum import SpectrumConfigUpdate


class ConfigService:
    def get_config(self) -> dict:
        with spectrum_config.lock:
            return {
                "center_frequency_hz": spectrum_config.center_frequency_hz,
                "span_hz": spectrum_config.span_hz,
                "start_frequency_hz": spectrum_config.start_frequency_hz,
                "stop_frequency_hz": spectrum_config.stop_frequency_hz,
                "rbw_hz": spectrum_config.rbw_hz,
                "vbw_hz": spectrum_config.vbw_hz,
                "sweep_time_s": spectrum_config.sweep_time_s,
                "reference_level_dbm": spectrum_config.reference_level_dbm,
                "attenuation": spectrum_config.attenuation,
                "gain": spectrum_config.gain,
                "auto_attenuation": spectrum_config.auto_attenuation,
                "auto_gain": spectrum_config.auto_gain,
                "detector": spectrum_config.detector,
                "rbw_shape": spectrum_config.rbw_shape,
                "spur_reject": spectrum_config.spur_reject,
            }

    def update_config(self, config: SpectrumConfigUpdate) -> dict:
        with spectrum_config.lock:
            if config.center_frequency_hz is not None:
                spectrum_config.center_frequency_hz = config.center_frequency_hz
            if config.span_hz is not None:
                spectrum_config.span_hz = config.span_hz
            if config.rbw_hz is not None:
                spectrum_config.rbw_hz = config.rbw_hz
            if config.vbw_hz is not None:
                spectrum_config.vbw_hz = config.vbw_hz
            if config.sweep_time_s is not None:
                spectrum_config.sweep_time_s = config.sweep_time_s
            if config.reference_level_dbm is not None:
                spectrum_config.reference_level_dbm = config.reference_level_dbm
            if config.attenuation is not None:
                spectrum_config.attenuation = config.attenuation
            if config.gain is not None:
                spectrum_config.gain = config.gain
            if config.auto_attenuation is not None:
                spectrum_config.auto_attenuation = config.auto_attenuation
            if config.auto_gain is not None:
                spectrum_config.auto_gain = config.auto_gain
            if config.detector is not None:
                spectrum_config.detector = config.detector
            if config.rbw_shape is not None:
                spectrum_config.rbw_shape = config.rbw_shape
            if config.spur_reject is not None:
                spectrum_config.spur_reject = config.spur_reject

            # Frequency representation.
            if (
                config.start_frequency_hz is not None
                or config.stop_frequency_hz is not None
            ):
                start = (
                    config.start_frequency_hz
                    if config.start_frequency_hz is not None
                    else spectrum_config.start_frequency_hz
                )
                stop = (
                    config.stop_frequency_hz
                    if config.stop_frequency_hz is not None
                    else spectrum_config.stop_frequency_hz
                )

                if start is None or stop is None:
                    if spectrum_config.start_frequency_hz is None:
                        center = spectrum_config.center_frequency_hz
                        span = spectrum_config.span_hz
                        start = center - span / 2.0
                    if spectrum_config.stop_frequency_hz is None:
                        center = spectrum_config.center_frequency_hz
                        span = spectrum_config.span_hz
                        stop = center + span / 2.0

                spectrum_config.start_frequency_hz = start
                spectrum_config.stop_frequency_hz = stop
                spectrum_config.center_frequency_hz = (start + stop) / 2.0
                spectrum_config.span_hz = stop - start
            elif (
                config.center_frequency_hz is not None
                or config.span_hz is not None
            ):
                center = spectrum_config.center_frequency_hz
                span = spectrum_config.span_hz
                spectrum_config.start_frequency_hz = center - span / 2.0
                spectrum_config.stop_frequency_hz = center + span / 2.0

            spectrum_config.version += 1

        return self.get_config()