import asyncio
import websockets

websocket_ip = "wss://socketsbay.com/wss/v2/1/demo/"

async def send_audio():
    async with websockets.connect(websocket_ip) as websocket:
        await websocket.send("audio")

# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.run_until_complete(send_audio())
