from sqlalchemy.orm import Session

from app.database.crud import (
    save_message as crud_save_message,
    get_messages as crud_get_messages
)


def save_message(
    db: Session,
    chat_id: int,
    role: str,
    content: str,
    model: str = None
):
    """
    Saves a chat message.
    """

    return crud_save_message(
        db=db,
        chat_id=chat_id,
        role=role,
        content=content,
        model=model
    )


def get_messages(
    db: Session,
    chat_id: int
):
    """
    Fetches all messages from a chat.
    """

    return crud_get_messages(
        db=db,
        chat_id=chat_id
    )