"""Centralized, thread-safe manager for the single BB60C session."""

from __future__ import annotations

import threading
from enum import Enum
from typing import Callable, Optional

from app.devices.bb60c.adapter import BB60CAdapter
from app.devices.bb60c.exceptions import (
    BB60CConnectionError,
)
from app.devices.bb60c.interfaces import (
    DeviceDiagnostics,
    DeviceInfo,
)
from app.devices.bb60c.models import (
    SweepConfiguration,
    TraceData,
)


class DeviceState(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    ACQUIRING = "ACQUIRING"
    ERROR = "ERROR"


class DeviceManager:
    """Owns the only BB60C adapter instance used by the application."""

    def __init__(
        self,
        factory: Callable[[], BB60CAdapter] = BB60CAdapter,
    ) -> None:
        self._factory = factory
        self._lock = threading.RLock()
        self._adapter = None
        self._state = DeviceState.DISCONNECTED
        self._ref_count = 0
        self._last_error: Optional[str] = None

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    @property
    def state(self) -> DeviceState:
        with self._lock:
            return self._state

    @property
    def last_error(self) -> Optional[str]:
        with self._lock:
            return self._last_error

    @property
    def is_connected(self) -> bool:
        with self._lock:
            return self._adapter is not None

    @property
    def ref_count(self) -> int:
        with self._lock:
            return self._ref_count

    # ---------------------------------------------------------
    # Connection
    # ---------------------------------------------------------

    def connect(self):
        with self._lock:
            if self._adapter is None:
                self._state = DeviceState.CONNECTING
                try:
                    adapter = self._factory()
                    adapter.connect()
                    self._adapter = adapter
                    self._state = DeviceState.CONNECTED
                    self._last_error = None
                except Exception as exc:
                    self._state = DeviceState.ERROR
                    self._last_error = str(exc)
                    raise

            self._ref_count += 1
            return self._adapter

    def disconnect(self) -> None:
        with self._lock:
            if self._ref_count > 0:
                self._ref_count -= 1

            if self._ref_count == 0 and self._adapter is not None:
                try:
                    self._adapter.disconnect()
                except Exception as exc:  # pragma: no cover - defensive
                    self._last_error = str(exc)
                finally:
                    self._adapter = None
                    self._state = DeviceState.DISCONNECTED

    def force_disconnect(self) -> None:
        with self._lock:
            if self._adapter is not None:
                try:
                    self._adapter.disconnect()
                except Exception as exc:  # pragma: no cover - defensive
                    self._last_error = str(exc)
                finally:
                    self._adapter = None
                    self._ref_count = 0
                    self._state = DeviceState.DISCONNECTED

    def reconnect(self):
        self.force_disconnect()
        return self.connect()

    def set_acquiring(self, value: bool) -> None:
        with self._lock:
            if self._adapter is None:
                return
            self._state = (
                DeviceState.ACQUIRING
                if value
                else DeviceState.CONNECTED
            )

    @property
    def device(self):
        with self._lock:
            if self._adapter is None:
                raise BB60CConnectionError(
                    "Device is not connected."
                )
            return self._adapter

    # ---------------------------------------------------------
    # Delegated operations
    # ---------------------------------------------------------

    def configure_sweep(self, config: SweepConfiguration) -> None:
        self.device.configure_sweep(config)

    def start_sweep(self) -> None:
        self.device.start_sweep()

    def get_trace(self) -> TraceData:
        return self.device.get_trace()

    def get_device_info(self) -> DeviceInfo:
        return self.device.get_device_info()

    def get_diagnostics(self) -> DeviceDiagnostics:
        return self.device.get_diagnostics()

    def get_api_version(self) -> str:
        return self.device.get_api_version()

    def get_product_id(self) -> str:
        return self.device.get_product_id()


# Single shared instance used by the application.
device_manager = DeviceManager()