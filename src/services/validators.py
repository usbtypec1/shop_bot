import datetime

from services.time_utils import Period
from support.exceptions import InvalidSupportDateRangeError

__all__ = ('validate_date_range',)


def validate_date_range(date_range: str) -> Period:
    try:
        start, end = date_range.split('-')
        start = datetime.datetime.strptime(start, '%m/%d/%Y')
        end = datetime.datetime.strptime(end, '%m/%d/%Y')
    except ValueError:
        raise InvalidSupportDateRangeError
    return Period(start=start, end=end)
