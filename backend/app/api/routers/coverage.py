from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.coverage_models import CoverageModelService
from app.services.coverage_comparison import CoverageComparisonService

router = APIRouter()
_models = CoverageModelService()
_compare = CoverageComparisonService()


class PredictRequest(BaseModel):
    model: str = "free_space"
    params: dict


class CompareRequest(BaseModel):
    model: str = "free_space"
    params: dict
    measurements: list[dict]


@router.post("/coverage/predict")
def predict(payload: PredictRequest):
    return _models.predict(payload.model, payload.params)


@router.post("/coverage/compare")
def compare(payload: CompareRequest):
    return _compare.compare(payload.model, payload.params, payload.measurements)