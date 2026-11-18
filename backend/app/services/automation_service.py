from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from app.rf.state import spectrum_state
from app.services.session_service import SessionService


@dataclass
class AutomationTask:
    id: str
    name: str
    enabled: bool = True
    threshold_dbm: float = -60.0
    duration_seconds: float = 1.0
    interval_seconds: float = 5.0
    action: str = "log"  # log | capture | record_iq
    session_id: Optional[int] = None
    last_run: float = 0.0
    run_count: int = 0
    history: List[Dict] = field(default_factory=list)


class AutomationService:
    def __init__(self, session_service: SessionService | None = None) -> None:
        self._tasks: Dict[str, AutomationTask] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.session_service = session_service or SessionService()

    def add_task(self, task: AutomationTask) -> None:
        with self._lock:
            self._tasks[task.id] = task

    def remove_task(self, task_id: str) -> None:
        with self._lock:
            self._tasks.pop(task_id, None)

    def list_tasks(self) -> List[Dict]:
        with self._lock:
            return [t.__dict__.copy() for t in self._tasks.values()]

    def set_enabled(self, task_id: str, enabled: bool) -> None:
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].enabled = enabled

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        while self._running:
            now = time.time()
            with self._lock:
                tasks = list(self._tasks.values())

            for task in tasks:
                if not task.enabled:
                    continue
                if now - task.last_run < task.interval_seconds:
                    continue

                with spectrum_state.lock:
                    snap = spectrum_state.snapshot
                    trace = snap.trace or []

                if not trace:
                    continue

                peak = max(trace)
                if peak >= task.threshold_dbm:
                    task.last_run = now
                    task.run_count += 1
                    event = {
                        "time": now,
                        "peak_dbm": peak,
                        "threshold": task.threshold_dbm,
                        "action": task.action,
                    }
                    task.history.append(event)
                    self.session_service.add_event(
                        task.session_id,
                        "warning",
                        f"Threshold exceeded: {peak:.2f} dBm >= {task.threshold_dbm} dBm",
                        event,
                    )

            time.sleep(1.0)