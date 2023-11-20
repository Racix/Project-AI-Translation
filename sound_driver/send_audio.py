import asyncio
import websockets

# websocket_ip = "wss://socketsbay.com/wss/v2/1/demo/"
websocket_ip = "ws://130.240.200.127:8080/ws/live-transcription/hej"

class WebSocket:
    def __init__(self):
        self.uri = websocket_ip  # WebSocket server address
        self.websocket = None

    async def connect(self):
        print("Connecting ws...")
        self.websocket = await websockets.connect(self.uri)
        print("Connected ws")

    async def send_audio(self, audio=None):
        print(f"Sending... {len(audio)}", end="")
        try:
            await self.websocket.send(audio)
            print("Sent")
        except asyncio.CancelledError:
            print("Task was cancelled.")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed unexpectedly: {e.code}, {e.reason}")
            await self.connect()
        except Exception as e:
            print(f"Unexpected error: {e}")
            # Handle other unexpected errors

    async def close(self):
        if self.websocket:
            await self.websocket.close()


# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.run_until_complete(send_audio())

