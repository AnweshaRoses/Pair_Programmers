from pydantic import BaseModel
from typing import Optional, Literal

# Message Types
MessageType = Literal[
    "CODE_UPDATE",
    "CURSOR_UPDATE", 
    "INIT",
    "USER_JOINED",
    "USER_LEFT",
    "ERROR",
    "PING",
    "PONG"
]

# Client Messages
class CodeUpdatePayload(BaseModel):
    code: str
    cursor: Optional[int] = None

class CursorUpdatePayload(BaseModel):
    cursor: int
    selectionStart: Optional[int] = None
    selectionEnd: Optional[int] = None

class ClientMessage(BaseModel):
    type: MessageType
    roomId: str
    payload: Optional[dict] = None

# Server Messages
class CodeUpdateResponse(BaseModel):
    type: Literal["CODE_UPDATE"] = "CODE_UPDATE"
    roomId: str
    payload: CodeUpdatePayload
    timestamp: Optional[str] = None

class CursorUpdateResponse(BaseModel):
    type: Literal["CURSOR_UPDATE"] = "CURSOR_UPDATE"
    roomId: str
    payload: CursorUpdatePayload
    userId: Optional[str] = None  # For multi-user cursor tracking

class InitResponse(BaseModel):
    type: Literal["INIT"] = "INIT"
    roomId: str
    payload: CodeUpdatePayload
    connectionCount: int

class UserJoinedResponse(BaseModel):
    type: Literal["USER_JOINED"] = "USER_JOINED"
    roomId: str
    payload: dict
    connectionCount: int

class UserLeftResponse(BaseModel):
    type: Literal["USER_LEFT"] = "USER_LEFT"
    roomId: str
    payload: dict
    connectionCount: int

class ErrorResponse(BaseModel):
    type: Literal["ERROR"] = "ERROR"
    roomId: str
    payload: dict
    message: str
    code: Optional[str] = None

class PingResponse(BaseModel):
    type: Literal["PONG"] = "PONG"
    roomId: str
    payload: dict

