from fastapi import APIRouter, Depends
from app.services.rooms import create_room
from app.schemas.room import RoomCreateResponse
from app.db.session import AsyncSessionLocal

router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/rooms", response_model=RoomCreateResponse)
async def create_room_endpoint(db=Depends(get_db)):
    room_id = await create_room(db)
    return RoomCreateResponse(roomId=room_id)
