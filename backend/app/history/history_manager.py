from sqlalchemy.orm import Session

from app.history.message_store import get_messages
from app.config.constants import MAX_HISTORY_MESSAGES


def get_chat_history(
    db: Session,
    chat_id: int
):
    """
    Returns the most recent conversation history
    formatted for the LLM.
    """

    messages = get_messages(
        db,
        chat_id
    )[-MAX_HISTORY_MESSAGES:]

    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "model": message.model
        }
        for message in messages
    ]