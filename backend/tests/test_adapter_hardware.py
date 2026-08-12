import pytest

from app.devices.bb60c.adapter import BB60CAdapter


@pytest.mark.hardware
def test_connect_and_disconnect_real_device():
    adapter = BB60CAdapter()

    adapter.connect()

    try:
        info = adapter.get_device_info()

        assert info.serial_number > 0

    finally:
        adapter.disconnect()