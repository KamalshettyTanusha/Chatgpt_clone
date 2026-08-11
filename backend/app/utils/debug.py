"""
Debug logging utilities for the LangGraph agent.
"""

from datetime import datetime


def debug_log(title: str, data=None):
    """
    Print a clearly formatted debugging message.
    """

    timestamp = datetime.now().strftime("%H:%M:%S")

    print("\n" + "=" * 70)
    print(f"[{timestamp}] {title}")
    print("=" * 70)

    if data is not None:
        print(data)

    print("=" * 70 + "\n")
