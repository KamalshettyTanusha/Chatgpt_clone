"""
LangGraph nodes for the AI Assistant.

The LLM decides which tools are required.
LangGraph orchestrates the execution of those tools.
"""

from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from app.agent.state import AgentState

from app.llm.llm import get_llm

from app.utils.debug import debug_log

from app.config.settings import settings

from app.config.constants import (
    MAX_MESSAGE_LENGTH,
    MAX_INPUT_TOKENS,
    MAX_TOOL_CALLS,
)

from app.cache.cache_manager import (
    get_cached_response,
    save_response_to_cache,
)

from app.database.database import SessionLocal

from app.database.crud import save_message


# ============================================================
# System Prompt
# ============================================================

SYSTEM_PROMPT = """
You are an intelligent agentic AI assistant.

You have access to these tools:

1. calculator
   - Performs mathematical calculations.

2. weather
   - Retrieves current weather information.

3. live_web_search
   - Searches the live web for information that requires
     current, recent, external, or otherwise unavailable
     information.

4. fetch_from_memory
   - Retrieves relevant long-term personal information
     about the authenticated user.

5. save_into_memory
   - Saves useful long-term personal information about
     the authenticated user.

6. ask_user
   - Asks the user for information that is genuinely
     required but cannot be obtained from memory or tools.

============================================================
IMPORTANT: YOU ARE RESPONSIBLE FOR TOOL SELECTION
============================================================

Do NOT use a fixed tool sequence.

Analyze every user request independently and decide which
tools are actually necessary.

You may use:
- zero tools
- one tool
- multiple tools
- the same tool again if necessary

After receiving a tool result, analyze the result again and
decide whether another tool is required before answering.

Do not stop merely because one tool has returned a result.

============================================================
PERSONAL INFORMATION
============================================================

When the user's request requires information about the user:

1. First determine whether the information may exist in
   personal memory.

2. If it may exist, call fetch_from_memory.

3. If memory contains the required information, use it.

4. If memory does not contain the required information and
   the user needs to provide it, use ask_user.

5. Do not invent personal information.

6. When the user provides useful long-term personal
   information, use save_into_memory.

============================================================
MULTI-SOURCE QUESTIONS
============================================================

Some questions require information from more than one source.

For example:

"Do I and Donald Trump have any common hobbies?"

This requires:
- the user's hobbies → fetch_from_memory
- Donald Trump's hobbies → live_web_search

Therefore, use both tools when both pieces of information
are necessary.

After obtaining both results, compare them and answer the
user.

============================================================
WEB SEARCH
============================================================

Use live_web_search when live/external information is
actually required.

Do NOT use live_web_search merely because the question is
about a technical term.

You should normally answer directly from your existing
knowledge when the question asks for:

- definitions
- meanings
- full forms
- basic concepts
- common facts
- simple explanations
- general programming concepts
- well-known terminology

For example:

"What is the full form of RAG?"

should normally be answered directly:

"Retrieval-Augmented Generation."

Do not search the web simply because a term has multiple
possible meanings unless clarification or current
information is genuinely necessary.

============================================================
CURRENT INFORMATION
============================================================

Use live_web_search when the user asks for information
whose correctness depends on current external information,
such as:

- current events
- recent events
- latest information
- current office holders
- current public information
- current news
- information about a person that you do not reliably know
- information that explicitly requires web research

============================================================
CALCULATIONS
============================================================

Use calculator for arithmetic and mathematical expressions.

Do not mentally calculate when the calculator tool is
available and appropriate.

============================================================
MEMORY SAVING
============================================================

Save useful long-term user information such as:

- preferences
- hobbies
- interests
- goals
- skills
- occupation
- communication preferences

Do not save temporary questions or one-time requests.

============================================================
FINAL ANSWER
============================================================

Only produce the final answer after all required tools have
been executed.

If multiple tools were required, combine their results into
one coherent answer.

Never expose internal tool-selection reasoning to the user.
"""


# ============================================================
# 1. Validate Request
# ============================================================

def validate_request(
    state: AgentState
) -> dict[str, Any]:

    user_message = (
        state.get(
            "user_message",
            ""
        ).strip()
    )

    debug_log(
        "USER REQUEST",
        {
            "user_id": state.get("user_id"),
            "chat_id": state.get("chat_id"),
            "message": user_message,
        },
    )

    if not user_message:

        return {
            "error": "Message cannot be empty."
        }

    if len(user_message) > MAX_MESSAGE_LENGTH:

        return {
            "error": (
                "Message exceeds the maximum length "
                f"of {MAX_MESSAGE_LENGTH} characters."
            )
        }

    return {
        "user_message": user_message,
        "error": None,
    }


# ============================================================
# 2. Rate Limit
# ============================================================

def check_rate_limit(
    state: AgentState
) -> dict[str, Any]:

    user_id = state.get(
        "user_id"
    )

    if not user_id:

        return {
            "error": (
                "User authentication is required."
            )
        }

    return {
        "error": None
    }


# ============================================================
# 3. Token Limit
# ============================================================

def check_token_limit(
    state: AgentState
) -> dict[str, Any]:

    user_message = state.get(
        "user_message",
        ""
    )

    estimated_tokens = len(
        user_message.split()
    )

    if estimated_tokens > MAX_INPUT_TOKENS:

        return {
            "token_count": estimated_tokens,
            "error": "Token limit exceeded.",
        }

    return {
        "token_count": estimated_tokens,
        "error": None,
    }


# ============================================================
# 4. Semantic Cache
# ============================================================

def check_cache(
    state: AgentState
) -> dict[str, Any]:

    user_id = state.get(
        "user_id"
    )

    user_message = state.get(
        "user_message",
        ""
    )

    # Keep the existing cache policy.
    non_cacheable_patterns = [
        "what time",
        "current time",
        "weather",
        "today",
        "tomorrow",
        "latest",
        "recent",
        "news",
        "stock price",
        "current price",
        "current weather",
    ]

    question_lower = (
        user_message.lower()
    )

    cacheable = not any(
        pattern in question_lower
        for pattern in non_cacheable_patterns
    )

    debug_log(
        "SEMANTIC CACHE CHECK",
        {
            "user_id": user_id,
            "query": user_message,
            "cacheable": cacheable,
        },
    )

    if not cacheable:

        debug_log(
            "CACHE MISS",
            "Request is not cacheable.",
        )

        return {
            "cache_hit": False,
            "cache_result": None,
            "cacheable": False,
        }

    try:

        cache = get_cached_response(
            user_id=user_id,
            query=user_message,
        )

        if cache["found"]:

            debug_log(
                "CACHE HIT",
                cache,
            )

            return {
                "cache_hit": True,
                "cache_result": cache,
                "cacheable": True,
            }

        debug_log(
            "CACHE MISS",
            {
                "query": user_message
            },
        )

        return {
            "cache_hit": False,
            "cache_result": None,
            "cacheable": True,
        }

    except Exception as e:

        debug_log(
            "CACHE ERROR",
            str(e),
        )

        return {
            "cache_hit": False,
            "cache_result": None,
            "cacheable": True,
            "error": (
                f"Cache error: {str(e)}"
            ),
        }


# ============================================================
# 5. Prepare Messages
# ============================================================

def prepare_messages(
    state: AgentState
) -> dict[str, Any]:

    user_message = state.get(
        "user_message",
        ""
    )

    existing_messages = state.get(
        "messages",
        []
    )

    messages = list(
        existing_messages
    )

    # --------------------------------------------------------
    # Add system prompt once
    # --------------------------------------------------------

    has_system_message = any(
        isinstance(
            message,
            SystemMessage
        )
        for message in messages
    )

    if not has_system_message:

        messages.insert(
            0,
            SystemMessage(
                content=SYSTEM_PROMPT
            ),
        )

    # --------------------------------------------------------
    # Add current user message
    # --------------------------------------------------------

    messages.append(
        HumanMessage(
            content=user_message
        )
    )

    return {
        "messages": messages
    }


# ============================================================
# 6. Call LLM
# ============================================================

def call_llm(
    state: AgentState
) -> dict[str, Any]:

    messages = state.get(
        "messages",
        []
    )

    if not messages:

        return {
            "error": (
                "No messages available "
                "for the LLM."
            )
        }

    try:

        llm = get_llm()

        from app.tools.tool_router import TOOLS

        # ----------------------------------------------------
        # The LLM receives ALL tools.
        #
        # It decides dynamically which tool(s) to call.
        # ----------------------------------------------------

        llm_with_tools = llm.bind_tools(
            TOOLS,
            tool_choice="auto",
        )

        debug_log(
            "LLM CALL",
            {
                "model": (
                    state.get("model")
                    or settings.PRIMARY_MODEL
                ),
                "message_count": len(messages),
                "user_message": state.get(
                    "user_message"
                ),
            },
        )

        response = (
            llm_with_tools.invoke(
                messages
            )
        )

        if not isinstance(
            response,
            AIMessage
        ):

            return {
                "error": (
                    "Invalid response received "
                    "from LLM."
                )
            }

        model_name = (
            getattr(
                response,
                "response_metadata",
                {}
            ).get("model_name")
            or settings.PRIMARY_MODEL
        )
        #-----------------------------
        # Detect whether this request depends
        #on personal memory.
        #---------------------------------------


        memory_dependent = state.get(
            "memory_dependent",
            False
        )

        for tool_call in response.tool_calls:

            if tool_call["name"] in {
                "fetch_from_memory",
                "save_into_memory"
            }:
                memory_dependent = True


        debug_log(
            "LLM RESPONSE",
            {
                "model": model_name,
                "content": response.content,
                "tool_calls": response.tool_calls,
                "memory_dependent": memory_dependent,
            },
        )

        return {
            "messages": [response],
            "model": model_name,
            "response": (
                response.content
                if isinstance(
                    response.content,
                    str
                )
                else str(
                    response.content
                )
            ),
            "memory_dependent": memory_dependent,
            "error": None,
        }

    except Exception as e:

        debug_log(
            "LLM ERROR",
            str(e)
        )

        return {
            "error": (
                f"LLM error: {str(e)}"
            )
        }


# ============================================================
# 7. Tool Call Limit
# ============================================================

def check_tool_call_limit(
    state: AgentState
) -> dict[str, Any]:

    tool_call_count = state.get(
        "tool_call_count",
        0
    )

    if tool_call_count >= MAX_TOOL_CALLS:

        return {
            "error": (
                "Maximum tool call limit reached."
            )
        }

    return {
        "error": None
    }


# ============================================================
# 8. Prepare Final Response
# ============================================================

def prepare_response(
    state: AgentState
) -> dict[str, Any]:

    messages = state.get(
        "messages",
        []
    )

    for message in reversed(
        messages
    ):

        if isinstance(
            message,
            AIMessage
        ):

            if getattr(
                message,
                "tool_calls",
                None
            ):
                continue

            content = (
                message.content
                if isinstance(
                    message.content,
                    str
                )
                else str(
                    message.content
                )
            )

            debug_log(
                "FINAL RESPONSE",
                content
            )

            return {
                "response": content
            }

    response = state.get(
        "response",
        ""
    )

    debug_log(
        "FINAL RESPONSE",
        response
    )

    return {
        "response": response
    }


# ============================================================
# 9. Save History
# ============================================================

def save_history(
    state: AgentState
) -> dict[str, Any]:

    user_id = state.get(
        "user_id"
    )

    chat_id = state.get(
        "chat_id"
    )

    user_message = state.get(
        "user_message"
    )

    response = state.get(
        "response"
    )

    model = state.get(
        "model"
    )

    if (
        not user_id
        or not chat_id
        or not user_message
    ):

        return {
            "error": (
                "Missing information required "
                "to save history."
            )
        }

    if not response:

        return {
            "error": (
                "Cannot save empty assistant response."
            )
        }

    db = SessionLocal()

    try:

        user_record = save_message(
            db=db,
            chat_id=chat_id,
            role="user",
            content=user_message,
        )

        assistant_record = save_message(
            db=db,
            chat_id=chat_id,
            role="assistant",
            content=response,
            model=model,
        )

        debug_log(
            "HISTORY SAVED",
            {
                "chat_id": chat_id,
                "user_message_id": user_record.id,
                "assistant_message_id": (
                    assistant_record.id
                ),
            },
        )

        return {
            "message_id": assistant_record.id,
            "error": None,
        }

    except Exception as e:

        db.rollback()

        debug_log(
            "HISTORY ERROR",
            str(e)
        )

        return {
            "error": (
                f"History save error: {str(e)}"
            )
        }

    finally:

        db.close()


# ============================================================
# 10. Update Semantic Cache
# ============================================================

def update_cache(
    state: AgentState
) -> dict[str, Any]:
    
    if state.get("memory_dependent", False):

        debug_log(
            "CACHE SKIPPED",
            {
                "reason": (
                    "Answer depends on personal memory."
                ),
                "query": state.get(
                    "user_message"
                ),
            }
       )
        return {}

    if not state.get(
        "cacheable",
        False
    ):
        return {}

    if state.get(
        "cache_hit",
        False
    ):
        return {}

    user_id = state.get(
        "user_id"
    )

    user_message = state.get(
        "user_message"
    )

    response = state.get(
        "response"
    )

    if (
        not user_id
        or not user_message
        or not response
    ):
        return {}

    try:

        result = save_response_to_cache(
            user_id=user_id,
            query=user_message,
            answer=response,
        )

        debug_log(
            "CACHE UPDATED",
            result
        )

        return {}

    except Exception as e:

        debug_log(
            "CACHE UPDATE ERROR",
            str(e)
        )

        return {
            "error": (
                f"Cache update error: {str(e)}"
            )
        }


# ============================================================
# 11. Handle Error
# ============================================================

def handle_error(
    state: AgentState
) -> dict[str, Any]:

    error = state.get(
        "error"
    )

    if error:

        debug_log(
            "GRAPH ERROR",
            error
        )

        return {
            "response": error
        }

    return {}