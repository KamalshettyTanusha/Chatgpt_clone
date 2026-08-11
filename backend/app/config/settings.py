from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()


class Settings:
    # OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    # Models
    PRIMARY_MODEL = os.getenv("PRIMARY_MODEL")
    FALLBACK_MODELS = [
        os.getenv("FALLBACK_MODEL_1"),
        os.getenv("FALLBACK_MODEL_2"),
        os.getenv("FALLBACK_MODEL_3"),
        os.getenv("FALLBACK_MODEL_4"),
    ]

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")

    # ChromaDB
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")

    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )


# Create a single settings object
settings = Settings()