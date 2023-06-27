from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

__all__ = ('TopUpBonus',)


@dataclass(frozen=True, slots=True)
class TopUpBonus:
    id: int
    min_amount_threshold: Decimal
    bonus_percentage: int
    starts_at: datetime
    expires_at: datetime | None
