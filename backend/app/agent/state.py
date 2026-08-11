from typing import Any, Optional, Annotated

from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):

    # ============================================================
    # User / Conversation
    # ============================================================

    user_id: int
    chat_id: int
    message_id: Optional[int]

    user_message: str

    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]

    # ============================================================
    # Memory
    #
    # These are retained for tool results/debugging.
    # Memory is NOT automatically fetched anymore.
    # ============================================================

    memory_results: list[str]
    memory_context: str

    # ============================================================
    # Semantic Cache
    # ============================================================

    cache_result: Optional[
        dict[str, Any]
    ]

    cache_hit: bool
    cacheable: bool

    # NEW:
    # True when the answer depends on personal/user memory.
    memory_dependent: bool


    # ============================================================
    # Tool Calling
    # ============================================================

    tool_name: Optional[str]

    tool_input: Optional[
        dict[str, Any]
    ]

    tool_result: Any

    tool_call_count: int

    # ============================================================
    # LLM
    # ============================================================

    model: Optional[str]

    response: Optional[str]

    # ============================================================
    # Limits
    # ============================================================

    token_count: int

    # ============================================================
    # User Interaction
    # ============================================================

    awaiting_user: bool

    user_response: Optional[str]

    pending_question: Optional[str]

    # ============================================================
    # Control Flow
    # ============================================================

    error: Optional[str]

    retry_count: int