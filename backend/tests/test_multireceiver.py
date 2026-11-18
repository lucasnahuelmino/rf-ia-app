from app.devices.bb60c.multi_device import MultiDeviceManager
from app.services.antenna_service import AntennaService
from app.services.mission_service import MissionService
from app.services.occupation_audit import OccupationAuditService
import tempfile, os


class FakeAdapter:
    def connect(self):
        pass
    def disconnect(self):
        pass
    def get_firmware_version(self):
        return 7


def test_multidevice_alias_and_state():
    m = MultiDeviceManager(factory=FakeAdapter)
    info = m.connect(12345)
    assert info.state == "CONNECTED"
    m.set_alias(12345, "RX-A")
    r = m.get(12345)
    assert r.alias == "RX-A"
    m.disconnect(12345)
    assert m.get(12345).state == "DISCONNECTED"


def test_antenna_and_mission_persistence():
    tmp = tempfile.mkdtemp()
    os.environ["RF_DB_DIR"] = tmp
    ant = AntennaService()
    aid = ant.create("FM chain", ["antenna", "splitter", "bb60c"], 12345, 3.0)
    assert ant.get(aid) is not None

    miss = MissionService()
    mid = miss.create("FM audit", "audit", 12345, aid, {"band": "FM"})
    assert miss.get(mid)["status"] == "created"
    miss.execute(mid)
    assert miss.get(mid)["status"] == "running"
    miss.mark_interrupted(mid, {"progress": 50})
    assert miss.get(mid)["status"] == "interrupted"
    recovered = miss.recover_interrupted()
    assert any(r["id"] == mid for r in recovered)
    miss.resume(mid)
    assert miss.get(mid)["status"] == "running"


def test_occupation_audit():
    svc = OccupationAuditService()
    trace = [-90.0] * 10 + [-40.0] + [-90.0] * 10
    res = svc.audit_channel(100e6, trace, 1000.0, 99990.0)
    assert res["peak_frequency_hz"] is not None
    assert res["max_power_dbm"] == -40.0
    assert res["activity_ratio"] >= 0