from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.api.routers.devices import router as devices_router
from app.api.routers.spectrum import router as spectrum_router

from contextlib import asynccontextmanager

from app.rf.spectrum_worker import (
    SpectrumWorker
)

app = FastAPI(
    title="RF Monitor",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(devices_router)
app.include_router(spectrum_router)

worker = SpectrumWorker()


@asynccontextmanager
async def lifespan(app):

    worker.start()

    yield

    worker.stop()


app = FastAPI(
    title="RF Monitor",
    version="0.1.0",
    lifespan=lifespan,
)