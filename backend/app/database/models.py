from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float
)

from sqlalchemy.orm import relationship

from datetime import datetime

from app.database.database import Base


# ==========================================================
# User
# ==========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, nullable=False)

    email = Column(String, unique=True, nullable=False)

    password_hash = Column(String, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    chats = relationship(
        "Chat",
        back_populates="user"
    )


# ==========================================================
# Chat
# ==========================================================

class Chat(Base):

    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(
        String,
        default="New Chat"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    user = relationship(
        "User",
        back_populates="chats"
    )

    messages = relationship(
        "Message",
        back_populates="chat"
    )


# ==========================================================
# Message
# ==========================================================

class Message(Base):

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    role = Column(String)

    content = Column(Text)

    model = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    chat_id = Column(
        Integer,
        ForeignKey("chats.id")
    )

    chat = relationship(
        "Chat",
        back_populates="messages"
    )


# ==========================================================
# Memory
# ==========================================================

class Memory(Base):

    __tablename__ = "memory"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    memory_key = Column(String, nullable=False)

    memory_value = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================================================
# Semantic Cache
# ==========================================================

class Cache(Base):

    __tablename__ = "cache"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    query = Column(Text)

    answer = Column(Text)

    similarity = Column(
        Float,
        default=1.0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================================================
# Feedback
# ==========================================================

class Feedback(Base):

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    message_id = Column(
        Integer,
        ForeignKey("messages.id")
    )

    feedback_type = Column(String)

    comment = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )