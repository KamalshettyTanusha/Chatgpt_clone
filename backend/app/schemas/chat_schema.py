from pydantic import BaseModel


class ChatRequest(BaseModel):
    chat_id: int
    message: str


class ChatResponse(BaseModel):
    response: str
    model: str
    source: str