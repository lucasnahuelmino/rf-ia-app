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

                payload = {
                    "trace_length":
                        spectrum_state.trace_length,

                    "bin_size_hz":
                        spectrum_state.bin_size_hz,

                    "start_frequency_hz":
                        spectrum_state.start_frequency_hz,

                    "trace":
                        spectrum_state.trace,
                }

            await websocket.send_json(
                payload
            )

            await asyncio.sleep(0.2)

    except WebSocketDisconnect:
        pass