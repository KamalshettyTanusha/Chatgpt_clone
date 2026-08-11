import tiktoken

from app.config.constants import MAX_INPUT_TOKENS


# Default tokenizer
encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """
    Returns the estimated number of tokens in the text.
    """

    if not text:
        return 0

    return len(encoding.encode(text))


def is_token_limit_exceeded(text: str) -> bool:
    """
    Checks whether the input exceeds the allowed token limit.
    """

    return count_tokens(text) > MAX_INPUT_TOKENS