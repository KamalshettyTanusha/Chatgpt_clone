"""
Retry handler.

Used when the user gives negative feedback and wants
the response regenerated using a different model.

This is separate from automatic LLM fallback.

Automatic fallback:
    Gemini fails
        ↓
    DeepSeek
        ↓
    Qwen
        ↓
    ...

Manual retry:
    User presses 👎 / Retry
        ↓
    Select a different model
        ↓
    Generate a new response
"""

from langchain_openai import ChatOpenAI

from app.config.settings import settings


def get_retry_model(previous_model: str | None = None):
    """
    Select the first configured fallback model that is
    different from the model that produced the previous response.
    """

    for model in settings.FALLBACK_MODELS:

        if not model:
            continue

        if model != previous_model:
            return model

    return None


def retry_with_different_model(
    query: str,
    memory=None,
    previous_model=None,
):
    """
    Regenerate the response using a different model.

    This function is used for explicit user retry/feedback,
    not for automatic fallback.
    """

    retry_model = get_retry_model(previous_model)

    if not retry_model:
        return {
            "response": "No alternative model is available.",
            "model": previous_model,
            "retry": False,
        }

    # --------------------------------------------------------
    # Create the retry model
    # --------------------------------------------------------

    llm = ChatOpenAI(
        model=retry_model,
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=1024,
    )

    # --------------------------------------------------------
    # Build messages
    # --------------------------------------------------------

    messages = []

    if memory:
        messages.append(
            (
                "system",
                f"Relevant user memory:\n{memory}"
            )
        )

    messages.append(
        (
            "user",
            query
        )
    )

    # --------------------------------------------------------
    # Generate retry response
    # --------------------------------------------------------

    try:

        response = llm.invoke(messages)

        return {
            "response": response.content,
            "model": retry_model,
            "retry": True,
        }

    except Exception as e:

        return {
            "response": f"Retry failed: {str(e)}",
            "model": retry_model,
            "retry": False,
        }

