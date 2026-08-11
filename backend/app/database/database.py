from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings

# Create SQLite Engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base Class for all database models
Base = declarative_base()


def get_db():
    """
    Creates a new database session for every request.
    """
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()