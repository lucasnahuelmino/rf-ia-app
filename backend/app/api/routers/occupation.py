from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.rf.state import spectrum_state
from app.services.occupation_audit import OccupationAuditService

router = APIRouter()
_service = OccupationAuditService()


class OccupationRequest(BaseModel):
    channels: list[dict] = []


@router.post("/occupation/audit")
def audit(payload: OccupationRequest):
    with spectrum_state.lock:
        snap = spectrum_state.snapshot
        trace = snap.trace or []
        bin_size = snap.bin_size_hz or 1.0
        start = snap.start_frequency_hz

    if not trace:
        return {"items": []}

    channels = payload.channels or [{"frequency": snap.center_frequency_hz}]
    return {"items": _service.audit_band(channels, trace, bin_size, start)}