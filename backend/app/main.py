from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.health import router as health_router
from app.api.routers.devices import router as devices_router
from app.api.routers.spectrum import router as spectrum_router
from app.api.routers.ws_spectrum import router as ws_router
from app.api.routers.config import router as config_router
from app.api.routers.iq import router as iq_router
from app.api.routers.demod import router as demod_router
from app.api.routers.audio import router as audio_router
from app.api.routers.recordings import router as recordings_router
from app.api.routers.sessions import router as sessions_router
from app.api.routers.exports import router as exports_router
from app.api.routers.automation import router as automation_router
from app.api.routers.ollama import router as ollama_router
from app.api.routers.ml import router as ml_router
from app.api.routers.multidevice import router as multidevice_router
from app.api.routers.antennas import router as antennas_router
from app.api.routers.missions import router as missions_router
from app.api.routers.occupation import router as occupation_router
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
app.include_router(iq_router)
app.include_router(demod_router)
app.include_router(audio_router)
app.include_router(recordings_router)
app.include_router(sessions_router)
app.include_router(exports_router)
app.include_router(automation_router)
app.include_router(ollama_router)
app.include_router(ml_router)
app.include_router(multidevice_router)
app.include_router(antennas_router)
app.include_router(missions_router)
app.include_router(occupation_router)