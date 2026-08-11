"""
LLM configuration for the LangGraph AI Assistant.

Primary model:
    Gemini 2.5 Flash

Provider:
    OpenRouter

LangChain is used so the returned model can be directly
used with LangGraph and ToolNode.
"""

from langchain_openai import ChatOpenAI

from app.config.settings import settings


# ============================================================
# Primary LLM
# ============================================================

def get_llm() -> ChatOpenAI:
    """
    Create and return the primary LLM.

    OpenRouter exposes an OpenAI-compatible API, so
    ChatOpenAI can be used with OpenRouter's base URL.

    The actual tool binding is performed in nodes.py:

        llm.bind_tools(TOOLS)
    """

    return ChatOpenAI(
        model=settings.PRIMARY_MODEL,
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=1024,
    )

