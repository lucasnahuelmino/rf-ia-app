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
from app.api.routers.audio_live import router as audio_live_router
from app.api.routers.recordings import router as recordings_router
from app.api.routers.sessions import router as sessions_router
from app.api.routers.exports import router as exports_router
from app.api.routers.automation import router as automation_router
from app.api.routers.ollama import router as ollama_router
from app.api.routers.ml import router as ml_router
from app.api.routers.multidevice import router as multidevice_router
from app.api.routers.antennas import router as antennas_router
from app.api.routers.missions import router as missions_router
from app.services.mission_service import MissionService
from app.api.routers.occupation import router as occupation_router
from app.api.routers.gps import router as gps_router
from app.api.routers.geo import router as geo_router
from app.api.routers.spatial import router as spatial_router
from app.api.routers.coverage import router as coverage_router
from app.api.routers.instrument_sessions import router as instrument_sessions_router
from app.api.routers.campaigns import router as campaigns_router
from app.rf.spectrum_worker import SpectrumWorker



worker = SpectrumWorker()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        MissionService().recover_interrupted()
    except Exception:
        pass

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
app.include_router(audio_live_router)
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
app.include_router(gps_router)
app.include_router(geo_router)
app.include_router(spatial_router)
app.include_router(coverage_router)
app.include_router(instrument_sessions_router)
app.include_router(campaigns_router)