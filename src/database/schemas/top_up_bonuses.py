from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.schemas.base import Base

__all__ = ('TopUpBonus',)


class TopUpBonus(Base):
    __tablename__ = 'top_up_bonuses'

    id: Mapped[int] = mapped_column(primary_key=True)
    min_amount_threshold: Mapped[Decimal]
    bonus_percentage: Mapped[int]
    starts_at: Mapped[datetime]
    expires_at: Mapped[datetime | None]

    __table_args__ = (
        CheckConstraint(
            '(expires_at IS NULL) OR (expires_at > starts_at)',
            name='check_time_sensitive_discount_expires_after_starts'),
        CheckConstraint(
            'min_amount_threshold >= 0',
            name='check_min_amount_threshold_non_negative',
        )
    )
