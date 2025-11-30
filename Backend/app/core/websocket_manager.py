from typing import Dict, Set
from fastapi import WebSocket
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class RoomState:
    def __init__(self, room_id: str, initial_code: str = ""):
        self.room_id = room_id
        self.code = initial_code
        self.connections: Set[WebSocket] = set()
        self.lock = asyncio.Lock()

    async def broadcast(self, message: dict, exclude: WebSocket | None = None):
        data = json.dumps(message)
        coros = []
        for conn in list(self.connections):
            if conn is exclude:
                continue
            coros.append(conn.send_text(data))
        if coros:
            # send concurrently and ignore individual failures here
            await asyncio.gather(*coros, return_exceptions=True)

class RoomManager:
    def __init__(self):
        # room_id -> RoomState
        self.rooms: Dict[str, RoomState] = {}

    def get_or_create(self, room_id: str, initial_code: str = "") -> RoomState:
        if room_id not in self.rooms:
            self.rooms[room_id] = RoomState(room_id, initial_code)
        return self.rooms[room_id]

    def get(self, room_id: str) -> RoomState | None:
        return self.rooms.get(room_id)

    def remove_connection(self, room_id: str, ws: WebSocket):
        room = self.rooms.get(room_id)
        if not room:
            return
        room.connections.discard(ws)

    def connection_count(self, room_id: str) -> int:
        room = self.rooms.get(room_id)
        return len(room.connections) if room else 0

    def get_code(self, room_id: str) -> str:
        room = self.rooms.get(room_id)
        return room.code if room else ""

    async def update_code(self, room_id: str, new_code: str):
        room = self.get(room_id)
        if not room:
            # create if missing
            room = self.get_or_create(room_id, new_code)
        async with room.lock:
            room.code = new_code

# single global manager
manager = RoomManager()
