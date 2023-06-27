from datetime import datetime
from typing import NewType
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo('US/Eastern')
UTC = ZoneInfo('UTC')
TZAware = NewType('TZAware', datetime)


def get_now_datetime() -> TZAware:
    return TZAware(datetime.now(tz=TIMEZONE))


def to_local_time(dt: datetime) -> TZAware:
    return TZAware(dt.replace(tzinfo=UTC).astimezone(TIMEZONE))
