from langchain_core.tools import tool
from langgraph.types import interrupt


@tool
def ask_user(question: str) -> str:
    """
    Ask the user for information that is required to answer
    the current request.

    This tool pauses the LangGraph execution and waits for the
    user's response.

    The LLM decides when this tool is necessary.

    Args:
        question: The question to ask the user.
    """

    if not question or not question.strip():
        return "Missing question."

    question = question.strip()

    # --------------------------------------------------------
    # INTERRUPT LANGGRAPH
    #
    # Execution pauses here.
    #
    # The value supplied when the graph is resumed becomes
    # the return value of this function.
    # --------------------------------------------------------

    user_answer = interrupt(
        {
            "type": "user_input",
            "question": question,
        }
    )

    if user_answer is None:
        return "The user did not provide an answer."

    return str(user_answer).strip()
