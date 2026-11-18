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
                    mission_id INTEGER,
                    measured_power_dbm REAL,
                    corrected_power_dbm REAL,
                    chain_loss_db REAL,
                    chain_gain_db REAL,
                    quality_flag TEXT,
                    uncertainty_db REAL,
                    calibration_status TEXT
                )
                """
            )
            c.commit()
            for idx_sql in [
                "CREATE INDEX IF NOT EXISTS idx_geo_mission ON geo_measurements(mission_id)",
                "CREATE INDEX IF NOT EXISTS idx_geo_time ON geo_measurements(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_geo_freq ON geo_measurements(frequency_hz)",
                "CREATE INDEX IF NOT EXISTS idx_geo_receiver ON geo_measurements(receiver_serial)",
            ]:
                try:
                    c.execute(idx_sql)
                    c.commit()
                except Exception:
                    pass
            for col, ddl in [
                ("measured_power_dbm", "REAL"),
                ("corrected_power_dbm", "REAL"),
                ("chain_loss_db", "REAL"),
                ("chain_gain_db", "REAL"),
                ("quality_flag", "TEXT"),
                ("uncertainty_db", "REAL"),
                ("calibration_status", "TEXT"),
            ]:
                try:
                    c.execute(f"ALTER TABLE geo_measurements ADD COLUMN {col} {ddl}")
                    c.commit()
                except Exception:
                    pass

    def record(self, measurement: Dict[str, Any]) -> int:
        measured = measurement.get("measured_power_dbm", measurement.get("level_dbm"))
        chain_loss = measurement.get("chain_loss_db", 0.0) or 0.0
        chain_gain = measurement.get("chain_gain_db", 0.0) or 0.0
        corrected = None
        if measured is not None:
            corrected = measured + chain_gain - chain_loss
        with sqlite3.connect(db_path()) as c:
            cur = c.execute(
                "INSERT INTO geo_measurements (timestamp, latitude, longitude, altitude, gps_valid, gps_source, receiver_serial, antenna_chain_id, frequency_hz, level_dbm, noise_floor_dbm, session_id, mission_id, measured_power_dbm, corrected_power_dbm, chain_loss_db, chain_gain_db, quality_flag, uncertainty_db, calibration_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
                    measured,
                    corrected,
                    chain_loss,
                    chain_gain,
                    measurement.get("quality_flag", "raw"),
                    measurement.get("uncertainty_db"),
                    measurement.get("calibration_status", "uncalibrated"),
                ),
            )
            c.commit()
            return int(cur.lastrowid)

    def list(self, mission_id: Optional[int] = None, limit: int = 500) -> List[Dict[str, Any]]:
        return self.query({"mission_id": mission_id, "limit": limit})

    def query(self, filters: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        filters = filters or {}
        clauses = []
        params: List[Any] = []
        if filters.get("mission_id") is not None:
            clauses.append("mission_id=?")
            params.append(filters["mission_id"])
        if filters.get("session_id") is not None:
            clauses.append("session_id=?")
            params.append(filters["session_id"])
        if filters.get("receiver_serial") is not None:
            clauses.append("receiver_serial=?")
            params.append(filters["receiver_serial"])
        if filters.get("antenna_chain_id") is not None:
            clauses.append("antenna_chain_id=?")
            params.append(filters["antenna_chain_id"])
        if filters.get("frequency_hz") is not None:
            clauses.append("ABS(frequency_hz - ?) <= ?")
            params.append(filters["frequency_hz"])
            params.append(filters.get("frequency_tolerance_hz", 1e6))
        if filters.get("min_lat") is not None:
            clauses.append("latitude >= ?")
            params.append(filters["min_lat"])
        if filters.get("max_lat") is not None:
            clauses.append("latitude <= ?")
            params.append(filters["max_lat"])
        if filters.get("min_lon") is not None:
            clauses.append("longitude >= ?")
            params.append(filters["min_lon"])
        if filters.get("max_lon") is not None:
            clauses.append("longitude <= ?")
            params.append(filters["max_lon"])
        if filters.get("start_time") is not None:
            clauses.append("timestamp >= ?")
            params.append(filters["start_time"])
        if filters.get("end_time") is not None:
            clauses.append("timestamp <= ?")
            params.append(filters["end_time"])
        if filters.get("gps_valid") is not None:
            clauses.append("gps_valid = ?")
            params.append(int(filters["gps_valid"]))
        if filters.get("quality_flag") is not None:
            clauses.append("quality_flag = ?")
            params.append(filters["quality_flag"])

        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        limit = int(filters.get("limit", 500))
        offset = int(filters.get("offset", 0))
        sql = f"SELECT * FROM geo_measurements{where} ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with sqlite3.connect(db_path()) as c:
            c.row_factory = sqlite3.Row
            rows = c.execute(sql, params).fetchall()
            return [dict(r) for r in rows]