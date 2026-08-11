from typing import List, Dict, Any


def create_scratchpad() -> List[Dict[str, Any]]:
    """
    Creates an empty scratchpad for the current request.
    """
    return []


def add_step(
    scratchpad: List[Dict[str, Any]],
    tool: str,
    tool_input: Dict[str, Any],
    tool_result: Dict[str, Any]
) -> None:
    """
    Adds one completed tool execution to the scratchpad.
    """

    scratchpad.append(
        {
            "tool": tool,
            "input": tool_input,
            "result": tool_result
        }
    )


def get_scratchpad(
    scratchpad: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Returns the current scratchpad.
    """

    return scratchpad


def clear_scratchpad(
    scratchpad: List[Dict[str, Any]]
) -> None:
    """
    Clears the scratchpad after the request finishes.
    """

    scratchpad.clear()