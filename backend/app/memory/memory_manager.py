import uuid

from app.config.constants import MEMORY_SIMILARITY_THRESHOLD
from app.memory.embedding import create_embedding
from app.memory.chroma_client import get_memory_collection


def save_memory(
    user_id: int,
    memory_text: str
):
    """
    Save user information into persistent ChromaDB memory.
    """

    collection = get_memory_collection()

    embedding = create_embedding(
        memory_text
    )

    if not embedding:
        raise ValueError(
            "Could not create an embedding for the memory."
        )

    memory_id = str(uuid.uuid4())

    collection.add(
        ids=[memory_id],
        embeddings=[embedding],
        documents=[memory_text],
        metadatas=[
            {
                "user_id": str(user_id)
            }
        ]
    )

    return {
        "message": "Memory saved successfully.",
        "memory_id": memory_id
    }


def fetch_memory(
    user_id: int,
    query: str
):
    """
    Retrieve relevant memories for one authenticated user.
    """

    collection = get_memory_collection()

    query_embedding = create_embedding(
        query
    )

    if not query_embedding:
        return []

    count = collection.count()

    if count == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(5, count),
        where={
            "user_id": str(user_id)
        },
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get(
        "documents"
    ) or [[]]

    distances = results.get(
        "distances"
    ) or [[]]

    memories = []

    if documents and documents[0]:

        for index, document in enumerate(
            documents[0]
        ):

            distance = (
                distances[0][index]
                if distances and distances[0]
                else None
            )

            # Embeddings are normalized.
            #
            # For L2 distance:
            #
            # similarity = 1 - (distance / 2)

            similarity = (
                1 - (distance / 2)
                if distance is not None
                else 0
            )
            print(
                f"Memory candidate: {document} | "
                f"distance={distance} | "
                f"similarity={similarity} | "
                f"threshold={MEMORY_SIMILARITY_THRESHOLD}"
                    )
            if similarity >= MEMORY_SIMILARITY_THRESHOLD:
                memories.append(document)

    return list(
        dict.fromkeys(memories)
    )