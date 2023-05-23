from datetime import datetime
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from typing import NewType

__all__ = (
    'get_now_datetime',
    'TIMEZONE',
    'TZAware',
    'to_local_time',
    'Period',
)

TIMEZONE = ZoneInfo('US/Eastern')
UTC = ZoneInfo('UTC')

TZAware = NewType('TZAware', datetime)


def get_now_datetime() -> TZAware:
    return TZAware(datetime.now(tz=TIMEZONE))


def to_local_time(dt: datetime) -> TZAware:
    return TZAware(dt.replace(tzinfo=UTC).astimezone(TIMEZONE))


@dataclass(frozen=True, slots=True)
class Period:
    start: datetime
    end: datetime
