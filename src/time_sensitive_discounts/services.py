from datetime import datetime

from time_sensitive_discounts.exceptions import DatetimeValidationError

__all__ = ('parse_datetime',)


def parse_datetime(datetime_text: str) -> datetime:
    try:
        return datetime.strptime(datetime_text, '%m/%d/%Y %H:%M')
    except ValueError:
        raise DatetimeValidationError
