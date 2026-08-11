from pydantic import BaseModel


class NewChatResponse(BaseModel):
    chat_id: int
    title: str


class ChatSummary(BaseModel):
    id: int
    title: str