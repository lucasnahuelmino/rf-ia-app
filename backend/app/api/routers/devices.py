from fastapi import APIRouter

from app.services.device_service import DeviceService

router = APIRouter()

service = DeviceService()


@router.get("/devices/bb60c/diagnostics")
def diagnostics():
    return service.get_diagnostics()