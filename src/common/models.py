import typing
from dataclasses import dataclass
from datetime import datetime


class Buyer(typing.TypedDict):
    telegram_id: int
    username: str | None
    purchase_number: int
    orders_amount: float


@dataclass(frozen=True, slots=True)
class Period:
    start: datetime
    end: datetime
