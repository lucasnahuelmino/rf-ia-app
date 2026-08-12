# app/devices/bb60c/diagnostics.py

from __future__ import annotations

from .adapter import BB60CAdapter


DEVICE_TYPES = {
    0: "NONE",
    1: "BB60A",
    2: "BB60C",
    3: "BB60D",
}


def main() -> None:
    print()
    print("RF Monitor - BB60C Diagnostic")
    print("-" * 40)

    adapter = BB60CAdapter()

    try:
        print(f"API Version : {adapter.get_api_version()}")
        print(f"Product ID  : {adapter.get_product_id()}")
        print()

        print("Opening device...")
        adapter.connect()

        info = adapter.get_device_info()
        diag = adapter.get_diagnostics()

        print("Device Information")
        print("------------------")
        print(
            f"Device Type   : "
            f"{DEVICE_TYPES.get(info.device_type, info.device_type)}"
        )
        print(f"Serial Number : {info.serial_number}")
        print(f"Firmware      : {info.firmware_version}")

        print()

        print("Diagnostics")
        print("-----------")
        print(f"Temperature : {diag.temperature:.2f} °C")
        print(f"USB Voltage : {diag.usb_voltage:.2f} V")
        print(f"USB Current : {diag.usb_current:.2f}")

        print()
        print("Status: OK")

    except Exception as exc:
        print()
        print(f"ERROR: {exc}")

    finally:
        adapter.disconnect()
        print()
        print("Device closed successfully.")


if __name__ == "__main__":
    main()