from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def db_path() -> str:
    d = os.environ.get("RF_DB_DIR", os.path.join(os.getcwd(), "data"))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "rf_monitor.db")


class AntennaService:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or db_path()
        self._init()

    def _conn(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def _init(self) -> None:
        with self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS antenna_chains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    components_json TEXT,
                    topology_json TEXT,
                    receiver_serial INTEGER,
                    losses_db REAL,
                    created_at TEXT
                )
                """
            )
            c.commit()
            for col, ddl in [("topology_json", "TEXT")]:
                try:
                    c.execute(f"ALTER TABLE antenna_chains ADD COLUMN {col} {ddl}")
                    c.commit()
                except Exception:
                    pass

    def create(self, name: str, components: List[str], receiver_serial: Optional[int] = None, losses_db: float = 0.0, topology: dict | None = None) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO antenna_chains (name, components_json, topology_json, receiver_serial, losses_db, created_at) VALUES (?,?,?,?,?,?)",
                (name, json.dumps(components), json.dumps(topology or {}), receiver_serial, losses_db, datetime.now(timezone.utc).isoformat()),
            )
            c.commit()
            return int(cur.lastrowid)

    def list(self) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM antenna_chains ORDER BY id DESC").fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["components"] = json.loads(d.pop("components_json", "[]") or "[]")
                d["topology"] = json.loads(d.pop("topology_json", "{}") or "{}")
                out.append(d)
            return out

    def get(self, chain_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM antenna_chains WHERE id=?", (chain_id,)).fetchone()
            if not r:
                return None
            d = dict(r)
            d["components"] = json.loads(d.pop("components_json", "[]") or "[]")
            d["topology"] = json.loads(d.pop("topology_json", "{}") or "{}")
            return d

    def update_topology(self, chain_id: int, topology: dict) -> bool:
        with self._conn() as c:
            cur = c.execute("UPDATE antenna_chains SET topology_json=? WHERE id=?", (json.dumps(topology), chain_id))
            c.commit()
            return cur.rowcount > 0

    def delete(self, chain_id: int) -> bool:
        with self._conn() as c:
            cur = c.execute("DELETE FROM antenna_chains WHERE id=?", (chain_id,))
            c.commit()
            return cur.rowcount > 0