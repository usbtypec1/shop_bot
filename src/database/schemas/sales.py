from decimal import Decimal

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.schemas.base import BaseModel, Base
from database.schemas.payment_methods import PaymentMethod

__all__ = ('Sale', 'SoldProduct')


class Sale(BaseModel):
    __tablename__ = 'sales'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    payment_method: Mapped[PaymentMethod]

    products = relationship('SoldProduct', back_populates='sale')


class SoldProduct(Base):
    __tablename__ = 'sold_products'

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(
        ForeignKey('sales.id', ondelete='CASCADE'),
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey('products.id', ondelete='SET NULL'),
    )
    price_at_the_moment: Mapped[Decimal]
    quantity: Mapped[int]

    sale = relationship(
        'Sale',
        back_populates='products',
        cascade='all, delete',
    )

    __table_args__ = (
        CheckConstraint(
            'quantity > 0',
            name='check_quantity_positive'
        ),
        CheckConstraint(
            'price_at_the_moment > 0',
            name='check_price_at_the_moment_positive'
        ),
    )
