"""
LLM configuration for the LangGraph agent.

The LLM is responsible for:
    - Understanding the user request
    - Deciding whether a tool is required
    - Calling tools through LangChain tool calling
    - Generating the final response

LangGraph is responsible for orchestration.
"""

from langchain_openai import ChatOpenAI

from app.config.settings import settings


# ============================================================
# Primary LLM
# ============================================================

def get_primary_llm():
    """
    Create the primary LLM.

    OpenRouter exposes an OpenAI-compatible API, so
    ChatOpenAI can be used with OpenRouter's base URL.
    """

    return ChatOpenAI(
        model=settings.PRIMARY_MODEL,
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=1024,
    )


# ============================================================
# Fallback LLMs
# ============================================================

def get_fallback_llms():
    """
    Create the configured fallback LLMs.

    The order comes from settings.FALLBACK_MODELS.
    """

    fallback_llms = []

    for model in settings.FALLBACK_MODELS:

        llm = ChatOpenAI(
            model=model,
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=1024,
        )

        fallback_llms.append(llm)

    return fallback_llms


# ============================================================
# LLM with Fallback
# ============================================================

def get_llm():
    """
    Return the primary LLM with fallback support.

    LangChain will automatically try the fallback models
    if the primary model fails.
    """

    primary_llm = get_primary_llm()
    fallback_llms = get_fallback_llms()

    if fallback_llms:
        return primary_llm.with_fallbacks(
            fallback_llms
        )

    return primary_llm

