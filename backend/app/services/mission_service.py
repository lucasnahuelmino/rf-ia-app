from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def db_path() -> str:
    d = os.environ.get("RF_DB_DIR", os.path.join(os.getcwd(), "data"))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "rf_monitor.db")


class MissionService:
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
                CREATE TABLE IF NOT EXISTS missions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    objective TEXT,
                    status TEXT,
                    receiver_serial INTEGER,
                    antenna_chain_id INTEGER,
                    profile_json TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            c.commit()

    def create(self, name: str, objective: str = "", receiver_serial: Optional[int] = None, antenna_chain_id: Optional[int] = None, profile: dict | None = None) -> int:
        with self._lock, self._conn() as c:
            cur = c.execute(
                "INSERT INTO missions (name, objective, status, receiver_serial, antenna_chain_id, profile_json, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                (name, objective, "created", receiver_serial, antenna_chain_id, json.dumps(profile or {}), datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()),
            )
            c.commit()
            return int(cur.lastrowid)

    def list(self) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM missions ORDER BY id DESC").fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["profile"] = json.loads(d.pop("profile_json", "{}"))
                out.append(d)
            return out

    def get(self, mission_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM missions WHERE id=?", (mission_id,)).fetchone()
            if not r:
                return None
            d = dict(r)
            d["profile"] = json.loads(d.pop("profile_json", "{}"))
            return d

    def set_status(self, mission_id: int, status: str) -> None:
        with self._lock, self._conn() as c:
            c.execute("UPDATE missions SET status=?, updated_at=? WHERE id=?", (status, datetime.now(timezone.utc).isoformat(), mission_id))
            c.commit()

    def execute(self, mission_id: int) -> Dict[str, Any]:
        self.set_status(mission_id, "running")
        return {"status": "running", "mission_id": mission_id}

    def pause(self, mission_id: int) -> Dict[str, Any]:
        self.set_status(mission_id, "paused")
        return {"status": "paused", "mission_id": mission_id}

    def resume(self, mission_id: int) -> Dict[str, Any]:
        self.set_status(mission_id, "running")
        return {"status": "running", "mission_id": mission_id}

    def cancel(self, mission_id: int) -> Dict[str, Any]:
        self.set_status(mission_id, "cancelled")
        return {"status": "cancelled", "mission_id": mission_id}