from app.devices.bb60c.adapter import BB60CAdapter


class DeviceService:

    def __init__(self):
        self._device = BB60CAdapter()

    def get_diagnostics(self):

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