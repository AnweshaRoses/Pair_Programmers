from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.services.rooms import create_room, save_room_code
from app.services.websocket_manager import manager
from app.schemas.room import (
    RoomCreateResponse,
    AutoCompleteRequest,
    AutoCompleteResponse,
)
from app.db.session import AsyncSessionLocal

router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session



@router.post("/rooms", response_model=RoomCreateResponse)
async def create_room_endpoint(db=Depends(get_db)):
    room_id = await create_room(db)
    return RoomCreateResponse(roomId=room_id)


@router.post("/autocomplete", response_model=AutoCompleteResponse)
async def autocomplete(payload: AutoCompleteRequest):
    return AutoCompleteResponse(suggestion="def hello_world():\n    print('Hello')")
    

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)

    # Create a database session for this WebSocket connection
    async with AsyncSessionLocal() as db:
        try:
            while True:
                data = await websocket.receive_json()

                if data["type"] == "patch":
                    code = data["code"]
                    manager.update_code(room_id, code)

                    await manager.broadcast(room_id, data, websocket)

                    # Persist code
                    await save_room_code(db, room_id, code)

        except WebSocketDisconnect:
            await manager.disconnect(room_id, websocket)
