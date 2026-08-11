from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.memory.memory_manager import save_memory


@tool
def save_into_memory(
    memory_content: str,
    user_id: Annotated[
        int,
        InjectedState("user_id")
    ],
) -> str:
    """
    Persist useful long-term information about the
    authenticated user into personal memory.

    Use this tool when the user explicitly provides
    information that should be remembered across
    future conversations.

    Good examples:

    - "My favorite color is yellow."
    - "I like Python."
    - "My hobbies are sketching and reading."
    - "I am preparing for interviews."
    - "I prefer concise explanations."

    Do not save:

    - temporary questions
    - one-time requests
    - general knowledge
    - transient conversation
    - information about other people

    user_id is injected by LangGraph and must never
    be supplied by the LLM.
    """

    if (
        not memory_content
        or not memory_content.strip()
    ):
        return "Memory content is missing."

    try:

        result = save_memory(
            user_id=user_id,
            memory_text=memory_content.strip()
        )

        return (
            "Memory saved successfully. "
            f"Memory ID: {result['memory_id']}"
        )

    except Exception as e:

        return (
            f"Memory save error: {str(e)}"
        )