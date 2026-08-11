"""
Chat service.

The service validates chat ownership, supplies existing
conversation history to LangGraph, and supports LangGraph
human-in-the-loop interrupts/resume.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langgraph.types import Command

from app.agent.graph import agent_graph

from app.history.history_manager import (
    get_chat_history
)

from app.history.thread_manager import (
    get_thread
)


# ============================================================
# History → LangChain Messages
# ============================================================

def _history_to_messages(history):

    messages = []

    for item in history:

        role = item.get(
            "role"
        )

        content = item.get(
            "content",
            ""
        )

        if role == "user":

            messages.append(
                HumanMessage(
                    content=content
                )
            )

        elif role == "assistant":

            messages.append(
                AIMessage(
                    content=content
                )
            )

        elif role == "system":

            messages.append(
                SystemMessage(
                    content=content
                )
            )

    return messages


# ============================================================
# LangGraph Thread ID
# ============================================================

def _get_thread_id(
    user_id: int,
    chat_id: int
) -> str:

    """
    Generate a stable LangGraph thread ID.

    The same user + chat always maps to the same
    LangGraph conversation thread.
    """

    return (
        f"user-{user_id}-chat-{chat_id}"
    )


# ============================================================
# Detect Interrupted Graph
# ============================================================

def _get_interrupt(
    result
):

    """
    Return the first LangGraph interrupt if one exists.

    LangGraph returns interrupts under the special
    '__interrupt__' key.
    """

    interrupts = result.get(
        "__interrupt__"
    )

    if not interrupts:

        return None

    return interrupts[0]


# ============================================================
# Process Chat
# ============================================================

def process_chat(
    user,
    chat_id: int,
    message: str,
    db: Session
):

    # ========================================================
    # Verify Chat Ownership
    # ========================================================

    chat = get_thread(
        db=db,
        chat_id=chat_id,
        user_id=user.id
    )

    if chat is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Chat not found for the "
                "authenticated user."
            )
        )

    # ========================================================
    # Stable LangGraph Thread
    # ========================================================

    thread_id = _get_thread_id(
        user_id=user.id,
        chat_id=chat_id
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # ========================================================
    # Check Whether This Chat Is Already Interrupted
    # ========================================================

    try:

        current_state = (
            agent_graph.get_state(
                config
            )
        )

        existing_interrupts = (
            current_state.tasks
        )

        has_pending_interrupt = False

        if existing_interrupts:

            for task in existing_interrupts:

                if getattr(
                    task,
                    "interrupts",
                    None
                ):

                    has_pending_interrupt = True
                    break

    except Exception as e:

        print(
            "\n========== "
            "LANGGRAPH STATE ERROR "
            "=========="
        )

        print(str(e))

        print(
            "=====================================\n"
        )

        has_pending_interrupt = False

    # ========================================================
    # Resume Existing Human-in-the-Loop Interaction
    # ========================================================

    if has_pending_interrupt:

        print(
            "\n========== "
            "RESUMING LANGGRAPH "
            "=========="
        )

        print(
            {
                "thread_id": thread_id,
                "user_response": message
            }
        )

        print(
            "=====================================\n"
        )

        try:

            result = agent_graph.invoke(
                Command(
                    resume=message
                ),
                config=config
            )

        except Exception as e:

            print(
                "\n========== "
                "LANGGRAPH RESUME ERROR "
                "=========="
            )

            print(str(e))

            print(
                "=====================================\n"
            )

            return {
                "response": (
                    "Something went wrong while "
                    "resuming the conversation."
                ),
                "source": "error"
            }

    # ========================================================
    # Start New LangGraph Execution
    # ========================================================

    else:

        # ----------------------------------------------------
        # Load Existing Database History
        # ----------------------------------------------------

        history = get_chat_history(
            db=db,
            chat_id=chat_id
        )

        previous_messages = (
            _history_to_messages(
                history
            )
        )

        # ----------------------------------------------------
        # Initial LangGraph State
        # ----------------------------------------------------

        initial_state = {

            "user_id": user.id,

            "chat_id": chat_id,

            "message_id": None,

            "user_message": message,

            "messages": previous_messages,

            # Memory
            "memory_results": [],
            "memory_context": "",

            # Cache
            "cache_result": None,
            "cache_hit": False,
            "cacheable": False,

            # Tools
            "tool_name": None,
            "tool_input": None,
            "tool_result": None,
            "tool_call_count": 0,

            # LLM
            "model": None,
            "response": None,

            # Limits
            "token_count": 0,

            # Ask User
            "awaiting_user": False,
            "user_response": None,
            "pending_question": None,

            # Control
            "error": None,
            "retry_count": 0
        }

        # ----------------------------------------------------
        # Execute LangGraph
        # ----------------------------------------------------

        print(
            "\n========== "
            "STARTING LANGGRAPH "
            "=========="
        )

        print(
            {
                "thread_id": thread_id,
                "user_message": message
            }
        )

        print(
            "=====================================\n"
        )

        try:

            result = agent_graph.invoke(
                initial_state,
                config=config
            )

        except Exception as e:

            print(
                "\n========== "
                "LANGGRAPH ERROR "
                "=========="
            )

            print(str(e))

            print(
                "=====================================\n"
            )

            return {
                "response": (
                    "Something went wrong while "
                    "processing your request."
                ),
                "source": "error"
            }

    # ========================================================
    # Handle LangGraph Interrupt
    # ========================================================

    interrupt_data = _get_interrupt(
        result
    )

    if interrupt_data is not None:

        interrupt_value = (
            interrupt_data.value
            if hasattr(
                interrupt_data,
                "value"
            )
            else interrupt_data
        )

        question = ""

        if isinstance(
            interrupt_value,
            dict
        ):

            question = (
                interrupt_value.get(
                    "question",
                    ""
                )
            )

        else:

            question = str(
                interrupt_value
            )

        print(
            "\n========== "
            "LANGGRAPH INTERRUPTED "
            "=========="
        )

        print(
            {
                "thread_id": thread_id,
                "question": question
            }
        )

        print(
            "=====================================\n"
        )

        return {

            "response": question,

            "model": result.get(
                "model"
            ),

            "source": "ask_user",

            "awaiting_user": True,

            "question": question,

            "thread_id": thread_id
        }

    # ========================================================
    # Normal Final Response
    # ========================================================

    response = (
        result.get("response")
        or "Unable to generate a response."
    )

    response_data = {

        "response": response,

        "model": result.get(
            "model"
        ),

        "source": "langgraph",

        "thread_id": thread_id
    }

    # ========================================================
    # Cache Hit
    # ========================================================

    if result.get(
        "cache_hit"
    ):

        response_data[
            "source"
        ] = "cache"

    # ========================================================
    # Error
    # ========================================================

    elif result.get(
        "error"
    ):

        response_data[
            "source"
        ] = "error"

    return response_data

