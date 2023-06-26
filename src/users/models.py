from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

__all__ = ('User', 'UsersIdentifiers')


@dataclass(frozen=True, slots=True)
class UsersIdentifiers:
    usernames: list[str]
    user_ids: list[int]


@dataclass(frozen=True, slots=True)
class User:
    id: int
    telegram_id: int
    username: str | None
    balance: Decimal
    is_banned: bool
    created_at: datetime
    max_cart_cost: Decimal | None
    permanent_discount: int
