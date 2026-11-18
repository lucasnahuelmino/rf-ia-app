from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.devices.bb60c.sdk import bb_api


class SpectrumConfigUpdate(BaseModel):
    center_frequency_hz: Optional[float] = None
    span_hz: Optional[float] = None
    start_frequency_hz: Optional[float] = None
    stop_frequency_hz: Optional[float] = None

    rbw_hz: Optional[float] = None
    vbw_hz: Optional[float] = None
    sweep_time_s: Optional[float] = None

    reference_level_dbm: Optional[float] = None

    attenuation: Optional[int] = None
    gain: Optional[int] = None
    auto_attenuation: Optional[bool] = None
    auto_gain: Optional[bool] = None

    detector: Optional[int] = None
    rbw_shape: Optional[int] = None
    spur_reject: Optional[int] = None

    @field_validator("center_frequency_hz", "start_frequency_hz", "stop_frequency_hz")
    @classmethod
    def _validate_frequency(cls, value):
        if value is None:
            return value
        if value < bb_api.BB_MIN_FREQ.value or value > bb_api.BB_MAX_FREQ.value:
            raise ValueError(
                f"Frequency must be between {bb_api.BB_MIN_FREQ.value} and "
                f"{bb_api.BB_MAX_FREQ.value} Hz."
            )
        return value

    @field_validator("span_hz")
    @classmethod
    def _validate_span(cls, value):
        if value is None:
            return value
        if value < bb_api.BB_MIN_SPAN.value or value > bb_api.BB_MAX_SPAN.value:
            raise ValueError("Span is out of range.")
        return value

    @field_validator("rbw_hz")
    @classmethod
    def _validate_rbw(cls, value):
        if value is None:
            return value
        if value < bb_api.BB_MIN_RBW.value or value > bb_api.BB_MAX_RBW.value:
            raise ValueError("RBW is out of range.")
        return value

    @field_validator("vbw_hz")
    @classmethod
    def _validate_vbw(cls, value):
        if value is None:
            return value
        if value < bb_api.BB_MIN_RBW.value or value > bb_api.BB_MAX_RBW.value:
            raise ValueError("VBW is out of range.")
        return value

    @field_validator("reference_level_dbm")
    @classmethod
    def _validate_ref_level(cls, value):
        if value is None:
            return value
        if value < -bb_api.BB_MAX_REFERENCE.value or value > bb_api.BB_MAX_REFERENCE.value:
            raise ValueError("Reference level is out of range.")
        return value

    @field_validator("attenuation")
    @classmethod
    def _validate_attenuation(cls, value):
        if value is None:
            return value
        if value != bb_api.BB_AUTO_ATTEN and (
            value < 0 or value > bb_api.BB_MAX_ATTEN
        ):
            raise ValueError("Attenuation is out of range.")
        return value

    @field_validator("gain")
    @classmethod
    def _validate_gain(cls, value):
        if value is None:
            return value
        if value != bb_api.BB_AUTO_GAIN and (
            value < 0 or value > bb_api.BB_MAX_GAIN
        ):
            raise ValueError("Gain is out of range.")
        return value

    @field_validator("sweep_time_s")
    @classmethod
    def _validate_sweep_time(cls, value):
        if value is None:
            return value
        if value != 0.0 and (
            value < bb_api.BB_MIN_SWEEP_TIME.value
            or value > bb_api.BB_MAX_SWEEP_TIME.value
        ):
            raise ValueError("Sweep time is out of range.")
        return value

    @field_validator("detector")
    @classmethod
    def _validate_detector(cls, value):
        if value is None:
            return value
        if value not in (bb_api.BB_MIN_AND_MAX, bb_api.BB_AVERAGE):
            raise ValueError("Detector must be BB_MIN_AND_MAX or BB_AVERAGE.")
        return value

    @field_validator("rbw_shape")
    @classmethod
    def _validate_rbw_shape(cls, value):
        if value is None:
            return value
        if value not in (
            bb_api.BB_RBW_SHAPE_NUTTALL,
            bb_api.BB_RBW_SHAPE_FLATTOP,
            bb_api.BB_RBW_SHAPE_CISPR,
        ):
            raise ValueError("RBW shape is invalid.")
        return value

    @field_validator("spur_reject")
    @classmethod
    def _validate_spur(cls, value):
        if value is None:
            return value
        if value not in (bb_api.BB_NO_SPUR_REJECT, bb_api.BB_SPUR_REJECT):
            raise ValueError("Spur rejection must be 0 or 1.")
        return value