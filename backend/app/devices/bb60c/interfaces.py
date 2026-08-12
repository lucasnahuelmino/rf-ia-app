# app/devices/bb60c/interfaces.py

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class DeviceDiagnostics:
    temperature: float
    usb_voltage: float
    usb_current: float


@dataclass(slots=True)
class DeviceInfo:
    device_type: int
    serial_number: int
    firmware_version: int


class RFDevice(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def get_device_info(self) -> DeviceInfo:
        pass

    @abstractmethod
    def get_diagnostics(self) -> DeviceDiagnostics:
        pass