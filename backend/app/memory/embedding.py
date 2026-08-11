from sentence_transformers import SentenceTransformer


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def create_embedding(text: str):
    """
    Convert text into a normalized vector embedding.
    """

    if not text or not text.strip():
        return []

    embedding = embedding_model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()