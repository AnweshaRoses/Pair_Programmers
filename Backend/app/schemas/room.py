from pydantic import BaseModel


class RoomCreateResponse(BaseModel):
    roomId: str


class AutoCompleteRequest(BaseModel):
    code: str
    cursorPosition: int
    language: str = "python"


class AutoCompleteResponse(BaseModel):
    suggestion: str
