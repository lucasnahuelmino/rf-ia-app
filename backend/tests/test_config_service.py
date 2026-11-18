import pytest

from app.services.config_service import ConfigService
from app.schemas.spectrum import SpectrumConfigUpdate


def test_config_update_partial_and_frequency_derivation():
    service = ConfigService()

    updated = service.update_config(
        SpectrumConfigUpdate(
            start_frequency_hz=100e6,
            stop_frequency_hz=110e6,
            rbw_hz=5000,
        )
    )

    assert updated["start_frequency_hz"] == 100e6
    assert updated["stop_frequency_hz"] == 110e6
    assert updated["center_frequency_hz"] == 105e6
    assert updated["span_hz"] == 10e6
    assert updated["rbw_hz"] == 5000

    current = service.get_config()
    assert current["center_frequency_hz"] == 105e6


def test_config_validation_rejects_bad_span():
    with pytest.raises(Exception):
        SpectrumConfigUpdate(span_hz=1.0)  # below BB_MIN_SPAN