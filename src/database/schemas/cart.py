from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database.schemas.base import BaseModel

__all__ = ('CartProduct',)


class CartProduct(BaseModel):
    __tablename__ = 'cart_products'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)

    product = relationship('Product', back_populates='cart_product')
    user = relationship('User', back_populates='cart_products')
