"""
Central registry for all LangChain tools.

LangGraph will use this collection of tools with ToolNode.
"""

from app.tools.calculator import calculator
from app.tools.weather import weather
from app.tools.web_search import live_web_search
from app.tools.ask_user import ask_user
from app.tools.fetch_from_memory import fetch_from_memory
from app.tools.save_into_memory import save_into_memory


# ============================================================
# All Agent Tools
# ============================================================

TOOLS = [
    calculator,
    weather,
    live_web_search,
    ask_user,
    fetch_from_memory,
    save_into_memory,
]


# ============================================================
# Tool Lookup
# ============================================================

TOOL_MAP = {
    tool.name: tool
    for tool in TOOLS
}