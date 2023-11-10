import asyncio
import websockets

# websocket_ip = "wss://socketsbay.com/wss/v2/1/demo/"
websocket_ip = "ws://130.240.200.128:8080/ws/live-transcription/hej"

async def send_audio(audio=None):
    async with websockets.connect(websocket_ip) as websocket:
        await websocket.send(audio)


# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.run_until_complete(send_audio())
