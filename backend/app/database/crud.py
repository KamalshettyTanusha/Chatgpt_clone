from sqlalchemy.orm import Session

from app.database.models import (
    User,
    Chat,
    Message
)


# ==========================================================
# USER
# ==========================================================

def get_user_by_email(
    db: Session,
    email: str
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_username(
    db: Session,
    username: str
):
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def create_user(
    db: Session,
    user: User
):
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ==========================================================
# CHAT
# ==========================================================

def create_chat(
    db: Session,
    chat: Chat
):
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


def get_chat(
    db: Session,
    chat_id: int
):
    return (
        db.query(Chat)
        .filter(Chat.id == chat_id)
        .first()
    )


# ==========================================================
# MESSAGE
# ==========================================================

def save_message(
    db: Session,
    chat_id: int,
    role: str,
    content: str,
    model: str = None
):
    message = Message(
        chat_id=chat_id,
        role=role,
        content=content,
        model=model
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_messages(
    db: Session,
    chat_id: int
):
    return (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at)
        .all()
    )