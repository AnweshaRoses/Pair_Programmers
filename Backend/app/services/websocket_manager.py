from fastapi import WebSocket
from typing import Dict, Set


class WebSocketManager:
    """
    Tracks room states, connected clients, and manages broadcasting.
    """

    def __init__(self):
        self.rooms: Dict[str, Dict] = {}  
        # rooms[room_id] = {"code": "...", "clients": set(WebSocket)}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()

        if room_id not in self.rooms:
            self.rooms[room_id] = {"code": "", "clients": set()}

        # Limit 2 users
        if len(self.rooms[room_id]["clients"]) >= 2:
            await websocket.close()
            return

        self.rooms[room_id]["clients"].add(websocket)

        # Send current code to new client
        await websocket.send_json({"type": "init", "code": self.rooms[room_id]["code"]})

    async def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.rooms and websocket in self.rooms[room_id]["clients"]:
            self.rooms[room_id]["clients"].remove(websocket)

    async def broadcast(self, room_id: str, message: dict, sender: WebSocket):
        for ws in self.rooms[room_id]["clients"]:
            if ws is not sender:
                await ws.send_json(message)

    def update_code(self, room_id: str, patch: str):
        self.rooms[room_id]["code"] = patch

manager = WebSocketManager()
