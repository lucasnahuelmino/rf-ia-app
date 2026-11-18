from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.ml.features import extract_spectrum_features
from app.ml.models import AnomalyDetector, SignalClassifier

router = APIRouter()

_classifier = SignalClassifier()
_anomaly = AnomalyDetector()


class TrainRequest(BaseModel):
    X: list[list[float]]
    y: list


class PredictRequest(BaseModel):
    X: list[list[float]]


class FeatureRequest(BaseModel):
    trace: list[float]


@router.post("/ml/features/spectrum")
def spectrum_features(payload: FeatureRequest):
    return extract_spectrum_features(payload.trace)


@router.post("/ml/train")
def train(payload: TrainRequest):
    _classifier.train(payload.X, payload.y)
    return {"status": "trained"}


@router.post("/ml/predict")
def predict(payload: PredictRequest):
    try:
        preds = _classifier.predict(payload.X)
    except RuntimeError as exc:
        return {"status": "error", "detail": str(exc)}
    return {"predictions": preds}


@router.post("/ml/anomaly/fit")
def anomaly_fit(payload: PredictRequest):
    _anomaly.fit(payload.X)
    return {"status": "fitted"}


@router.post("/ml/anomaly/predict")
def anomaly_predict(payload: PredictRequest):
    return {"predictions": _anomaly.predict(payload.X)}