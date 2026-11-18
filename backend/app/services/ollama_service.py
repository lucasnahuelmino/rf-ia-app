from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, List, Optional


class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")

    def status(self) -> Dict[str, Any]:
        try:
            with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=3) as resp:
                data = json.loads(resp.read().decode())
            models = [m.get("name") for m in data.get("models", [])]
            return {"available": True, "models": models}
        except Exception as exc:
            return {"available": False, "models": [], "error": str(exc)}

    def generate(self, model: str, prompt: str, system: str | None = None) -> Dict[str, Any]:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
            return {"ok": True, "response": data.get("response", "")}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def chat_with_tools(self, model: str, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        # Ollama tool calling is model-dependent; keep a safe text fallback.
        prompt = "\n".join(m.get("content", "") for m in messages)
        return self.generate(model, prompt)