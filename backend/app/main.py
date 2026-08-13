from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.health import router as health_router
from app.api.routers.devices import router as devices_router
from app.api.routers.spectrum import router as spectrum_router
from app.api.routers.ws_spectrum import router as ws_router
from app.api.routers.config import router as config_router
from app.rf.spectrum_worker import SpectrumWorker



worker = SpectrumWorker()


@asynccontextmanager
async def lifespan(app: FastAPI):

    worker.start()

    yield

    worker.stop()


app = FastAPI(
    title="RF Monitor",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(devices_router)
app.include_router(spectrum_router)
app.include_router(config_router)
app.include_router(ws_router)