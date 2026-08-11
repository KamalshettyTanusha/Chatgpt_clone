import time

from app.config.constants import (
    MAX_REQUESTS_PER_MINUTE
)


class RateLimiter:
    """
    Controls number of requests
    from a user within a time window.
    """

    def __init__(self):

        self.requests = {}


    def is_allowed(
        self,
        user_id: int
    ):
        """
        Checks whether user can make
        another request.
        """

        current_time = time.time()


        if user_id not in self.requests:

            self.requests[user_id] = []


        # Remove requests older than 1 minute

        self.requests[user_id] = [

            request_time

            for request_time in self.requests[user_id]

            if current_time - request_time < 60

        ]


        if len(self.requests[user_id]) >= MAX_REQUESTS_PER_MINUTE:

            return False


        self.requests[user_id].append(
            current_time
        )


        return True



rate_limiter = RateLimiter()