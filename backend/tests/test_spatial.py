import tempfile, os
from app.services.geo_service import GeoMeasurementService
from app.services.spatial_analysis import SpatialAnalysisService


def test_heatmap_and_fm_analysis():
    tmp = tempfile.mkdtemp()
    os.environ["RF_DB_DIR"] = tmp
    geo = GeoMeasurementService()
    for i in range(5):
        geo.record({"latitude": -34.6 + i*0.001, "longitude": -58.38 + i*0.001, "frequency_hz": 100e6, "level_dbm": -50 - i, "gps_valid": True, "gps_source": "SIM"})
    svc = SpatialAnalysisService()
    hm = svc.heatmap(metric="level_dbm", grid_size=4)
    assert hm["cells"]
    fm = svc.fm_analysis(100e6)
    assert fm["count"] == 5
    assert fm["level_mean"] is not None