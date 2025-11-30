# app/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager
from app.db.session import AsyncSessionLocal
from app.services.rooms import save_room_code, get_room_code
from datetime import datetime

import json
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

async def send_message(websocket: WebSocket, message: dict):
    """Helper to send a properly formatted message."""
    try:
        await websocket.send_text(json.dumps(message))
    except Exception as e:
        logger.exception("Failed to send message: %s", e)

async def send_error(websocket: WebSocket, room_id: str, message: str, code: str = "UNKNOWN_ERROR"):
    """Send an error message to the client."""
    error_msg = {
        "type": "ERROR",
        "roomId": room_id,
        "payload": {},
        "message": message,
        "code": code
    }
    await send_message(websocket, error_msg)

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """
    WebSocket endpoint for realtime code editing.
    
    Message Protocol:
    
    Client Messages:
    - CODE_UPDATE: {"type": "CODE_UPDATE", "roomId": "...", "payload": {"code": "...", "cursor": 22}}
    - CURSOR_UPDATE: {"type": "CURSOR_UPDATE", "roomId": "...", "payload": {"cursor": 22, "selectionStart": 10, "selectionEnd": 20}}
    - PING: {"type": "PING", "roomId": "...", "payload": {}}
    
    Server Messages:
    - INIT: {"type": "INIT", "roomId": "...", "payload": {"code": "...", "cursor": 0}, "connectionCount": 1}
    - CODE_UPDATE: {"type": "CODE_UPDATE", "roomId": "...", "payload": {"code": "...", "cursor": 22}, "timestamp": "..."}
    - CURSOR_UPDATE: {"type": "CURSOR_UPDATE", "roomId": "...", "payload": {"cursor": 22}, "userId": "..."}
    - USER_JOINED: {"type": "USER_JOINED", "roomId": "...", "payload": {}, "connectionCount": 2}
    - USER_LEFT: {"type": "USER_LEFT", "roomId": "...", "payload": {}, "connectionCount": 1}
    - ERROR: {"type": "ERROR", "roomId": "...", "payload": {}, "message": "...", "code": "..."}
    - PONG: {"type": "PONG", "roomId": "...", "payload": {}}
    """
    # Generate a unique user ID for this connection
    user_id = str(uuid.uuid4())[:8]
    
    # Accept the connection
    await websocket.accept()
    logger.info("WebSocket connection accepted: room=%s, user=%s", room_id, user_id)

    # Create a database session for this WebSocket connection
    async with AsyncSessionLocal() as db:
        # Fetch current code from in-memory cache or DB fallback
        room_state = manager.get(room_id)
        if not room_state:
            # Try DB
            code = await get_room_code(db, room_id)
            room_state = manager.get_or_create(room_id, code or "")

        # Register connection
        connection_count_before = len(room_state.connections)
        room_state.connections.add(websocket)
        connection_count_after = len(room_state.connections)
        
        logger.info("WebSocket connected: room=%s, user=%s, connections=%d", 
                   room_id, user_id, connection_count_after)

        # Send INIT message with current code
        try:
            init_message = {
                "type": "INIT",
                "roomId": room_id,
                "payload": {
                    "code": room_state.code,
                    "cursor": 0
                },
                "connectionCount": connection_count_after
            }
            await send_message(websocket, init_message)
        except Exception as e:
            logger.exception("Failed to send init message: %s", e)

        # Notify other users that someone joined (if not the first connection)
        if connection_count_before > 0:
            user_joined_msg = {
                "type": "USER_JOINED",
                "roomId": room_id,
                "payload": {"userId": user_id},
                "connectionCount": connection_count_after
            }
            await room_state.broadcast(user_joined_msg, exclude=websocket)

        try:
            while True:
                text = await websocket.receive_text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    await send_error(websocket, room_id, "Invalid JSON format", "INVALID_JSON")
                    continue

                # Validate message structure
                if not isinstance(data, dict):
                    await send_error(websocket, room_id, "Message must be a JSON object", "INVALID_MESSAGE")
                    continue

                msg_type = data.get("type")
                msg_room_id = data.get("roomId")

                # Validate room ID matches
                if msg_room_id != room_id:
                    await send_error(websocket, room_id, f"Room ID mismatch. Expected {room_id}, got {msg_room_id}", "ROOM_ID_MISMATCH")
                    continue

                payload = data.get("payload", {})

                if msg_type == "CODE_UPDATE":
                    new_code = payload.get("code", "")
                    cursor = payload.get("cursor")
                    
                    # Update in-memory state
                    await manager.update_code(room_id, new_code)

                    # Broadcast to others in same room
                    code_update_msg = {
                        "type": "CODE_UPDATE",
                        "roomId": room_id,
                        "payload": {
                            "code": new_code,
                            "cursor": cursor
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await room_state.broadcast(code_update_msg, exclude=websocket)
                    
                    # Persist code to DB (async, don't block)
                    try:
                        await save_room_code(db, room_id, new_code)
                    except Exception:
                        logger.exception("Failed to save room code to DB")

                elif msg_type == "CURSOR_UPDATE":
                    cursor = payload.get("cursor")
                    selection_start = payload.get("selectionStart")
                    selection_end = payload.get("selectionEnd")
                    
                    # Broadcast cursor position to others
                    cursor_update_msg = {
                        "type": "CURSOR_UPDATE",
                        "roomId": room_id,
                        "payload": {
                            "cursor": cursor,
                            "selectionStart": selection_start,
                            "selectionEnd": selection_end
                        },
                        "userId": user_id
                    }
                    await room_state.broadcast(cursor_update_msg, exclude=websocket)

                elif msg_type == "PING":
                    # Respond to ping with pong
                    pong_msg = {
                        "type": "PONG",
                        "roomId": room_id,
                        "payload": {}
                    }
                    await send_message(websocket, pong_msg)

                else:
                    await send_error(websocket, room_id, f"Unknown message type: {msg_type}", "UNKNOWN_MESSAGE_TYPE")

        except WebSocketDisconnect:
            # Remove connection
            manager.remove_connection(room_id, websocket)
            connection_count_after = manager.connection_count(room_id)
            
            logger.info("WebSocket disconnected: room=%s, user=%s, connections=%d", 
                       room_id, user_id, connection_count_after)

            # Notify other users that someone left
            if connection_count_after > 0:
                user_left_msg = {
                    "type": "USER_LEFT",
                    "roomId": room_id,
                    "payload": {"userId": user_id},
                    "connectionCount": connection_count_after
                }
                await room_state.broadcast(user_left_msg, exclude=None)

            # If this was the last connection for this room, persist the code to DB
            if connection_count_after == 0:
                current_code = manager.get_code(room_id)
                try:
                    await save_room_code(db, room_id, current_code)
                    logger.info("Saved room %s code to DB on last disconnect", room_id)
                except Exception:
                    logger.exception("Failed to save room code to DB")

        except Exception as e:
            # Any other error
            manager.remove_connection(room_id, websocket)
            logger.exception("Websocket endpoint error for room %s, user %s", room_id, user_id)
            
            connection_count_after = manager.connection_count(room_id)
            if connection_count_after == 0:
                current_code = manager.get_code(room_id)
                try:
                    await save_room_code(db, room_id, current_code)
                except Exception:
                    logger.exception("Failed to save room code to DB after error")
