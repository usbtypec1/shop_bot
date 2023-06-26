from datetime import datetime

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.schemas.base import Base

__all__ = ('TimeSpecificDiscount',)


class TimeSpecificDiscount(Base):
    __tablename__ = 'time_specific_discounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    starts_at: Mapped[datetime | None]
    ends_at: Mapped[datetime | None]
    code: Mapped[str]
    value: Mapped[int]

    __table_args__ = (
        CheckConstraint(
            '(ends_at IS NULL) OR (starts_at IS NULL) OR (ends_at > starts_at)',
            name='check_time_specific_discount_ends_after_starts'),
    )
