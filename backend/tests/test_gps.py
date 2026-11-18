from app.gps.nmea import parse_nmea, _nmea_to_decimal
from app.services.gps_service import GPSService
from app.services.geo_service import GeoMeasurementService
import tempfile, os


def test_nmea_decimal_conversion():
    assert abs(_nmea_to_decimal("3436.1234", "S") + 34.6020566667) < 1e-6


def test_nmea_parse_gga():
    line = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
    pos = parse_nmea(line)
    assert pos is not None
    assert pos.valid is True
    assert abs(pos.latitude - 48.1173) < 1e-4
    assert abs(pos.longitude - 11.5166667) < 1e-4
    assert pos.satellites == 8


def test_simulated_gps_and_geo_record():
    tmp = tempfile.mkdtemp()
    os.environ["RF_DB_DIR"] = tmp
    svc = GPSService()
    svc.connect_simulated()
    pos = svc.read_position()
    assert pos is not None
    assert pos.valid is True

    geo = GeoMeasurementService()
    gid = geo.record({"latitude": pos.latitude, "longitude": pos.longitude, "frequency_hz": 100e6, "level_dbm": -50, "gps_valid": True, "gps_source": "SIMULATED"})
    assert gid > 0
    items = geo.list()
    assert len(items) == 1