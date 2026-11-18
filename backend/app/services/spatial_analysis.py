from __future__ import annotations

import json
import math
from typing import Any, Dict, List, Optional

import numpy as np

from app.services.geo_service import GeoMeasurementService


class SpatialAnalysisService:
    def __init__(self) -> None:
        self.geo = GeoMeasurementService()

    def route(self, mission_id: Optional[int] = None, frequency_hz: Optional[float] = None, tolerance_hz: float = 1e6) -> List[Dict[str, Any]]:
        items = self.geo.list(mission_id, limit=100000)
        if frequency_hz is not None:
            items = [i for i in items if i.get("frequency_hz") is not None and abs(i["frequency_hz"] - frequency_hz) <= tolerance_hz]
        return items

    def heatmap(self, mission_id: Optional[int] = None, metric: str = "level_dbm", grid_size: int = 20, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        f = dict(filters or {})
        if mission_id is not None:
            f["mission_id"] = mission_id
        f["limit"] = 100000
        items = self.geo.query(f)
        if not items:
            return {"cells": [], "min": None, "max": None}

        lats = [i["latitude"] for i in items if i.get("latitude") is not None]
        lons = [i["longitude"] for i in items if i.get("longitude") is not None]
        if not lats or not lons:
            return {"cells": [], "min": None, "max": None}

        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        lat_step = (max_lat - min_lat) / grid_size or 1e-9
        lon_step = (max_lon - min_lon) / grid_size or 1e-9

        grid = {}
        for item in items:
            lat = item.get("latitude")
            lon = item.get("longitude")
            val = item.get(metric)
            if lat is None or lon is None or val is None:
                continue
            ix = min(grid_size - 1, max(0, int((lon - min_lon) / lon_step)))
            iy = min(grid_size - 1, max(0, int((lat - min_lat) / lat_step)))
            key = (ix, iy)
            grid.setdefault(key, []).append(val)

        cells = []
        values = []
        for (ix, iy), vals in grid.items():
            agg = float(np.mean(vals))
            values.append(agg)
            cells.append({
                "ix": ix,
                "iy": iy,
                "lat": min_lat + (iy + 0.5) * lat_step,
                "lon": min_lon + (ix + 0.5) * lon_step,
                "value": agg,
                "count": len(vals),
            })

        return {
            "cells": cells,
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "grid_size": grid_size,
        }

    def fm_analysis(self, nominal_frequency_hz: float, tolerance_hz: float = 200000.0, mission_id: Optional[int] = None) -> Dict[str, Any]:
        items = self.route(mission_id, nominal_frequency_hz, tolerance_hz)
        if not items:
            return {"count": 0, "message": "Sin detecciones"}

        levels = [i.get("level_dbm") for i in items if i.get("level_dbm") is not None]
        lats = [i.get("latitude") for i in items if i.get("latitude") is not None]
        lons = [i.get("longitude") for i in items if i.get("longitude") is not None]

        # gaps: time intervals? just count points without gps
        no_gps = [i for i in items if not i.get("gps_valid")]

        return {
            "count": len(items),
            "points_with_gps": len(lats),
            "points_without_gps": len(no_gps),
            "level_mean": float(np.mean(levels)) if levels else None,
            "level_max": float(np.max(levels)) if levels else None,
            "level_min": float(np.min(levels)) if levels else None,
            "level_std": float(np.std(levels)) if levels else None,
            "lat_range": [min(lats), max(lats)] if lats else None,
            "lon_range": [min(lons), max(lons)] if lons else None,
            "first_timestamp": items[-1].get("timestamp") if items else None,
            "last_timestamp": items[0].get("timestamp") if items else None,
        }

    def compare_routes(self, mission_a: int, mission_b: int, frequency_hz: Optional[float] = None, tolerance_hz: float = 1e6) -> Dict[str, Any]:
        a = self.route(mission_a, frequency_hz, tolerance_hz)
        b = self.route(mission_b, frequency_hz, tolerance_hz)
        la = [i.get("level_dbm") for i in a if i.get("level_dbm") is not None]
        lb = [i.get("level_dbm") for i in b if i.get("level_dbm") is not None]
        return {
            "mission_a": {"count": len(a), "level_mean": float(np.mean(la)) if la else None},
            "mission_b": {"count": len(b), "level_mean": float(np.mean(lb)) if lb else None},
            "delta_mean_db": (float(np.mean(la) - np.mean(lb)) if la and lb else None),
        }