from decimal import Decimal

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.schemas.base import BaseModel

__all__ = ('User',)


class User(BaseModel):
    __tablename__ = 'user'

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(String(32))
    balance: Mapped[Decimal] = mapped_column(default=0)
    is_banned: Mapped[bool] = mapped_column(default=False)
    max_cart_cost: Mapped[Decimal | None]

    cart_products = relationship('CartProduct', back_populates='user')
