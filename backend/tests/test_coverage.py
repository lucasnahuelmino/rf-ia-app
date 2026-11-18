from app.services.coverage_models import CoverageModelService
from app.services.coverage_comparison import CoverageComparisonService


def test_coverage_models():
    svc = CoverageModelService()
    params = {"frequency_hz": 100e6, "distance_km": 1, "tx_power_dbm": 30, "tx_gain_dbi": 6, "rx_gain_dbi": 0, "losses_db": 0, "tx_height_m": 30, "rx_height_m": 1.5}
    r1 = svc.predict("free_space", params)
    assert "predicted_rssi_dbm" in r1
    r2 = svc.predict("okumura_hata", params)
    assert "path_loss_db" in r2


def test_coverage_compare():
    svc = CoverageComparisonService()
    params = {"frequency_hz": 100e6, "tx_power_dbm": 30, "tx_gain_dbi": 6, "rx_gain_dbi": 0, "losses_db": 0, "tx_height_m": 30, "rx_height_m": 1.5}
    meas = [{"distance_km": 1, "level_dbm": -60}, {"distance_km": 2, "level_dbm": -70}]
    res = svc.compare("free_space", params, meas)
    assert res["count"] == 2
    assert res["rmse_db"] is not None