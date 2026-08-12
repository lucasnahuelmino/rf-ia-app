import pytest

from app.devices.bb60c.interfaces import (
    DeviceDiagnostics,
    DeviceInfo,
)


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


@pytest.fixture
def fake_device():
    return FakeBB60C()