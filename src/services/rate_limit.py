import datetime
from typing import NoReturn

from services.time_utils import get_now_datetime, to_local_time
from support.exceptions import SupportTicketCreateRateLimitError

__all__ = ('check_support_ticket_create_rate_limit',)


def check_support_ticket_create_rate_limit(
        *,
        last_ticket_created_at: datetime.datetime,
) -> None | NoReturn:
    last_ticket_created_at = to_local_time(last_ticket_created_at)
    passed_time = get_now_datetime() - last_ticket_created_at
    remaining_time_in_seconds = 600 - passed_time.total_seconds()
    if remaining_time_in_seconds > 0:
        raise SupportTicketCreateRateLimitError(
            remaining_time_in_seconds=int(remaining_time_in_seconds),
        )
