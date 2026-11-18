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
                    progress_json TEXT,
                    interrupted INTEGER DEFAULT 0,
                    start_time TEXT,
                    pause_time TEXT,
                    resume_time TEXT,
                    end_time TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            c.commit()
            for col, ddl in [
                ("progress_json", "TEXT"),
                ("interrupted", "INTEGER DEFAULT 0"),
                ("start_time", "TEXT"),
                ("pause_time", "TEXT"),
                ("resume_time", "TEXT"),
                ("end_time", "TEXT"),
            ]:
                try:
                    c.execute(f"ALTER TABLE missions ADD COLUMN {col} {ddl}")
                    c.commit()
                except Exception:
                    pass

    def create(self, name: str, objective: str = "", receiver_serial: Optional[int] = None, antenna_chain_id: Optional[int] = None, profile: dict | None = None) -> int:
        with self._lock, self._conn() as c:
            cur = c.execute(
                "INSERT INTO missions (name, objective, status, receiver_serial, antenna_chain_id, profile_json, progress_json, interrupted, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (name, objective, "created", receiver_serial, antenna_chain_id, json.dumps(profile or {}), json.dumps({}), 0, datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()),
            )
            c.commit()
            return int(cur.lastrowid)

    def list(self) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM missions ORDER BY id DESC").fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["profile"] = json.loads(d.pop("profile_json", "{}") or "{}")
                d["progress"] = json.loads(d.pop("progress_json", "{}") or "{}")
                d["interrupted"] = bool(d.get("interrupted", 0))
                out.append(d)
            return out

    def get(self, mission_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM missions WHERE id=?", (mission_id,)).fetchone()
            if not r:
                return None
            d = dict(r)
            d["profile"] = json.loads(d.pop("profile_json", "{}") or "{}")
            d["progress"] = json.loads(d.pop("progress_json", "{}") or "{}")
            d["interrupted"] = bool(d.get("interrupted", 0))
            return d

    def _update(self, mission_id: int, **fields) -> None:
        with self._lock, self._conn() as c:
            sets = []
            vals = []
            for k, v in fields.items():
                sets.append(f"{k}=?")
                vals.append(v)
            sets.append("updated_at=?")
            vals.append(datetime.now(timezone.utc).isoformat())
            vals.append(mission_id)
            c.execute(f"UPDATE missions SET {', '.join(sets)} WHERE id=?", vals)
            c.commit()

    def execute(self, mission_id: int) -> Dict[str, Any]:
        self._update(mission_id, status="running", interrupted=0, start_time=datetime.now(timezone.utc).isoformat(), pause_time=None, end_time=None)
        return {"status": "running", "mission_id": mission_id}

    def pause(self, mission_id: int) -> Dict[str, Any]:
        self._update(mission_id, status="paused", pause_time=datetime.now(timezone.utc).isoformat())
        return {"status": "paused", "mission_id": mission_id}

    def resume(self, mission_id: int) -> Dict[str, Any]:
        self._update(mission_id, status="running", resume_time=datetime.now(timezone.utc).isoformat(), interrupted=0)
        return {"status": "running", "mission_id": mission_id}

    def cancel(self, mission_id: int) -> Dict[str, Any]:
        self._update(mission_id, status="cancelled", end_time=datetime.now(timezone.utc).isoformat())
        return {"status": "cancelled", "mission_id": mission_id}

    def complete(self, mission_id: int, progress: dict | None = None) -> Dict[str, Any]:
        self._update(mission_id, status="completed", progress_json=json.dumps(progress or {}), end_time=datetime.now(timezone.utc).isoformat(), interrupted=0)
        return {"status": "completed", "mission_id": mission_id}

    def mark_interrupted(self, mission_id: int, progress: dict | None = None) -> Dict[str, Any]:
        self._update(mission_id, status="interrupted", interrupted=1, progress_json=json.dumps(progress or {}))
        return {"status": "interrupted", "mission_id": mission_id}

    def recover_interrupted(self) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM missions WHERE status='running' OR interrupted=1").fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["profile"] = json.loads(d.pop("profile_json", "{}") or "{}")
                d["progress"] = json.loads(d.pop("progress_json", "{}") or "{}")
                d["interrupted"] = bool(d.get("interrupted", 0))
                # Mark as interrupted/paused for user decision.
                if d["status"] == "running":
                    self.mark_interrupted(d["id"], d["progress"])
                    d["status"] = "interrupted"
                out.append(d)
            return out