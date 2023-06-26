from dataclasses import dataclass
from datetime import datetime

__all__ = ('TimeSensitiveDiscount',)


@dataclass(frozen=True, slots=True)
class TimeSensitiveDiscount:
    id: int
    starts_at: datetime
    expires_at: datetime | None
    code: str
    value: int
