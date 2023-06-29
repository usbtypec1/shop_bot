class SupportTicketCreateRateLimitError(Exception):

    def __init__(self, *args, remaining_time_in_seconds: int):
        super().__init__(*args)
        self.remaining_time_in_seconds = remaining_time_in_seconds


class InvalidSupportDateRangeError(Exception):
    pass
