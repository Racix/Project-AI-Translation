import asyncio
import websockets

class WebSocket:
    def __init__(self, websocket_ip, room_id):
        self.uri = f"{websocket_ip}/{room_id}"
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri, ping_interval=None, ping_timeout=None, close_timeout=None)
        # self.websocket = await websockets.connect(self.uri)

    async def send_audio(self, audio=None):
        # print(f"Sending... {len(audio)}", end="")
        try:
            await self.websocket.send(audio)
            # print("Sent")
        except asyncio.CancelledError as e:
            print("Task was cancelled.")
            raise e
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed unexpectedly: {e.code}, {e}")
            print("Reconnecting...")
            await self.connect()
            print("Connected!\n")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise e
            # Handle other unexpected errors

    async def close(self):
        if self.websocket:
            await self.websocket.close()


# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.run_until_complete(send_audio())

