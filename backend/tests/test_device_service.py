from app.devices.bb60c.interfaces import (
    DeviceDiagnostics,
    DeviceInfo,
)
from app.services.device_manager import DeviceManager
from app.services.device_service import DeviceService


class FakeBB60C:
    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_api_version(self):
        return "5.0.9"

    def get_product_id(self):
        return "4308-1101"

    def get_device_info(self):
        return DeviceInfo(
            device_type=2,
            serial_number=123456,
            firmware_version=7,
        )

    def get_diagnostics(self):
        return DeviceDiagnostics(
            temperature=35.5,
            usb_voltage=5.0,
            usb_current=1200,
        )


def test_generate_diagnostic_report():
    manager = DeviceManager(FakeBB60C)
    service = DeviceService(manager)

    report = service.get_diagnostics()

    assert report["api_version"] == "5.0.9"
    assert report["device_type"] == 2
    assert report["serial_number"] == 123456
    assert report["firmware_version"] == 7
    assert report["temperature"] == 35.5
    assert report["usb_voltage"] == 5.0
    assert report["usb_current"] == 1200
    assert report["state"] == "CONNECTED"