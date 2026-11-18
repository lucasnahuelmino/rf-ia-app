from __future__ import annotations

from fastapi import APIRouter

from app.services.automation_service import AutomationService, AutomationTask
from app.services.session_service import SessionService

router = APIRouter()
_service = AutomationService(SessionService())


@router.get("/automation/tasks")
def list_tasks():
    return {"items": _service.list_tasks()}


@router.post("/automation/tasks")
def create_task(task: dict):
    t = AutomationTask(**task)
    _service.add_task(t)
    return {"status": "created", "id": t.id}


@router.post("/automation/tasks/{task_id}/enable")
def enable_task(task_id: str, enabled: bool = True):
    _service.set_enabled(task_id, enabled)
    return {"status": "ok"}


@router.delete("/automation/tasks/{task_id}")
def delete_task(task_id: str):
    _service.remove_task(task_id)
    return {"status": "deleted"}


@router.post("/automation/start")
def start_automation():
    _service.start()
    return {"status": "started"}


@router.post("/automation/stop")
def stop_automation():
    _service.stop()
    return {"status": "stopped"}