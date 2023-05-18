from datetime import datetime
from zoneinfo import ZoneInfo

__all__ = ('get_now_datetime',)


def get_now_datetime() -> datetime:
    timezone = ZoneInfo('US/Eastern')
    return datetime.now(tz=timezone)
