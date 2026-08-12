from __future__ import annotations

from typing import Optional

from .exceptions import (
    BB60CConnectionError,
    BB60CDeviceNotFoundError,
    BB60CSDKError,
)
from .interfaces import DeviceDiagnostics, DeviceInfo, RFDevice
from .models import (
    SweepConfiguration,
    TraceData,
    TraceInfo,
)

from .sdk import bb_api


class BB60CAdapter(RFDevice):
    def __init__(self) -> None:
        self._handle: Optional[int] = None

    @property
    def handle(self) -> int:
        if self._handle is None:
            raise BB60CConnectionError(
                "Device is not connected."
            )

        return self._handle

    def _check_status(self, result: dict) -> None:
        status = result.get("status")

        if status is None:
            return

        if status != 0:
            raise BB60CSDKError(
                f"SDK returned status={status}"
            )

    # =====================================================
    # Connection
    # =====================================================

    def connect(self) -> None:
        result = bb_api.bb_open_device()

        self._check_status(result)

        handle = result.get("handle")

        if handle is None or handle < 0:
            raise BB60CDeviceNotFoundError(
                "No BB60C device found."
            )

        self._handle = handle

    def disconnect(self) -> None:
        if self._handle is None:
            return

        try:
            result = bb_api.bb_close_device(
                self._handle
            )

            self._check_status(result)

        finally:
            self._handle = None

    # =====================================================
    # Device Information
    # =====================================================

    def get_api_version(self) -> str:
        result = bb_api.bb_get_API_version()

        value = result["api_version"]

        if isinstance(value, bytes):
            return value.decode("utf-8")

        return str(value)

    def get_product_id(self) -> str:
        result = bb_api.bb_get_product_ID()

        value = result["product_id"]

        if isinstance(value, bytes):
            return value.decode("utf-8")

        return str(value)

    def get_device_info(self) -> DeviceInfo:
        device_type = bb_api.bb_get_device_type(
            self.handle
        )

        serial = bb_api.bb_get_serial_number(
            self.handle
        )

        firmware = bb_api.bb_get_firmware_version(
            self.handle
        )

        self._check_status(device_type)
        self._check_status(serial)
        self._check_status(firmware)

        return DeviceInfo(
            device_type=device_type["device_type"],
            serial_number=serial["serial"],
            firmware_version=firmware["version"],
        )

    def get_diagnostics(
        self,
    ) -> DeviceDiagnostics:

        result = bb_api.bb_get_device_diagnostics(
            self.handle
        )

        self._check_status(result)

        return DeviceDiagnostics(
            temperature=result["temperature"],
            usb_voltage=result["usb_voltage"],
            usb_current=result["usb_current"],
        )

    # =====================================================
    # Sweep Configuration
    # =====================================================

    def configure_sweep(
        self,
        config: SweepConfiguration,
    ) -> None:

        result = bb_api.bb_configure_ref_level(
            self.handle,
            config.reference_level_dbm,
        )
        self._check_status(result)

        result = bb_api.bb_configure_center_span(
            self.handle,
            config.center_frequency_hz,
            config.span_hz,
        )
        self._check_status(result)

        result = bb_api.bb_configure_sweep_coupling(
            self.handle,
            config.rbw_hz,
            config.vbw_hz,
            0.0,
            bb_api.BB_RBW_SHAPE_NUTTALL,
            bb_api.BB_NO_SPUR_REJECT,
        )
        self._check_status(result)

        result = bb_api.bb_configure_acquisition(
            self.handle,
            bb_api.BB_AVERAGE,
            bb_api.BB_LOG_SCALE,
        )
        self._check_status(result)

    # =====================================================
    # Sweep Runtime
    # =====================================================

    def start_sweep(self) -> None:

        result = bb_api.bb_initiate(
            self.handle,
            bb_api.BB_SWEEPING,
            0,
        )

        self._check_status(result)

    def get_trace(self) -> TraceData:

        info_result = bb_api.bb_query_trace_info(
            self.handle
        )

        self._check_status(info_result)

        trace_length = info_result["trace_len"]

        trace_result = bb_api.bb_fetch_trace(
            self.handle,
            trace_length,
        )

        self._check_status(trace_result)

        info = TraceInfo(
            trace_length=trace_length,
            bin_size_hz=info_result["bin_size"],
            start_frequency_hz=info_result["start"],
        )

        return TraceData(
            trace_min=trace_result["trace_min"],
            trace_max=trace_result["trace_max"],
            info=info,
        )