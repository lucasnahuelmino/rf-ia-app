from fastapi import APIRouter

from app.services.spectrum_service import SpectrumService

router = APIRouter()

service = SpectrumService()


@router.get("/spectrum/current")
def current_spectrum():
    return service.get_current_spectrum()