from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

import asyncio

from app.rf.state import spectrum_state

router = APIRouter()


@router.websocket("/ws/spectrum")
async def spectrum_ws(
    websocket: WebSocket,
):
    await websocket.accept()

    try:

        while True:

            with spectrum_state.lock:

                snapshot = (
                    spectrum_state.snapshot
                )

                payload = {
                    "timestamp":
                        snapshot.timestamp,

                    "center_frequency_hz":
                        snapshot.center_frequency_hz,

                    "span_hz":
                        snapshot.span_hz,

                    "start_frequency_hz":
                        snapshot.start_frequency_hz,

                    "stop_frequency_hz":
                        snapshot.stop_frequency_hz,

                    "bin_size_hz":
                        snapshot.bin_size_hz,

                    "trace_length":
                        snapshot.trace_length,

                    "trace":
                        snapshot.trace,
                }

            await websocket.send_json(
                payload
            )

            await asyncio.sleep(0.2)

    except WebSocketDisconnect:
        pass