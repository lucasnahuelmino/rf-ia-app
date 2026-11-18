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


class SessionService:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or db_path()
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    created_at TEXT,
                    center_frequency_hz REAL,
                    span_hz REAL,
                    config_json TEXT,
                    notes TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS captures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    type TEXT,
                    filename TEXT,
                    created_at TEXT,
                    metadata_json TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    created_at TEXT,
                    level TEXT,
                    message TEXT,
                    metadata_json TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
                """
            )
            conn.commit()

    def create_session(self, name: str, config: Dict[str, Any] | None = None, notes: str = "") -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO sessions (name, created_at, center_frequency_hz, span_hz, config_json, notes) VALUES (?,?,?,?,?,?)",
                (
                    name,
                    datetime.now(timezone.utc).isoformat(),
                    (config or {}).get("center_frequency_hz"),
                    (config or {}).get("span_hz"),
                    json.dumps(config or {}),
                    notes,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_sessions(self) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM sessions ORDER BY id DESC").fetchall()
            return [dict(r) for r in rows]

    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
            return dict(row) if row else None

    def add_capture(self, session_id: int, ctype: str, filename: str, metadata: Dict[str, Any] | None = None) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO captures (session_id, type, filename, created_at, metadata_json) VALUES (?,?,?,?,?)",
                (session_id, ctype, filename, datetime.now(timezone.utc).isoformat(), json.dumps(metadata or {})),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_captures(self, session_id: int | None = None) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            if session_id is None:
                rows = conn.execute("SELECT * FROM captures ORDER BY id DESC").fetchall()
            else:
                rows = conn.execute("SELECT * FROM captures WHERE session_id=? ORDER BY id DESC", (session_id,)).fetchall()
            return [dict(r) for r in rows]

    def add_event(self, session_id: int | None, level: str, message: str, metadata: Dict[str, Any] | None = None) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO events (session_id, created_at, level, message, metadata_json) VALUES (?,?,?,?,?)",
                (session_id, datetime.now(timezone.utc).isoformat(), level, message, json.dumps(metadata or {})),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_events(self, session_id: int | None = None) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            if session_id is None:
                rows = conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT 200").fetchall()
            else:
                rows = conn.execute("SELECT * FROM events WHERE session_id=? ORDER BY id DESC", (session_id,)).fetchall()
            return [dict(r) for r in rows]