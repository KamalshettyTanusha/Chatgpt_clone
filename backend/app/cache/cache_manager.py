from app.cache.semantic_cache import semantic_cache


def get_cached_response(
    user_id: int,
    query: str
):
    """
    Return a semantically similar cached
    answer for this user.
    """

    return semantic_cache.search_cache(
        user_id=user_id,
        query=query
    )


def save_response_to_cache(
    user_id: int,
    query: str,
    answer: str
):
    """
    Persist a question/answer pair in
    the semantic cache.
    """

    return semantic_cache.add_cache(
        user_id=user_id,
        question=query,
        answer=answer
    )
def delete_cached_response(
    user_id: int,
    query: str
):
    """
    Delete an exact cached response for a user.
    """

    return semantic_cache.delete_cache(
        user_id=user_id,
        query=query
    )