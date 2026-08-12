from __future__ import annotations

from app.devices.bb60c.adapter import BB60CAdapter


class DeviceService:
    """
    Application service layer.

    El resto de la aplicación utiliza esta clase y no accede
    directamente al SDK ni al adapter.
    """

    def __init__(self, device: BB60CAdapter | None = None) -> None:
        self._device = device or BB60CAdapter()

    def get_diagnostic_report(self) -> dict:
        self._device.connect()

        try:
            info = self._device.get_device_info()
            diag = self._device.get_diagnostics()

            return {
                "api_version": self._device.get_api_version(),
                "product_id": self._device.get_product_id(),
                "device_type": info.device_type,
                "serial_number": info.serial_number,
                "firmware_version": info.firmware_version,
                "temperature": diag.temperature,
                "usb_voltage": diag.usb_voltage,
                "usb_current": diag.usb_current,
            }

        finally:
            self._device.disconnect()