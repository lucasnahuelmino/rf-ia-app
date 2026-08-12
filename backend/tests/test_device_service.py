from app.services.device_service import DeviceService


def test_generate_diagnostic_report(fake_device):
    service = DeviceService(fake_device)

    report = service.get_diagnostic_report()

    assert report["api_version"] == "5.0.9"
    assert report["device_type"] == 2
    assert report["serial_number"] == 123456
    assert report["firmware_version"] == 7

    assert report["temperature"] == 35.5
    assert report["usb_voltage"] == 5.0
    assert report["usb_current"] == 1200