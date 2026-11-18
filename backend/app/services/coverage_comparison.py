from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from app.services.coverage_models import CoverageModelService


class CoverageComparisonService:
    def __init__(self) -> None:
        self.models = CoverageModelService()

    def compare(self, model: str, params: Dict[str, Any], measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        preds = []
        meas = []
        errors = []
        for m in measurements:
            if m.get("level_dbm") is None:
                continue
            d_km = m.get("distance_km")
            if d_km is None:
                continue
            p = dict(params)
            p["distance_km"] = d_km
            pred = self.models.predict(model, p)["predicted_rssi_dbm"]
            preds.append(pred)
            meas.append(m["level_dbm"])
            errors.append(pred - m["level_dbm"])

        if not errors:
            return {"count": 0, "message": "Sin datos comparables"}

        return {
            "count": len(errors),
            "mean_error_db": float(np.mean(errors)),
            "rmse_db": float(np.sqrt(np.mean(np.array(errors) ** 2))),
            "mae_db": float(np.mean(np.abs(errors))),
            "max_error_db": float(np.max(np.abs(errors))),
            "predictions": preds,
            "measurements": meas,
        }