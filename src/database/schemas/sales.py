from decimal import Decimal

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.schemas.base import BaseModel

__all__ = ('Sale',)


class Sale(BaseModel):
    __tablename__ = 'sale'

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    username: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal]
    quantity: Mapped[int]
    payment_type: Mapped[str] = mapped_column(String(255))

    product_unit = relationship(
        'ProductUnit',
        lazy=False,
        backref='sale',
        cascade='all, delete',
    )
