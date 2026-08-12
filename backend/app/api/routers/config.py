from fastapi import APIRouter

from app.schemas.spectrum import (
    SpectrumConfigUpdate,
)

from app.services.config_service import (
    ConfigService,
)

router = APIRouter()

service = ConfigService()


@router.get("/spectrum/config")
def get_config():

    return service.get_config()


@router.post("/spectrum/config")
def update_config(
    config: SpectrumConfigUpdate,
):

    return service.update_config(
        config
    )