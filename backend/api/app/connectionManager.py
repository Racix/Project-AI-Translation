from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = defaultdict(dict)

    async def connect(self, websocket: WebSocket, media_id: str):
        await websocket.accept()
        if self.connections[media_id] == {} or len(self.connections[media_id]) == 0:
            self.connections[media_id] = []
        self.connections[media_id].append(websocket)

    def disconnect(self, websocket: WebSocket, media_id: str):
        self.connections[media_id].remove(websocket)

    async def broadcast(self, message: str, media_id: str):
        for connection in self.connections[media_id]:
            await connection.send_json(message)