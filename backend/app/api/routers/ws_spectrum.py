from __future__ import annotations

import asyncio

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.rf.state import spectrum_state

router = APIRouter()


@router.websocket("/ws/spectrum")
async def spectrum_ws(websocket: WebSocket) -> None:
    await websocket.accept()

    last_timestamp = None

    try:
        while True:
            with spectrum_state.lock:
                snapshot = spectrum_state.snapshot

                payload = {
                    "timestamp": snapshot.timestamp,
                    "center_frequency_hz": snapshot.center_frequency_hz,
                    "span_hz": snapshot.span_hz,
                    "start_frequency_hz": snapshot.start_frequency_hz,
                    "stop_frequency_hz": snapshot.stop_frequency_hz,
                    "bin_size_hz": snapshot.bin_size_hz,
                    "trace_length": snapshot.trace_length,
                    "trace": snapshot.trace,
                    "trace_min": snapshot.trace_min,
                    "trace_max": snapshot.trace_max,
                    "config_version": snapshot.config_version,
                }

                current_timestamp = snapshot.timestamp

            if (
                snapshot.trace is not None
                and current_timestamp != last_timestamp
            ):
                await websocket.send_json(payload)
                last_timestamp = current_timestamp

            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        pass