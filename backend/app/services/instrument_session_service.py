from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def db_path() -> str:
    d = os.environ.get("RF_DB_DIR", os.path.join(os.getcwd(), "data"))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "rf_monitor.db")


class InstrumentSessionService:
    def __init__(self) -> None:
        self.path = db_path()
        self._lock = threading.RLock()
        self._init()

    def _conn(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def _init(self) -> None:
        with self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS instrument_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    receiver_serial INTEGER,
                    session_type TEXT,
                    center_frequency_hz REAL,
                    span_hz REAL,
                    rbw_hz REAL,
                    vbw_hz REAL,
                    reference_level_dbm REAL,
                    attenuation INTEGER,
                    gain INTEGER,
                    detector INTEGER,
                    mode TEXT,
                    status TEXT,
                    config_json TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            c.commit()

    def create(self, name: str, receiver_serial: int | None = None, session_type: str = "sweep", config: dict | None = None) -> int:
        cfg = config or {}
        with self._lock, self._conn() as c:
            cur = c.execute(
                "INSERT INTO instrument_sessions (name, receiver_serial, session_type, center_frequency_hz, span_hz, rbw_hz, vbw_hz, reference_level_dbm, attenuation, gain, detector, mode, status, config_json, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    name,
                    receiver_serial,
                    session_type,
                    cfg.get("center_frequency_hz"),
                    cfg.get("span_hz"),
                    cfg.get("rbw_hz"),
                    cfg.get("vbw_hz"),
                    cfg.get("reference_level_dbm"),
                    cfg.get("attenuation"),
                    cfg.get("gain"),
                    cfg.get("detector"),
                    cfg.get("mode", "sweep"),
                    "created",
                    json.dumps(cfg),
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            c.commit()
            return int(cur.lastrowid)

    def list(self, receiver_serial: int | None = None) -> List[Dict[str, Any]]:
        with self._conn() as c:
            if receiver_serial is not None:
                rows = c.execute("SELECT * FROM instrument_sessions WHERE receiver_serial=? ORDER BY id DESC", (receiver_serial,)).fetchall()
            else:
                rows = c.execute("SELECT * FROM instrument_sessions ORDER BY id DESC").fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["config"] = json.loads(d.pop("config_json", "{}") or "{}")
                out.append(d)
            return out

    def get(self, session_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM instrument_sessions WHERE id=?", (session_id,)).fetchone()
            if not r:
                return None
            d = dict(r)
            d["config"] = json.loads(d.pop("config_json", "{}") or "{}")
            return d

    def update_status(self, session_id: int, status: str) -> None:
        with self._lock, self._conn() as c:
            c.execute("UPDATE instrument_sessions SET status=?, updated_at=? WHERE id=?", (status, datetime.now(timezone.utc).isoformat(), session_id))
            c.commit()

    def update_config(self, session_id: int, config: dict) -> None:
        with self._lock, self._conn() as c:
            c.execute("UPDATE instrument_sessions SET config_json=?, center_frequency_hz=?, span_hz=?, rbw_hz=?, vbw_hz=?, reference_level_dbm=?, attenuation=?, gain=?, detector=?, mode=?, updated_at=? WHERE id=?",
                      (json.dumps(config), config.get("center_frequency_hz"), config.get("span_hz"), config.get("rbw_hz"), config.get("vbw_hz"), config.get("reference_level_dbm"), config.get("attenuation"), config.get("gain"), config.get("detector"), config.get("mode"), datetime.now(timezone.utc).isoformat(), session_id))
            c.commit()