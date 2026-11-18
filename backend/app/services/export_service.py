from __future__ import annotations

import csv
import json
import os
from typing import Any, Dict, List

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas


def export_dir() -> str:
    d = os.environ.get("RF_EXPORT_DIR", os.path.join(os.getcwd(), "data", "exports"))
    os.makedirs(d, exist_ok=True)
    return d


class ExportService:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = base_dir or export_dir()

    def to_csv(self, filename: str, rows: List[Dict[str, Any]], fieldnames: List[str] | None = None) -> str:
        path = os.path.join(self.base_dir, filename)
        if fieldnames is None:
            fieldnames = list(rows[0].keys()) if rows else []
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return path

    def to_xlsx(self, filename: str, sheets: Dict[str, List[Dict[str, Any]]]) -> str:
        path = os.path.join(self.base_dir, filename)
        wb = Workbook()
        first = True
        for sheet_name, rows in sheets.items():
            if first:
                ws = wb.active
                ws.title = sheet_name[:31]
                first = False
            else:
                ws = wb.create_sheet(title=sheet_name[:31])

            if rows:
                headers = list(rows[0].keys())
                ws.append(headers)
                for cell in ws[1]:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill("solid", fgColor="1F4E79")
                for row in rows:
                    ws.append([row.get(h) for h in headers])
                for idx, h in enumerate(headers, start=1):
                    ws.column_dimensions[get_column_letter(idx)].width = max(12, len(str(h)) + 4)
        wb.save(path)
        return path

    def to_geojson(self, filename: str, points: List[Dict[str, Any]]) -> str:
        path = os.path.join(self.base_dir, filename)
        features = []
        for p in points:
            if p.get("latitude") is None or p.get("longitude") is None:
                continue
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [p["longitude"], p["latitude"]],
                },
                "properties": {k: v for k, v in p.items() if k not in ("latitude", "longitude")},
            })
        geojson = {"type": "FeatureCollection", "features": features}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2)
        return path

    def to_pdf(self, filename: str, title: str, sections: List[Dict[str, Any]]) -> str:
        path = os.path.join(self.base_dir, filename)
        c = pdf_canvas.Canvas(path, pagesize=letter)
        width, height = letter
        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, title)
        y -= 30
        c.setFont("Helvetica", 10)
        for section in sections:
            heading = section.get("heading", "")
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, heading)
            y -= 18
            c.setFont("Helvetica", 10)
            for line in section.get("lines", []):
                c.drawString(60, y, str(line))
                y -= 14
                if y < 60:
                    c.showPage()
                    y = height - 50
        c.save()
        return path