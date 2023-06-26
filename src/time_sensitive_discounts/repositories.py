from datetime import datetime

from sqlalchemy import select

from common.repositories import BaseRepository
from database.schemas import TimeSensitiveDiscount
from time_sensitive_discounts import models as discounts_models

__all__ = ('TimeSensitiveDiscountRepository',)


class TimeSensitiveDiscountRepository(BaseRepository):

    def create(
            self,
            *,
            starts_at: datetime | None,
            expires_at: datetime | None,
            code: str,
            value: int,
    ) -> discounts_models.TimeSensitiveDiscount:
        time_sensitive_discount = TimeSensitiveDiscount(
            starts_at=starts_at,
            expires_at=expires_at,
            code=code,
            value=value,
        )
        with self._session_factory() as session:
            with session.begin():
                session.add(time_sensitive_discount)
                session.flush()
                session.refresh(time_sensitive_discount)
        return discounts_models.TimeSensitiveDiscount(
            id=time_sensitive_discount.id,
            starts_at=time_sensitive_discount.starts_at,
            expires_at=time_sensitive_discount.expires_at,
            code=time_sensitive_discount.code,
            value=time_sensitive_discount.value,
        )

    def get_all(self) -> list[discounts_models.TimeSensitiveDiscount]:
        statement = select(TimeSensitiveDiscount)
        with self._session_factory() as session:
            time_sensitive_discounts = session.scalars(statement).all()
        return [
            discounts_models.TimeSensitiveDiscount(
                id=time_sensitive_discount.id,
                starts_at=time_sensitive_discount.starts_at,
                expires_at=time_sensitive_discount.expires_at,
                code=time_sensitive_discount.code,
                value=time_sensitive_discount.value,
            ) for time_sensitive_discount in time_sensitive_discounts
        ]
