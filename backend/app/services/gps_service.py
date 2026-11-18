from __future__ import annotations

import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import serial
from serial.tools import list_ports

from app.gps.nmea import GPSPosition, parse_nmea


def db_path() -> str:
    d = os.environ.get("RF_DB_DIR", os.path.join(os.getcwd(), "data"))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "rf_monitor.db")


class GPSService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._positions: List[GPSPosition] = []
        self._connected = False
        self._simulated = False
        self._serial = None
        self._port = None
        self._baudrate = 9600
        self._sim_index = 0
        self._sim_route = self._default_route()
        self._last_position: Optional[GPSPosition] = None
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(db_path()) as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS gps_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    latitude REAL,
                    longitude REAL,
                    altitude REAL,
                    speed_knots REAL,
                    course REAL,
                    satellites INTEGER,
                    fix_quality INTEGER,
                    valid INTEGER,
                    source TEXT,
                    port TEXT,
                    session_id INTEGER,
                    mission_id INTEGER
                )
                """
            )
            c.commit()

    def _default_route(self) -> List[GPSPosition]:
        # Buenos Aires-ish small route
        base_lat = -34.6037
        base_lon = -58.3816
        route = []
        for i in range(100):
            route.append(
                GPSPosition(
                    latitude=base_lat + i * 0.0001,
                    longitude=base_lon + i * 0.0001,
                    altitude=20.0,
                    speed_knots=30.0,
                    course=45.0,
                    satellites=8,
                    fix_quality=1,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    valid=True,
                )
            )
        return route

    def list_ports(self) -> List[Dict[str, str]]:
        return [{"device": p.device, "description": p.description, "hwid": p.hwid} for p in list_ports.comports()]

    def connect_simulated(self) -> None:
        with self._lock:
            self._disconnect_internal()
            self._simulated = True
            self._connected = True
            self._port = "SIMULATED"

    def connect_serial(self, port: str, baudrate: int = 9600) -> None:
        with self._lock:
            self._disconnect_internal()
            ser = serial.Serial(port, baudrate, timeout=1)
            self._serial = ser
            self._port = port
            self._baudrate = baudrate
            self._simulated = False
            self._connected = True

    def _disconnect_internal(self) -> None:
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
        self._serial = None
        self._connected = False
        self._simulated = False
        self._port = None

    def disconnect(self) -> None:
        with self._lock:
            self._disconnect_internal()

    def status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "connected": self._connected,
                "simulated": self._simulated,
                "port": self._port,
                "last_position": self._last_position.__dict__ if self._last_position else None,
            }

    def read_position(self) -> Optional[GPSPosition]:
        with self._lock:
            if not self._connected:
                return None
            if self._simulated:
                pos = self._sim_route[self._sim_index % len(self._sim_route)]
                self._sim_index += 1
                pos.timestamp = datetime.now(timezone.utc).isoformat()
                self._last_position = pos
                self._persist(pos, "SIMULATED")
                return pos

            # Serial
            if self._serial is None:
                return None
            try:
                line = self._serial.readline().decode("ascii", errors="ignore")
            except Exception:
                return None
            pos = parse_nmea(line)
            if pos is not None:
                self._last_position = pos
                self._persist(pos, "SERIAL")
            return pos

    def _persist(self, pos: GPSPosition, source: str) -> None:
        with sqlite3.connect(db_path()) as c:
            c.execute(
                "INSERT INTO gps_positions (timestamp, latitude, longitude, altitude, speed_knots, course, satellites, fix_quality, valid, source, port) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (pos.timestamp, pos.latitude, pos.longitude, pos.altitude, pos.speed_knots, pos.course, pos.satellites, pos.fix_quality, int(pos.valid), source, self._port),
            )
            c.commit()

    def history(self, limit: int = 100) -> List[Dict[str, Any]]:
        with sqlite3.connect(db_path()) as c:
            c.row_factory = sqlite3.Row
            rows = c.execute("SELECT * FROM gps_positions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]