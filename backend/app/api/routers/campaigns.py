from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.campaign_service import CampaignService

router = APIRouter()
_service = CampaignService()


class CampaignCreate(BaseModel):
    name: str
    description: str = ""
    objective: str = ""
    campaign_type: str = "custom"
    zone: str = ""


class AddMission(BaseModel):
    mission_id: int


@router.get("/campaigns")
def list_campaigns():
    return {"items": _service.list()}


@router.post("/campaigns")
def create_campaign(payload: CampaignCreate):
    cid = _service.create(payload.name, payload.description, payload.objective, payload.campaign_type, payload.zone)
    return {"id": cid}


@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: int):
    return _service.get(campaign_id)


@router.post("/campaigns/{campaign_id}/missions")
def add_mission(campaign_id: int, payload: AddMission):
    mid = _service.add_mission(campaign_id, payload.mission_id)
    return {"id": mid}


@router.get("/campaigns/{campaign_id}/missions")
def list_campaign_missions(campaign_id: int):
    return {"items": _service.list_missions(campaign_id)}


@router.get("/campaigns/{campaign_id}/report")
def campaign_report(campaign_id: int):
    return _service.report(campaign_id)


@router.post("/campaigns/{campaign_id}/status")
def set_status(campaign_id: int, status: str):
    _service.update_status(campaign_id, status)
    return {"status": "ok"}