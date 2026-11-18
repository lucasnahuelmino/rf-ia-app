from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.spatial_analysis import SpatialAnalysisService
from app.services.export_service import ExportService
from app.services.geo_service import GeoMeasurementService

router = APIRouter()
_analysis = SpatialAnalysisService()
_export = ExportService()
_geo = GeoMeasurementService()


class HeatmapRequest(BaseModel):
    mission_id: int | None = None
    metric: str = "level_dbm"
    grid_size: int = 20
    filters: dict | None = None


class FMAnalysisRequest(BaseModel):
    nominal_frequency_hz: float
    tolerance_hz: float = 200000.0
    mission_id: int | None = None


class CompareRequest(BaseModel):
    mission_a: int
    mission_b: int
    frequency_hz: float | None = None
    tolerance_hz: float = 1e6


@router.get("/spatial/route")
def spatial_route(mission_id: int | None = None, frequency_hz: float | None = None, tolerance_hz: float = 1e6):
    return {"items": _analysis.route(mission_id, frequency_hz, tolerance_hz)}


@router.post("/spatial/heatmap")
def spatial_heatmap(payload: HeatmapRequest):
    return _analysis.heatmap(payload.mission_id, payload.metric, payload.grid_size, payload.filters)


@router.post("/spatial/fm-analysis")
def spatial_fm(payload: FMAnalysisRequest):
    return _analysis.fm_analysis(payload.nominal_frequency_hz, payload.tolerance_hz, payload.mission_id)


@router.post("/spatial/compare")
def spatial_compare(payload: CompareRequest):
    return _analysis.compare_routes(payload.mission_a, payload.mission_b, payload.frequency_hz, payload.tolerance_hz)


@router.post("/spatial/export-geojson")
def export_geojson(mission_id: int | None = None):
    points = _geo.list(mission_id, limit=100000)
    path = _export.to_geojson("geo_export.geojson", points)
    return {"path": path}