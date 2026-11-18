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


class CampaignService:
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
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    objective TEXT,
                    campaign_type TEXT,
                    zone TEXT,
                    status TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    notes TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS campaign_missions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER,
                    mission_id INTEGER,
                    added_at TEXT,
                    FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
                )
                """
            )
            c.commit()

    def create(self, name: str, description: str = "", objective: str = "", campaign_type: str = "custom", zone: str = "") -> int:
        with self._lock, self._conn() as c:
            cur = c.execute(
                "INSERT INTO campaigns (name, description, objective, campaign_type, zone, status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                (name, description, objective, campaign_type, zone, "created", datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()),
            )
            c.commit()
            return int(cur.lastrowid)

    def list(self) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall()
            return [dict(r) for r in rows]

    def get(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
            return dict(r) if r else None

    def update_status(self, campaign_id: int, status: str) -> None:
        with self._lock, self._conn() as c:
            c.execute("UPDATE campaigns SET status=?, updated_at=? WHERE id=?", (status, datetime.now(timezone.utc).isoformat(), campaign_id))
            c.commit()

    def add_mission(self, campaign_id: int, mission_id: int) -> int:
        with self._lock, self._conn() as c:
            cur = c.execute("INSERT INTO campaign_missions (campaign_id, mission_id, added_at) VALUES (?,?,?)", (campaign_id, mission_id, datetime.now(timezone.utc).isoformat()))
            c.commit()
            return int(cur.lastrowid)

    def list_missions(self, campaign_id: int) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute("SELECT mission_id FROM campaign_missions WHERE campaign_id=?", (campaign_id,)).fetchall()
            return [dict(r) for r in rows]

    def report(self, campaign_id: int) -> Dict[str, Any]:
        campaign = self.get(campaign_id)
        missions = self.list_missions(campaign_id)
        return {"campaign": campaign, "missions": missions, "mission_count": len(missions)}