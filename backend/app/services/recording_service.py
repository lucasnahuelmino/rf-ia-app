from __future__ import annotations

import json
import os
from typing import List


def data_dir() -> str:
    return os.environ.get(
        "RF_DATA_DIR",
        os.path.join(os.getcwd(), "data", "recordings"),
    )


class RecordingService:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = base_dir or data_dir()
        os.makedirs(self.base_dir, exist_ok=True)

    def list_recordings(self) -> List[dict]:
        items = []
        for name in sorted(os.listdir(self.base_dir)):
            path = os.path.join(self.base_dir, name)
            if not os.path.isfile(path):
                continue
            stat = os.stat(path)
            meta = None
            if name.endswith(".json"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except Exception:
                    meta = None
            items.append(
                {
                    "name": name,
                    "path": path,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "metadata": meta,
                }
            )
        return items

    def delete(self, filename: str) -> bool:
        # Prevent path traversal.
        safe_name = os.path.basename(filename)
        path = os.path.join(self.base_dir, safe_name)
        if not os.path.exists(path):
            return False
        os.remove(path)
        # Remove sidecar metadata if present.
        sidecar = os.path.splitext(path)[0] + ".json"
        if os.path.exists(sidecar) and sidecar != path:
            try:
                os.remove(sidecar)
            except OSError:
                pass
        return True