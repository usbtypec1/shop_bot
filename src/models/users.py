from dataclasses import dataclass
from datetime import datetime

__all__ = ('User',)


@dataclass(frozen=True, slots=True)
class User:
    id: int
    telegram_id: int
    username: str | None
    balance: float
    is_banned: bool
    created_at: datetime
