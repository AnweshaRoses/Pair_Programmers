import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import Room


async def create_room(db: AsyncSession) -> str:
    """
    Generates a roomId, saves to DB, returns it.
    """
    room_id = uuid.uuid4().hex[:8]

    room = Room(room_id=room_id, code="", language="python")
    db.add(room)
    await db.commit()

    return room_id


async def get_room_code(db: AsyncSession, room_id: str) -> str:
    result = await db.execute(select(Room).where(Room.room_id == room_id))
    room = result.scalar_one_or_none()
    return room.code if room else ""
    

async def save_room_code(db: AsyncSession, room_id: str, code: str):
    result = await db.execute(select(Room).where(Room.room_id == room_id))
    room = result.scalar_one_or_none()
    if room:
        room.code = code
        await db.commit()
