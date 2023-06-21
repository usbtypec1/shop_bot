from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.schemas.base import BaseModel

__all__ = ('CartProduct',)


class CartProduct(BaseModel):
    __tablename__ = 'cart_products'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id', ondelete='CASCADE'),
    )
    quantity: Mapped[int]

    product: Mapped['Product'] = relationship(
        'Product',
        back_populates='cart_products',
    )
    user: Mapped['User'] = relationship(
        'User',
        back_populates='cart_products',
    )

    __table_args__ = (
        CheckConstraint(
            'quantity >= 0',
            name='check_cart_product_quantity_non_negative',
        ),
    )
