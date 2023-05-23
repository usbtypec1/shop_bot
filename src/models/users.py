from dataclasses import dataclass

__all__ = ('User',)


@dataclass(frozen=True, slots=True)
class User:
    id: int
    telegram_id: int
    username: str | None
    balance: float
    is_banned: float
