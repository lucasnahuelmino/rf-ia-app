from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.export_service import ExportService

router = APIRouter()
_service = ExportService()


class ExportRequest(BaseModel):
    format: str = "csv"  # csv | xlsx | pdf
    filename: str = "export"
    rows: List[Dict[str, Any]] = []
    sheets: Dict[str, List[Dict[str, Any]]] | None = None
    title: str = "RF Monitor Report"
    sections: List[Dict[str, Any]] | None = None


@router.post("/exports")
def create_export(payload: ExportRequest):
    if payload.format == "csv":
        path = _service.to_csv(payload.filename + ".csv", payload.rows)
    elif payload.format == "xlsx":
        sheets = payload.sheets or {"Data": payload.rows}
        path = _service.to_xlsx(payload.filename + ".xlsx", sheets)
    elif payload.format == "pdf":
        sections = payload.sections or [{"heading": "Data", "lines": [str(r) for r in payload.rows[:50]]}]
        path = _service.to_pdf(payload.filename + ".pdf", payload.title, sections)
    else:
        raise ValueError("Unsupported format")
    return {"status": "ok", "path": path, "filename": os.path.basename(path)} if False else {"status": "ok", "path": path}