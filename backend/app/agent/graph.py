"""
LangGraph workflow for the AI Assistant.

The LLM is responsible for deciding which tools are required.
LangGraph is responsible for orchestrating the execution loop.

Flow:

START
  ↓
validation
  ↓
rate limit
  ↓
token limit
  ↓
cache
  ├── HIT  → cached response → history → END
  │
  └── MISS → prepare messages → LLM
                         ↓
                  tool required?
                    /        \
                  yes         no
                   ↓           ↓
                ToolNode    final response
                   ↓
                  LLM
                   ↓
                repeat
"""

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)

from app.agent.state import AgentState

from app.agent.nodes import (
    call_llm,
    check_cache,
    check_rate_limit,
    check_token_limit,
    check_tool_call_limit,
    handle_error,
    prepare_messages,
    prepare_response,
    save_history,
    update_cache,
    validate_request,
)

from app.config.constants import MAX_TOOL_CALLS

from app.tools.tool_router import TOOLS

from app.utils.debug import debug_log

from langgraph.checkpoint.memory import MemorySaver

# ============================================================
# Routing
# ============================================================

def route_after_validation(
    state: AgentState
) -> str:

    if state.get("error"):
        return "error"

    return "rate_limit"


def route_after_rate_limit(
    state: AgentState
) -> str:

    if state.get("error"):
        return "error"

    return "token_limit"


def route_after_token_limit(
    state: AgentState
) -> str:

    if state.get("error"):
        return "error"

    return "cache"


def route_after_cache(
    state: AgentState
) -> str:

    if state.get("error"):
        return "error"

    if state.get("cache_hit"):
        return "cached_response"

    return "prepare_messages"


def route_after_tool_limit(
    state: AgentState
) -> str:

    if state.get("error"):
        return "error"

    if (
        state.get("tool_call_count", 0)
        >= MAX_TOOL_CALLS
    ):
        return "error"

    return "tools"


# ============================================================
# Cached Response
# ============================================================

def return_cached_response(
    state: AgentState
) -> dict:

    cache_result = state.get(
        "cache_result"
    )

    if not cache_result:

        return {
            "response": (
                "Cached response was "
                "not available."
            )
        }

    answer = (
        cache_result.get("answer")
        or ""
    )

    debug_log(
        "CACHED RESPONSE",
        {
            "query": state.get(
                "user_message"
            ),
            "similarity": cache_result.get(
                "similarity"
            ),
            "answer": answer,
        },
    )

    return {
        "response": answer
    }


# ============================================================
# Tool Execution
# ============================================================

def execute_tools_with_debug(
    state: AgentState
) -> dict:

    messages = state.get(
        "messages",
        []
    )

    if not messages:

        return {
            "error": (
                "No messages available "
                "for tool execution."
            )
        }

    latest_ai_message = next(
        (
            message
            for message in reversed(messages)
            if isinstance(
                message,
                AIMessage
            )
        ),
        None,
    )

    tool_calls = (
        latest_ai_message.tool_calls
        if latest_ai_message
        else []
    )

    if not tool_calls:

        return {
            "error": (
                "Tool execution requested "
                "but no tool calls were found."
            )
        }

    # --------------------------------------------------------
    # Debug tool calls selected by the LLM
    # --------------------------------------------------------

    for tool_call in tool_calls:

        debug_log(
            "TOOL CALL",
            {
                "tool": tool_call.get(
                    "name"
                ),
                "input": tool_call.get(
                    "args"
                ),
                "tool_call_id": tool_call.get(
                    "id"
                ),
            },
        )

    # --------------------------------------------------------
    # Execute tools
    #
    # ToolNode automatically handles:
    # - tool lookup
    # - tool execution
    # - InjectedState
    # - ToolMessage creation
    # --------------------------------------------------------

    tool_node = ToolNode(
        TOOLS
    )

    result = tool_node.invoke(
        state
    )

    current_count = state.get(
        "tool_call_count",
        0
    )

    result["tool_call_count"] = (
        current_count
        + len(tool_calls)
    )
    # --------------------------------------------------------
    # Preserve memory dependency
    # --------------------------------------------------------

    memory_dependent = state.get(
        "memory_dependent",
        False
    )

    for tool_call in tool_calls:

        if tool_call.get("name") in {
            "fetch_from_memory",
            "save_into_memory"
        }:

            memory_dependent = True

    result["memory_dependent"] = (
        memory_dependent
)

    # --------------------------------------------------------
    # Debug tool results
    # --------------------------------------------------------

    for message in result.get(
        "messages",
        []
    ):

        if isinstance(
            message,
            ToolMessage
        ):

            debug_log(
                "TOOL RESULT",
                {
                    "tool": message.name,
                    "result": message.content,
                    "tool_call_id": (
                        message.tool_call_id
                    ),
                },
            )

    return result


# ============================================================
# Build Graph
# ============================================================

def build_graph():

    graph = StateGraph(
        AgentState
    )

    # ========================================================
    # Nodes
    # ========================================================

    graph.add_node(
        "validate_request",
        validate_request
    )

    graph.add_node(
        "check_rate_limit",
        check_rate_limit
    )

    graph.add_node(
        "check_token_limit",
        check_token_limit
    )

    graph.add_node(
        "check_cache",
        check_cache
    )

    graph.add_node(
        "cached_response",
        return_cached_response
    )

    graph.add_node(
        "prepare_messages",
        prepare_messages
    )

    graph.add_node(
        "llm",
        call_llm
    )

    graph.add_node(
        "check_tool_limit",
        check_tool_call_limit
    )

    graph.add_node(
        "tools",
        execute_tools_with_debug
    )

    graph.add_node(
        "prepare_response",
        prepare_response
    )

    graph.add_node(
        "save_history",
        save_history
    )

    graph.add_node(
        "update_cache",
        update_cache
    )

    graph.add_node(
        "error",
        handle_error
    )

    # ========================================================
    # START
    # ========================================================

    graph.add_edge(
        START,
        "validate_request"
    )

    # ========================================================
    # Validation
    # ========================================================

    graph.add_conditional_edges(
        "validate_request",
        route_after_validation,
        {
            "rate_limit": "check_rate_limit",
            "error": "error",
        },
    )

    graph.add_conditional_edges(
        "check_rate_limit",
        route_after_rate_limit,
        {
            "token_limit": "check_token_limit",
            "error": "error",
        },
    )

    graph.add_conditional_edges(
        "check_token_limit",
        route_after_token_limit,
        {
            "cache": "check_cache",
            "error": "error",
        },
    )

    # ========================================================
    # Cache
    # ========================================================

    graph.add_conditional_edges(
        "check_cache",
        route_after_cache,
        {
            "cached_response": (
                "cached_response"
            ),
            "prepare_messages": (
                "prepare_messages"
            ),
            "error": "error",
        },
    )

    graph.add_edge(
        "cached_response",
        "save_history"
    )

    # ========================================================
    # Prepare Messages → LLM
    # ========================================================

    graph.add_edge(
        "prepare_messages",
        "llm"
    )

    # ========================================================
    # LLM → Tool or Final Response
    #
    # tools_condition checks the latest AIMessage.
    #
    # If the LLM produced tool_calls:
    #
    #     llm → check_tool_limit → tools
    #
    # Otherwise:
    #
    #     llm → prepare_response
    # ========================================================

    graph.add_conditional_edges(
        "llm",
        tools_condition,
        {
            "tools": "check_tool_limit",
            END: "prepare_response",
        },
    )

    # ========================================================
    # Tool Limit
    # ========================================================

    graph.add_conditional_edges(
        "check_tool_limit",
        route_after_tool_limit,
        {
            "tools": "tools",
            "error": "error",
        },
    )

    # ========================================================
    # Tools → LLM
    #
    # THIS IS THE AGENT LOOP.
    #
    # After receiving a tool result, the LLM gets another
    # chance to decide whether another tool is necessary.
    # ========================================================

    graph.add_edge(
        "tools",
        "llm"
    )

    # ========================================================
    # Final Response → History
    # ========================================================

    graph.add_edge(
        "prepare_response",
        "save_history"
    )

    # ========================================================
    # History → Cache
    # ========================================================

    graph.add_edge(
        "save_history",
        "update_cache"
    )

    # ========================================================
    # Cache → END
    # ========================================================

    graph.add_edge(
        "update_cache",
        END
    )

    # ========================================================
    # Error → END
    # ========================================================

    graph.add_edge(
        "error",
        END
    )
    
    checkpointer = MemorySaver()
    
    return graph.compile(
        checkpointer=checkpointer
    )


agent_graph = build_graph()