from datetime import datetime

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.schemas.base import Base

__all__ = ('TimeSensitiveDiscount',)


class TimeSensitiveDiscount(Base):
    __tablename__ = 'time_sensitive_discounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    starts_at: Mapped[datetime]
    expires_at: Mapped[datetime | None]
    code: Mapped[str] = mapped_column(unique=True)
    value: Mapped[int]

    __table_args__ = (
        CheckConstraint(
            '(expires_at IS NULL)'
            ' OR (starts_at IS NULL)'
            ' OR (expires_at > starts_at)',
            name='check_time_sensitive_discount_expires_after_starts'),
    )
