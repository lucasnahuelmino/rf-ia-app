from __future__ import annotations

from typing import Optional

from app.services.device_manager import (
    DeviceManager,
    device_manager,
)


class DeviceService:
    """Expose device diagnostics through the centralized manager."""

    def __init__(
        self,
        manager: Optional[DeviceManager] = None,
    ) -> None:
        self._manager = manager or device_manager

    def get_diagnostics(self) -> dict:
        self._manager.connect()

        try:
            info = self._manager.get_device_info()
            diag = self._manager.get_diagnostics()

            return {
                "api_version": self._manager.get_api_version(),
                "product_id": self._manager.get_product_id(),
                "device_type": info.device_type,
                "serial_number": info.serial_number,
                "firmware_version": info.firmware_version,
                "temperature": diag.temperature,
                "usb_voltage": diag.usb_voltage,
                "usb_current": diag.usb_current,
                "state": self._manager.state.value,
            }

        finally:
            self._manager.disconnect()