from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ollama_service import OllamaService

router = APIRouter()
_service = OllamaService()


class GenerateRequest(BaseModel):
    model: str
    prompt: str
    system: str | None = None


@router.get("/ollama/status")
def ollama_status():
    return _service.status()


@router.post("/ollama/generate")
def ollama_generate(payload: GenerateRequest):
    return _service.generate(payload.model, payload.prompt, payload.system)