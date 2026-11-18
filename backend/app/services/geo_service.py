from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def db_path() -> str:
    d = os.environ.get("RF_DB_DIR", os.path.join(os.getcwd(), "data"))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "rf_monitor.db")


class GeoMeasurementService:
    def __init__(self) -> None:
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(db_path()) as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS geo_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    latitude REAL,
                    longitude REAL,
                    altitude REAL,
                    gps_valid INTEGER,
                    gps_source TEXT,
                    receiver_serial INTEGER,
                    antenna_chain_id INTEGER,
                    frequency_hz REAL,
                    level_dbm REAL,
                    noise_floor_dbm REAL,
                    session_id INTEGER,
                    mission_id INTEGER
                )
                """
            )
            c.commit()

    def record(self, measurement: Dict[str, Any]) -> int:
        with sqlite3.connect(db_path()) as c:
            cur = c.execute(
                "INSERT INTO geo_measurements (timestamp, latitude, longitude, altitude, gps_valid, gps_source, receiver_serial, antenna_chain_id, frequency_hz, level_dbm, noise_floor_dbm, session_id, mission_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    measurement.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    measurement.get("latitude"),
                    measurement.get("longitude"),
                    measurement.get("altitude"),
                    int(measurement.get("gps_valid", False)),
                    measurement.get("gps_source"),
                    measurement.get("receiver_serial"),
                    measurement.get("antenna_chain_id"),
                    measurement.get("frequency_hz"),
                    measurement.get("level_dbm"),
                    measurement.get("noise_floor_dbm"),
                    measurement.get("session_id"),
                    measurement.get("mission_id"),
                ),
            )
            c.commit()
            return int(cur.lastrowid)

    def list(self, mission_id: Optional[int] = None, limit: int = 500) -> List[Dict[str, Any]]:
        with sqlite3.connect(db_path()) as c:
            c.row_factory = sqlite3.Row
            if mission_id is not None:
                rows = c.execute("SELECT * FROM geo_measurements WHERE mission_id=? ORDER BY id DESC LIMIT ?", (mission_id, limit)).fetchall()
            else:
                rows = c.execute("SELECT * FROM geo_measurements ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]