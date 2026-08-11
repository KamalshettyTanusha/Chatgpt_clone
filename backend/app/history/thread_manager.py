from sqlalchemy.orm import Session

from app.database.models import Chat


def create_thread(
    db: Session,
    user_id: int,
    title: str = "New Chat"
):
    """
    Creates a new chat thread.
    """

    chat = Chat(
        user_id=user_id,
        title=title
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat



def get_user_threads(
    db: Session,
    user_id: int
):
    """
    Fetches all chats of a user.
    """

    chats = (
        db.query(Chat)
        .filter(
            Chat.user_id == user_id
        )
        .order_by(
            Chat.created_at.desc()
        )
        .all()
    )

    return chats



def get_thread(
    db: Session,
    chat_id: int,
    user_id: int
):
    """
    Fetches a specific chat thread.
    """

    chat = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id,
            Chat.user_id == user_id
        )
        .first()
    )

    return chat



def rename_thread(
    db: Session,
    chat_id: int,
    title: str
):
    """
    Renames a chat.
    """

    chat = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id
        )
        .first()
    )

    if chat:
        chat.title = title
        db.commit()

    return chat