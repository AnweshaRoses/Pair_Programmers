# app/api/rooms.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.websocket_manager import manager
from app.services.rooms import get_room_by_room_id, get_room_code  # helpers
from pydantic import BaseModel

router = APIRouter()

class RoomResponse(BaseModel):
    roomId: str
    code: str
    language: str | None = "python"

@router.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str, db: AsyncSession = Depends(get_db)):
    # check DB existence
    room = await get_room_by_room_id(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # prefer in-memory code if present
    code = manager.get_code(room_id) or room.code or ""
    return {"roomId": room_id, "code": code, "language": room.language}
