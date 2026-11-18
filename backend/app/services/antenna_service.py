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
                    receiver_serial INTEGER,
                    losses_db REAL,
                    created_at TEXT
                )
                """
            )
            c.commit()

    def create(self, name: str, components: List[str], receiver_serial: Optional[int] = None, losses_db: float = 0.0) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO antenna_chains (name, components_json, receiver_serial, losses_db, created_at) VALUES (?,?,?,?,?)",
                (name, json.dumps(components), receiver_serial, losses_db, datetime.now(timezone.utc).isoformat()),
            )
            c.commit()
            return int(cur.lastrowid)

    def list(self) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM antenna_chains ORDER BY id DESC").fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["components"] = json.loads(d.pop("components_json", "[]"))
                out.append(d)
            return out

    def get(self, chain_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM antenna_chains WHERE id=?", (chain_id,)).fetchone()
            if not r:
                return None
            d = dict(r)
            d["components"] = json.loads(d.pop("components_json", "[]"))
            return d

    def delete(self, chain_id: int) -> bool:
        with self._conn() as c:
            cur = c.execute("DELETE FROM antenna_chains WHERE id=?", (chain_id,))
            c.commit()
            return cur.rowcount > 0