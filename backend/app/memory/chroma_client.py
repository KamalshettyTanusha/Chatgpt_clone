from pathlib import Path

import chromadb

from app.config.constants import CHROMA_COLLECTION_NAME
from app.config.settings import settings


chroma_path = Path(
    settings.CHROMA_DB_PATH or "./chroma_db"
)


client = chromadb.PersistentClient(
    path=str(chroma_path)
)


memory_collection = client.get_or_create_collection(
    name=CHROMA_COLLECTION_NAME
)


def get_memory_collection():
    """
    Return the persistent user-memory collection.
    """

    return memory_collection