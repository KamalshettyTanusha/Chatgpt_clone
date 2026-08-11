import math

from langchain_core.tools import tool

from app.config.constants import TOOL_CALCULATOR


@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Use this tool when the user asks for calculations,
    arithmetic, percentages, powers, square roots,
    rounding, minimum, maximum, ceiling, or floor operations.

    Examples:
        25 * 4
        100 / 5
        sqrt(144)
        pow(2, 10)
        round(3.14159, 2)
    """

    if not expression:
        return "Expression is missing."

    allowed_functions = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "pow": pow,
        "sqrt": math.sqrt,
        "ceil": math.ceil,
        "floor": math.floor,
    }

    try:

        result = eval(
            expression,
            {"__builtins__": None},
            allowed_functions,
        )

        return str(result)

    except Exception as e:

        return f"Calculation Error: {str(e)}"

