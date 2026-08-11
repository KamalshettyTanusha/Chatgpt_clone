from typing import Optional

from pydantic import BaseModel


class FeedbackRequest(BaseModel):

    message_id: int

    feedback_type: str

    comment: Optional[str] = None


class RetryRequest(BaseModel):

    query: str

    previous_model: str

    memory: Optional[str] = None