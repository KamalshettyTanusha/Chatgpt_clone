from app.config.constants import MAX_TOOL_CALLS


class ToolCallLimiter:
    """
    Limits the number of tool calls
    made during a single request.
    """

    def __init__(self):
        self.call_count = 0


    def can_execute(self):
        """
        Checks whether another tool call is allowed.
        """

        return self.call_count < MAX_TOOL_CALLS


    def register_call(self):
        """
        Increments tool call count.
        """

        self.call_count += 1


    def reset(self):
        """
        Resets count for a new user request.
        """

        self.call_count = 0