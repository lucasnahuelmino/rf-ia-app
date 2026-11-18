import tempfile, os
from app.services.campaign_service import CampaignService


def test_campaign_create_and_report():
    tmp = tempfile.mkdtemp()
    os.environ["RF_DB_DIR"] = tmp
    svc = CampaignService()
    cid = svc.create("Test Campaign", "desc", "objective", "FM", "zone")
    svc.add_mission(cid, 1)
    report = svc.report(cid)
    assert report["campaign"]["name"] == "Test Campaign"
    assert report["mission_count"] == 1