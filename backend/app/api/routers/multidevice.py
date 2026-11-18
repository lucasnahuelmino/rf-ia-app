from __future__ import annotations

from fastapi import APIRouter

from app.devices.bb60c.multi_device import MultiDeviceManager

router = APIRouter()
_manager = MultiDeviceManager()


@router.get("/devices/multi/discover")
def discover():
    infos = _manager.discover()
    return {"items": [i.__dict__ for i in infos if not hasattr(i, "adapter") or True]}


@router.get("/devices/multi")
def list_devices():
    infos = _manager.list_receivers()
    return {"items": [{"serial_number": i.serial_number, "device_type": i.device_type, "firmware_version": i.firmware_version, "alias": i.alias, "state": i.state, "last_seen": i.last_seen, "last_used": i.last_used} for i in infos]}


@router.post("/devices/multi/{serial}/alias")
def set_alias(serial: int, alias: str):
    _manager.set_alias(serial, alias)
    return {"status": "ok"}


@router.post("/devices/multi/{serial}/connect")
def connect(serial: int):
    info = _manager.connect(serial)
    return {"serial_number": info.serial_number, "state": info.state}


@router.post("/devices/multi/{serial}/disconnect")
def disconnect(serial: int):
    _manager.disconnect(serial)
    return {"status": "ok"}