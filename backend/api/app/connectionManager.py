from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = defaultdict(dict)

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if self.connections[room_id] == {} or len(self.connections[room_id]) == 0:
            self.connections[room_id] = []
        self.connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        self.connections[room_id].remove(websocket)

    async def broadcast(self, message: str, room_id: str):
        for connection in self.connections[room_id]:
            await connection.send_json(message)