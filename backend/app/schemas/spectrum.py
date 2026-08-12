from pydantic import BaseModel


class SpectrumConfigUpdate(BaseModel):

    center_frequency_hz: float

    span_hz: float

    rbw_hz: float

    vbw_hz: float

    reference_level_dbm: float