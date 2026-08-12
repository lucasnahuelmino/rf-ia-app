import asyncio
import websockets
import json


async def main():

    async with websockets.connect(
        "ws://127.0.0.1:8000/ws/spectrum"
    ) as ws:

        while True:

            data = await ws.recv()

            payload = json.loads(data)

            print(
                payload["trace_length"]
            )


asyncio.run(main())