from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from app.devices.bb60c.adapter import BB60CAdapter
from app.devices.bb60c.sdk import bb_api


@dataclass
class ReceiverInfo:
    serial_number: int
    device_type: int
    firmware_version: int
    alias: str = ""
    state: str = "DISCONNECTED"  # DISCONNECTED/CONNECTED/ACQUIRING/ERROR
    last_seen: float = 0.0
    last_used: float = 0.0
    adapter: Optional[BB60CAdapter] = None
    connection_history: List[dict] = field(default_factory=list)


class MultiDeviceManager:
    """Manage multiple BB60C receivers by serial number."""

    def __init__(self, factory: Callable[[], BB60CAdapter] = BB60CAdapter) -> None:
        self._factory = factory
        self._lock = threading.RLock()
        self._receivers: Dict[int, ReceiverInfo] = {}

    def discover(self) -> List[ReceiverInfo]:
        """Detect connected devices using SDK list function."""
        try:
            result = bb_api.bb_get_serial_number_list_2()
            serials = result.get("serials")
            types = result.get("device_types")
            count = result.get("device_count", 0)
        except Exception:
            serials, types, count = [], [], 0

        found: List[ReceiverInfo] = []
        if serials is not None and count:
            for i in range(min(count, len(serials))):
                sn = int(serials[i])
                dt = int(types[i]) if types is not None and i < len(types) else 0
                with self._lock:
                    if sn not in self._receivers:
                        self._receivers[sn] = ReceiverInfo(
                            serial_number=sn,
                            device_type=dt,
                            firmware_version=0,
                            last_seen=time.time(),
                        )
                    else:
                        self._receivers[sn].device_type = dt
                        self._receivers[sn].last_seen = time.time()
                    found.append(self._receivers[sn])
        return found

    def list_receivers(self) -> List[ReceiverInfo]:
        with self._lock:
            return list(self._receivers.values())

    def get(self, serial_number: int) -> Optional[ReceiverInfo]:
        with self._lock:
            return self._receivers.get(serial_number)

    def set_alias(self, serial_number: int, alias: str) -> None:
        with self._lock:
            if serial_number in self._receivers:
                self._receivers[serial_number].alias = alias

    def connect(self, serial_number: int) -> ReceiverInfo:
        with self._lock:
            info = self._receivers.get(serial_number)
            if info is None:
                info = ReceiverInfo(serial_number=serial_number, device_type=0, firmware_version=0)
                self._receivers[serial_number] = info

            if info.adapter is None:
                info.state = "CONNECTING"
                adapter = self._factory()
                try:
                    # Prefer open by serial if adapter supports it; fallback to generic connect.
                    try:
                        bb_api.bb_open_device_by_serial_number(serial_number)
                    except Exception:
                        pass
                    adapter.connect()
                    info.adapter = adapter
                    try:
                        info.firmware_version = adapter.get_firmware_version() if hasattr(adapter, "get_firmware_version") else info.firmware_version
                    except Exception:
                        pass
                    info.state = "CONNECTED"
                    info.connection_history.append({"time": time.time(), "event": "connected"})
                except Exception as exc:
                    info.state = "ERROR"
                    info.connection_history.append({"time": time.time(), "event": "error", "detail": str(exc)})
                    raise
            info.last_used = time.time()
            return info

    def disconnect(self, serial_number: int) -> None:
        with self._lock:
            info = self._receivers.get(serial_number)
            if info is None:
                return
            if info.adapter is not None:
                try:
                    info.adapter.disconnect()
                except Exception:
                    pass
                info.adapter = None
            info.state = "DISCONNECTED"
            info.connection_history.append({"time": time.time(), "event": "disconnected"})

    def set_state(self, serial_number: int, state: str) -> None:
        with self._lock:
            info = self._receivers.get(serial_number)
            if info is not None:
                info.state = state

    def acquire(self, serial_number: int) -> Optional[BB60CAdapter]:
        info = self.connect(serial_number)
        info.state = "ACQUIRING"
        return info.adapter