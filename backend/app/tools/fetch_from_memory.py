from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.memory.memory_manager import fetch_memory


@tool
def fetch_from_memory(
    query: str,
    user_id: Annotated[
        int,
        InjectedState("user_id")
    ],
) -> str:
    """
    Retrieve relevant long-term personal information
    belonging to the authenticated user.

    Use this tool when the user's question requires
    personal information that may already be stored
    in memory.

    Examples:

    - "What are my hobbies?"
    - "What programming language do I prefer?"
    - "Do I have any goals stored?"
    - "What is my favorite color?"
    - "Do I have any hobbies in common with X?"

    For comparison questions, retrieve the user's
    information first and then use other appropriate
    tools to retrieve information about the other
    person or subject.

    Do not use this tool for general knowledge,
    calculations, or unrelated questions.

    user_id is injected by LangGraph and must never
    be supplied by the LLM.
    """

    if not query or not query.strip():
        return "Memory query is missing."

    try:

        memories = fetch_memory(
            user_id=user_id,
            query=query.strip()
        )

        if not memories:

            return (
                "No relevant personal memory was found "
                "for this query."
            )

        return "\n".join(
            f"- {memory}"
            for memory in memories
        )

    except Exception as e:

        return (
            f"Memory search error: {str(e)}"
        )