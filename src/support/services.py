import datetime
from typing import NoReturn

from services.time_utils import Period, to_local_time, get_now_datetime
from support.exceptions import (
    InvalidSupportDateRangeError,
    SupportTicketCreateRateLimitError
)

__all__ = (
    'validate_date_range',
    'check_support_ticket_create_rate_limit',
)


def validate_date_range(date_range: str) -> Period:
    try:
        start, end = date_range.split('-')
        start = datetime.datetime.strptime(start, '%m/%d/%Y')
        end = datetime.datetime.strptime(end, '%m/%d/%Y')
    except ValueError:
        raise InvalidSupportDateRangeError
    return Period(start=start, end=end)


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
